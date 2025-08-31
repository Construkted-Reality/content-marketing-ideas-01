#!/bin/bash

# Script to extract and display voice characteristics from voice_selection.md
# This helps verify the voice characteristics are properly parsed

echo "=== Voice Characteristics Extractor ==="
echo ""

# Read the voice selection file
VOICE_SELECTION_FILE="voice_selection.md"

if [ ! -f "$VOICE_SELECTION_FILE" ]; then
    echo "Error: $VOICE_SELECTION_FILE not found!"
    exit 1
fi

echo "Extracting voice characteristics from $VOICE_SELECTION_FILE..."
echo ""

# Extract each voice section
echo "=== NEW YORKER VOICE ==="
grep -A 15 "^**New Yorker**" "$VOICE_SELECTION_FILE" | head -15
echo ""

echo "=== THE ATLANTIC VOICE ==="
grep -A 15 "^**The Atlantic**" "$VOICE_SELECTION_FILE" | head -15
echo ""

echo "=== WIRED VOICE ==="
grep -A 15 "^**Wired**" "$VOICE_SELECTION_FILE" | head -15
echo ""

echo "=== Voice Selection Guide Summary ==="
echo "This file contains detailed voice characteristics for:"
echo "- New Yorker: sophisticated, witty, inquisitive; conversational yet authoritative"
echo "- The Atlantic: thought-provoking, long-form, measured, policy-aware, argument-driven"
echo "- Wired: tech-forward, skeptical-futurist, fast-paced, jargon-light"
