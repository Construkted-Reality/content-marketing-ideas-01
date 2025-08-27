#!/bin/bash

# --- Configuration ---
DEFAULT_OLLAMA_HOST="192.168.8.90"
#DEFAULT_MODEL="qwen3:30b-a3b-thinking-2507-fp16"
DEFAULT_MODEL="gpt-oss:120b"

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

    voice_TheNewYorker="New Yorker \
- Tone: sophisticated, witty, introspective, and conversational, yet authoritative. \
- Rhythm: mix short, punchy sentences with longer, meandering ones; allow occasional asides and minor tangents.\
- Style: sprinkle in idioms, slang, and light‑hearted rhetorical questions (e.g., “Who hasn’t…?”) to keep it authentic. \
- Personality: let the narrator’s sharp curiosity and dry humor shine through; don’t be afraid of a subtle imperfection or a fleeting digression. \
- Purpose: inform, entertain, and provoke thought—think of a column that educates while it delights and challenges the reader. "
 
    voice_TheAtlantic="The Atlantic 
- Personality: Thought‑provoking, long‑form, measured, policy‑savvy. \
- Signature tricks: Structured arguments, data‑driven evidence, historical context, calm but persuasive tone, minimal slang. \
- Prompt cheat‑sheet: Write in the voice of an Atlantic columnist: analytical, well‑researched, balanced,with a calm persuasive tone and ample historical context. "

    voice_Wired="Wired \
- Personality: Futurist, tech‑obsessed, fast‑paced, jargon‑light. \
- Signature tricks: Short, punchy sentences; use of bold tech metaphors ('the internet is a nervous system'); occasional emojis or meme references (when appropriate); 'what‑it‑means‑for‑you' framing. \
- Prompt cheat‑sheet: Write like a Wired feature: tech‑forward, fast‑paced, with vivid metaphors and a ‘what it means for the reader’ angle. "

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
    voice="Write in the voice of a seasoned journalist at $voice_TheNewYorker "

    system_prompt="Reasoning: high ,  extra context $context_content. Writing Style should be: $voice3 . $formatting_rules "
    
    prompt="Using Construkted Reality's content marketing strategy, create a full blog post using the following draft: $idea_content. \
    Visit all URLs listed in the SOURCE section and use for context. \
    Display the sources used in the response. \
    Focus on validating the user pain point hand take every opportunity to mentioning our product Construkted Reality. \
    For images, create numeric placeholders in the body of the post, and at the bottom of the post create an **Image Prompt Summary** section where the detailed prompts specified. Image generation prompts will be used in an llm for image generation. \
    Do not use tables in your response. "

    # Prepare the JSON payload
    JSON_PAYLOAD=$(jq -n \
        --arg model "$DEFAULT_MODEL" \
        --arg prompt "$prompt" \
        --arg system "$system_prompt" \
        '{model: $model, prompt: $prompt, system: $system, stream: false}')

    # Send the request
    OLLAMA_URL="http://${DEFAULT_OLLAMA_HOST}:11434/api/generate"
    response=$(curl -s -X POST "$OLLAMA_URL" -d "$JSON_PAYLOAD" | jq -r '.response')
    
    # Save the response
    echo "$response" > "$DESTINATION_FOLDER/$(basename "$idea_file")"
    #echo $JSON_PAYLOAD
    #echo "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ \n"
    #echo "$response"

done
