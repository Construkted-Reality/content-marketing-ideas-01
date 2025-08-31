#!/bin/bash

# --- Configuration ---
DEFAULT_OLLAMA_HOST="192.168.8.90"
#DEFAULT_MODEL="qwen3:30b-a3b-thinking-2507-fp16"
#DEFAULT_MODEL="gpt-oss:120b"
DEFAULT_MODEL="gpt-oss-120b-CTX28k"

# Test mode - set to "on" to output to screen instead of file
TEST_MODE="off"

SOURCE_FOLDER="blog_post_ideas"
DESTINATION_FOLDER="blog_post_drafts"

# --- Check for required tools ---
if ! command -v curl &> /dev/null; then
    echo "Error: curl is not installed. Please install it to continue."
    exit 1
fi
if ! command -v jq &> /dev/null; then
    echo "Error: jq is not installed. Please install it to continue."
    exit 1
fi

mkdir -p blog_post_full
total_files=$(find $SOURCE_FOLDER -maxdepth 1 -type f -name "*.md" | wc -l)
current=0

# Load reference data from external files
voice_selection=$(cat voice_selection.md)
context_content=$(cat context.md)
#writing_guidance=$(cat writing_guidance.md)
titles=$(cat crafting_compelling_titles.md)

for idea_file in $SOURCE_FOLDER/*.md; do
    current=$((current + 1))
    echo "[$current/$total_files] Processing $(basename "$idea_file")"
    idea_content=$(cat "$idea_file")


    # First OLLAMA call: Establish voice + metadata
    echo "  -> Establishing voice and metadata..."
    
    voice_system_prompt="Reasoning: high \
    You are a content strategy expert for Construkted Reality. \
    Extra context: $context_content
    Your task is to analyze blog post ideas and return ONLY structured data about:
    - Voice (choose from the voices listed $voice_selection )
    - Voice Characteristics taken from the information provided (detailed description of tone, rhythm, style, personality, purpose for the selected voice)
    - Piece Type (explainer, tutorial, methods deep dive, case study, product update, standards/policy analysis, news reaction)
    - Primary Goal (educate, persuade, announce, compare, troubleshoot)
    - Target Audience (enterprise, public sector, academic, hobbyist)
    - Technical Depth (low/med/high)

    Return EXACTLY in this format with no extra text:
    Voice: [value]
    Voice Characteristics: [detailed characteristics of the voice]
    Piece Type: [value]
    Primary Goal: [value]
    Target Audience: [value]
    Technical Depth: [value]"

    voice_prompt="Analyze the following blog post idea and return ONLY structured data as specified above:

    Idea content: $idea_content. Visit all URLs listed in the SOURCE section read their content carefully and use the content at the URLs to extract the pain points, and use the content to guide the writing of the blog post content. "

    # Prepare the JSON payload for voice determination
    VOICE_JSON_PAYLOAD=$(jq -n \
        --arg model "$DEFAULT_MODEL" \
        --arg prompt "$voice_prompt" \
        --arg system "$voice_system_prompt" \
        '{model: $model, prompt: $prompt, system: $system, stream: false}')

    # Send the first request to establish voice
    OLLAMA_URL="http://${DEFAULT_OLLAMA_HOST}:11434/api/generate"
    
    # Get the voice response
    voice_response=$(curl -s -X POST "$OLLAMA_URL" -d "$VOICE_JSON_PAYLOAD" | jq -r '.response')
    
    # Parse the structured response to extract voice and other metadata
    voice=$(echo "$voice_response" | grep -E "^Voice:" | cut -d' ' -f2-)
    voice_characteristics=$(echo "$voice_response" | grep -E "^Voice Characteristics:" | cut -d' ' -f3-)
    piece_type=$(echo "$voice_response" | grep -E "^Piece Type:" | cut -d' ' -f3-)
    primary_goal=$(echo "$voice_response" | grep -E "^Primary Goal:" | cut -d' ' -f3-)
    target_audience=$(echo "$voice_response" | grep -E "^Target Audience:" | cut -d' ' -f3-)
    technical_depth=$(echo "$voice_response" | grep -E "^Technical Depth:" | cut -d' ' -f3-)
    
    echo "  -> Voice determined: $voice"
    echo "  -> Voice Characteristics: $voice_characteristics"
    echo "  -> Piece Type: $piece_type"
    echo "  -> Primary Goal: $primary_goal"
    echo "  -> Target Audience: $target_audience"
    echo "  -> Technical Depth: $technical_depth"
    
    # Second OLLAMA call: Generate full draft using established voice
    echo "  -> Generating full draft..."
    
    # Create the system prompt with the established voice
    final_system_prompt="Reasoning: high, extra context $context_content. \
    Writing Style should be: Write in the voice of a seasoned journalist from the $voice using the appropriate characteristics $voice_selection in crafting the article. \
    The type of piece you are writing is $piece_type. \
    The primary goal of the article is $primary_goal. \
    The target audience for the article is $target_audience. \
    The technical depth for the article should be $technical_depth. \

    **Do not use tables in your response. ** "

    final_prompt="Using Construkted Reality's content marketing strategy, create a full blog post using the following draft: $idea_content. \
    Visit all URLs listed in the SOURCE section read their content carefully and use the content at the URLs to extract the pain points, and use the content to guide the writing of the blog post content. \
    Display the sources used in the response. \
    Focus on validating the user pain point hand take every opportunity to mentioning our product Construkted Reality. \
    For images, create numeric placeholders in the body of the post, and at the bottom of the post create an **Image Prompt Summary** section where the detailed prompts specified. Image generation prompts will be used in an llm for image generation. \
    
    Change the article title by using all the context available, and use the title crafting guidance as follows: $titles. "

    # Prepare the JSON payload for final draft
    FINAL_JSON_PAYLOAD=$(jq -n \
        --arg model "$DEFAULT_MODEL" \
        --arg prompt "$final_prompt" \
        --arg system "$final_system_prompt" \
        '{model: $model, prompt: $prompt, system: $system, stream: false}')

    # Send the second request to generate full draft
    final_response=$(curl -s -X POST "$OLLAMA_URL" -d "$FINAL_JSON_PAYLOAD" | jq -r '.response')
    
    # Save the response
    if [ "$TEST_MODE" = "on" ]; then
        echo $FINAL_JSON_PAYLOAD
        echo "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ \n"
        #echo "=== OUTPUT FOR $(basename "$idea_file") ==="
        #echo "$response"
    else
        output_filename="${DESTINATION_FOLDER}/$(basename "$idea_file" .md)"
        echo "$final_response" > "$output_filename"
        echo "  -> Saved draft to $output_filename"
    fi
done

echo "All blog drafts processed successfully!"
