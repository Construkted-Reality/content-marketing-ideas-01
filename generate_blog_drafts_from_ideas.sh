#!/bin/bash

# --- Configuration ---
DEFAULT_OLLAMA_HOST="192.168.8.90"
#DEFAULT_MODEL="qwen3:30b-a3b-thinking-2507-fp16"
#DEFAULT_MODEL="gpt-oss:120b"
DEFAULT_MODEL="gpt-oss-120b-CTX28k"

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

declare -A voice_definitions=(
    ["TheNewYorker"]="New Yorker \
- Tone: sophisticated, witty, introspective, and conversational, yet authoritative. \
- Rhythm: mix short, punchy sentences with longer, meandering ones; allow occasional asides and minor tangents.\
- Style: sprinkle in idioms, slang, and light‑hearted rhetorical questions (e.g., “Who hasn’t…?”) to keep it authentic. \
- Personality: let the narrator’s sharp curiosity and dry humor shine through; don’t be afraid of a subtle imperfection or a fleeting digression. \
- Purpose: inform, entertain, and provoke thought—think of a column that educates while it delights and challenges the reader. "
    ["TheAtlantic"]="The Atlantic \
- Personality: Thought‑provoking, long‑form, measured, policy‑savvy. \
- Signature tricks: Structured arguments, data‑driven evidence, historical context, calm but persuasive tone, minimal slang. \
- Prompt cheat‑sheet: Write in the voice of an Atlantic columnist: analytical, well‑researched, balanced, with a calm persuasive tone and ample historical context. "
    ["Wired"]="Wired \
- Personality: Futurist, tech‑obsessed, fast‑paced, jargon‑light. \
- Signature tricks: Short, punchy sentences; use of bold tech metaphors ('the internet is a nervous system'); occasional emojis or meme references (when appropriate); 'what‑it‑means‑for‑you' framing. \
- Prompt cheat‑sheet: Write like a Wired feature: tech‑forward, fast‑paced, with vivid metaphors and a ‘what it means for the reader’ angle. "
)

    formatting_rules="**Formatting rules** \
- Do **not** use any tables, ASCII‑art tables, or Markdown tables. \
- Keep the output strictly in paragraph form (or simple bullet points if a list is needed). \
- Avoid other “grid‑like” structures; use prose instead. \
Deliver a piece that fulfills the voice and purpose while respecting the formatting rules." 

for idea_file in $SOURCE_FOLDER/*.md; do
    current=$((current + 1))
    echo "[$current/$total_files] Processing $(basename "$idea_file")"
    idea_content=$(cat "$idea_file")
    context_content=$(cat context.md)
    #writing_guidance=$(cat writing_guidance.md)
    titles=$(cat crafting_compelling_titles.md)

    # First API call: Select parameters
    first_prompt="Analyze the following topic research and select the most appropriate writing parameters.
    
Use ONLY this JSON format for output (no other text):
{
  \"voice\": \"Your chosen voice option (e.g., TheNewYorker)\",
  \"piece_type\": \"Your chosen piece type (e.g., explainer)\",
  \"primary_goal\": \"Your chosen primary goal (e.g., educate)\",
  \"target_audience\": \"Your chosen target audience (e.g., enterprise)\",
  \"technical_depth\": \"Your chosen technical depth (e.g., med)\",
  \"justification\": \"Explanation of why these choices were made\",
  \"pain_point\": \"Summary of the main pain point users are experiencing\"
}

Writing style descriptions:
New Yorker: ${voice_definitions[TheNewYorker]}
The Atlantic: ${voice_definitions[TheAtlantic]}
Wired: ${voice_definitions[Wired]}

Topic research content:
$idea_content
Visit all URLs listed in the SOURCE section, read their content carefully and use the content at the URLs to extract the pain points, and use the content to guide the research.

Instructions:
1. Analyze the topic and determine which of the three **voices** best fits
2. Select appropriate **piece type** from: explainer, tutorial, methods deep dive, case study, product update, standards/policy analysis, news reaction
3. Select **primary goal** from: educate, persuade, announce, compare, troubleshoot
4. Select **target audience** from: enterprise, public sector, academic, hobbyist
5. Select **technical depth** from: low, med, high
6. Provide a **justification** explaining why these specific choices were made
7. Extract and summarize the main pain point that users are experiencing from the research content and URLs. Be very descriptive of the exact problems and pains, with specific examples gathered from the research. \
It is very important to have as much detail as possible so as to be able to address a solution specifically to the pain points you find, and not a generic solution.

Output ONLY the JSON object above with your selections."

    # Prepare the JSON payload for first API call
    JSON_PAYLOAD_FIRST=$(jq -n \
        --arg model "$DEFAULT_MODEL" \
        --arg prompt "$first_prompt" \
        '{model: $model, prompt: $prompt, stream: false}')

    # Send the first request to select parameters
    OLLAMA_URL="http://${DEFAULT_OLLAMA_HOST}:11434/api/generate"
    params_response=$(curl -s -X POST "$OLLAMA_URL" -d "$JSON_PAYLOAD_FIRST" | jq -r '.response')

    # Parse the JSON response
    selected_voice=$(echo "$params_response" | jq -r .voice)
    piece_type=$(echo "$params_response" | jq -r .piece_type)
    primary_goal=$(echo "$params_response" | jq -r .primary_goal)
    target_audience=$(echo "$params_response" | jq -r .target_audience)
    technical_depth=$(echo "$params_response" | jq -r .technical_depth)
    justification=$(echo "$params_response" | jq -r .justification)
    pain_point=$(echo "$params_response" | jq -r .pain_point)

    # Validate that we got valid selections
    if [ "$selected_voice" = "null" ] || [ "$selected_voice" = "" ]; then
        echo "Error: Failed to select voice from AI response"
        continue
    fi

    # Echo the selected parameters for visibility
    echo "Selected parameters for $(basename "$idea_file"):"
    echo "  Voice: $selected_voice"
    echo "  Piece Type: $piece_type"
    echo "  Primary Goal: $primary_goal"
    echo "  Target Audience: $target_audience"
    echo "  Technical Depth: $technical_depth"
    echo "  Justification: $justification"
    echo "  Pain Point: $pain_point"

    # Second API call: Generate blog post with selected parameters
    voice_content=${voice_definitions[$selected_voice]}
    voice_prompt="Write in the voice of a seasoned journalist at $voice_content"

    system_prompt="Reasoning: high, extra context $context_content. \
    Writing Style should be: $voice_prompt. \
    Piece Type: $piece_type. \
    Primary Goal: $primary_goal. \
    Target Audience: $target_audience. \
    Technical Depth: $technical_depth. \
    Follow the following formatting rules: $formatting_rules. "

    prompt="Using Construkted Reality's content marketing strategy, create a full blog post using the following draft: $idea_content. \
    Visit all URLs listed in the SOURCE section read their content carefully and use the content at the URLs to extract the pain points, and use the content to guide the writing of the blog post content. \
    Extract the main pain point that users are experiencing from the research content and URLs. Be very descriptive of the exact problems and pains, with specific examples gathered from the research. \
    It is very important to have as much detail as possible so as to be able to address a solution specifically when writing the article, to the pain points you find, and not writing about a generic solution to a generic problem.

    Display the sources used in the response. \
    This article should focus on validating and suggesting solutions to the user pain points that are extracted from the URLs. \
    Mention our product Construkted Reality whenever appropriate, and how it could potentially provide a solution. \
    For images, create numeric placeholders in the body of the post, and at the bottom of the post create an **Image Prompt Summary** section where the detailed prompts specified. Image generation prompts will be used in an llm for image generation. \
    Do not use tables in your response. \

    Change the article title by using all the context available, and use the title crafting guidance as follows: $titles. \
    "

    # Prepare the JSON payload for second API call
    JSON_PAYLOAD_SECOND=$(jq -n \
        --arg model "$DEFAULT_MODEL" \
        --arg prompt "$prompt" \
        --arg system "$system_prompt" \
        '{model: $model, prompt: $prompt, system: $system, stream: false}')

    # Send the second request to generate blog post
    response=$(curl -s -X POST "$OLLAMA_URL" -d "$JSON_PAYLOAD_SECOND" | jq -r '.response')
    
    # Append metadata to the response
    metadata="

---
### Content Creation Metadata
- **Voice**: $selected_voice
- **Piece Type**: $piece_type
- **Primary Goal**: $primary_goal
- **Target Audience**: $target_audience
- **Technical Depth**: $technical_depth
- **Justification**: $justification
- **Pain Point**: $pain_point
---"
    
    # Save the response with metadata
    output_filename="${DESTINATION_FOLDER}/$(basename "$idea_file" .md).md"
    
    # Check if file already exists and append -xx suffix if needed
    base_name=$(basename "$idea_file" .md)
    counter=1
    
    # Find the highest existing counter for this base name
    # Look for files matching pattern like "base-01.md", "base-02.md", etc.
    if [ -d "$DESTINATION_FOLDER" ]; then
        # Get all existing files with same base name and extract their counters
        max_counter=0
        for file in "$DESTINATION_FOLDER"/"${base_name}"-*.md; do
            if [ -f "$file" ]; then
                # Extract the counter part from filename like "base-03.md" -> 03
                counter_part=$(basename "$file" .md | sed -n "s/.*-\([0-9][0-9]\)\.md$/\1/p")
                if [ -n "$counter_part" ] && [ "$counter_part" -gt "$max_counter" ] 2>/dev/null; then
                    max_counter=$counter_part
                fi
            fi
        done
        # Start counter from the next available number
        counter=$((max_counter + 1))
    fi
    
    # Generate filename with appropriate suffix
    original_filename="$output_filename"
    while [ -f "$output_filename" ]; do
        # Format counter as two digits (01, 02, 03, ...)
        formatted_counter=$(printf "%02d" $counter)
        output_filename="${DESTINATION_FOLDER}/${base_name}-${formatted_counter}.md"
        counter=$((counter + 1))
    done
    
    echo -e "$response$metadata" > "$output_filename"
done

    #echo "$response"

#done
