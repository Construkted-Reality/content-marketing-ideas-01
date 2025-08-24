#!/bin/bash

# --- Configuration ---
DEFAULT_OLLAMA_HOST="192.168.8.90"
DEFAULT_MODEL="qwen3:30b-a3b-thinking-2507-fp16"
#DEFAULT_MODEL="gpt-oss:120b"

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
total_files=$(find blog_post_ideas -maxdepth 1 -type f -name "*.md" | wc -l)
current=0

for idea_file in blog_post_drafts/*.md; do
    current=$((current + 1))
    echo "[$current/$total_files] Processing $(basename "$idea_file")"
    idea_content=$(cat "$idea_file")
    context_content=$(cat context.md)
    prompt="Using Construkted Reality's content strategy (from context.md), create a full blog post using the following draft: $idea_content. Focus on validating the user pain point whand take every opportunity to mentioning our product Construkted Reality. Suggest prompts for image generation for images throughout the post. Context content for what Construkted Reality does: $context_content. Minimal use of tables. "

    # Prepare the JSON payload
    JSON_PAYLOAD=$(jq -n \
        --arg model "$DEFAULT_MODEL" \
        --arg prompt "$prompt" \
        '{model: $model, prompt: $prompt, stream: false, options: {reasoning_effort: "high"}}')

    # Send the request
    OLLAMA_URL="http://${DEFAULT_OLLAMA_HOST}:11434/api/generate"
    response=$(curl -s -X POST "$OLLAMA_URL" -d "$JSON_PAYLOAD" | jq -r '.response')
    
    # Save the response
    echo "$response" > "blog_post_full/$(basename "$idea_file")"
done
