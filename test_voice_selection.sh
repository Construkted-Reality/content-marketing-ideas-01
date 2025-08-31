#!/bin/bash

# Test script to verify voice selection with characteristics works correctly

echo "=== Testing Voice Selection with Characteristics ==="
echo ""

# Test the modified script with a simple echo to see if it parses correctly
echo "Testing that the script can parse voice characteristics..."

# Create a sample response that mimics what OLLAMA would return
SAMPLE_RESPONSE="Voice: The Atlantic
Voice Characteristics: Personality: thought-provoking, long-form, measured, policy-aware, argument-driven. Signature traits: clear thesis early (nut graf); structured arguments; synthesis of research and expert voices; historical context; anticipates counterarguments; calm, persuasive tone; minimal slang; data as context rather than the star; plain, precise prose.
Piece Type: explainer
Primary Goal: educate
Target Audience: enterprise
Technical Depth: high"

echo "Sample response parsing test:"
echo "Response: $SAMPLE_RESPONSE"
echo ""

# Test parsing
VOICE=$(echo "$SAMPLE_RESPONSE" | grep -E "^Voice:" | cut -d' ' -f2-)
CHARACTERISTICS=$(echo "$SAMPLE_RESPONSE" | grep -E "^Voice Characteristics:" | cut -d' ' -f3-)

echo "Parsed Voice: $VOICE"
echo "Parsed Characteristics (first 100 chars): ${CHARACTERISTICS:0:100}..."
echo ""

echo "=== Test Complete ==="
