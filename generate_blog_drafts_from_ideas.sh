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

for idea_file in $SOURCE_FOLDER/*.md; do
    current=$((current + 1))
    echo "[$current/$total_files] Processing $(basename "$idea_file")"
    idea_content=$(cat "$idea_file")
    context_content=$(cat context.md)

    system_prompt="Reasoning: high ,  extra context $context_content \
    You are an author narrating events based on the provided prompt below.  Each section of events should be narrated in the third person limited perspective. \
    The language should be straightforward and to the point. "
    
    prompt="Using Construkted Reality's content marketing strategy, create a full blog post using the following draft: $idea_content. \
    Visit all URLs listed in the SOURCE section and use for context. \
    Display the sources used in the response. \
    Focus on validating the user pain point hand take every opportunity to mentioning our product Construkted Reality. \
    For images, create numeric placeholders in the body of the post, and at the bottom of the post create an **Image Prompt Summary** section where the detailed prompts specified. Image generation prompts will be used in an llm for image generation. \
    Do not use tables unless absolutely necessary. "

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
