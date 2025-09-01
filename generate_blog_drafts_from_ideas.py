#!/usr/bin/env python3
"""
Python translation of `generate_blog_drafts_from_ideas.sh`.

This script:
1. Reads markdown idea files from `blog_post_ideas/`.
2. Calls an OLLAMA API twice per idea:
   - First to select writing parameters (voice, piece type, etc.).
   - Second to generate the full blog draft using the selected parameters.
3. Saves the generated draft (with metadata) into `blog_post_drafts/`,
   handling naming collisions by appending a two‑digit suffix (e.g., `-01.md`).
"""

import os
import sys
import json
import pathlib
import re
from typing import Dict, Any

try:
    import requests
except ImportError:
    sys.stderr.write("Error: The Python `requests` library is required. Install it with `pip install requests`.\n")
    sys.exit(1)

# --- Configuration -----------------------------------------------------------
DEFAULT_OLLAMA_HOST = "192.168.8.90"
DEFAULT_MODEL = "gpt-oss-120b-CTX28k"

SOURCE_FOLDER = pathlib.Path("blog_post_ideas")
DESTINATION_FOLDER = pathlib.Path("blog_post_drafts")
CONTEXT_FILE = pathlib.Path("context.md")
TITLES_FILE = pathlib.Path("crafting_compelling_titles.md")
COMPANY_OPERATION_FILE = pathlib.Path("company_operation.md")

# Voice definitions (mirroring the associative array in the Bash script)
VOICE_DEFINITIONS: Dict[str, str] = {
    "TheNewYorker": (
        "New Yorker "
        "- Tone: sophisticated, witty, introspective, and conversational, yet authoritative. "
        "- Rhythm: mix short, punchy sentences with longer, meandering ones; allow occasional asides and minor tangents. "
        "- Style: sprinkle in idioms, slang, and light‑hearted rhetorical questions (e.g., “Who hasn’t…?”) to keep it authentic. "
        "- Personality: let the narrator’s sharp curiosity and dry humor shine through; don’t be afraid of a subtle imperfection or a fleeting digression. "
        "- Purpose: inform, entertain, and provoke thought—think of a column that educates while it delights and challenges the reader."
    ),
    "TheAtlantic": (
        "The Atlantic "
        "- Personality: Thought‑provoking, long‑form, measured, policy‑savvy. "
        "- Signature tricks: Structured arguments, data‑driven evidence, historical context, calm but persuasive tone, minimal slang. "
        "- Prompt cheat‑sheet: Write in the voice of an Atlantic columnist: analytical, well‑researched, balanced, with a calm persuasive tone and ample historical context."
    ),
    "Wired": (
        "Wired "
        "- Personality: Futurist, tech‑obsessed, fast‑paced, jargon‑light. "
        "- Signature tricks: Short, punchy sentences; use of bold tech metaphors ('the internet is a nervous system'); occasional emojis or meme references (when appropriate); 'what‑it‑means‑for‑you' framing. "
        "- Prompt cheat‑sheet: Write like a Wired feature: tech‑forward, fast‑paced, with vivid metaphors and a ‘what it means for the reader’ angle."
    ),
}

FORMATTING_RULES = (
    "**Formatting rules** "
    "- Do **not** use any tables, ASCII‑art tables, or Markdown tables. "
    "- Keep the output strictly in paragraph form (or simple bullet points if a list is needed). "
    "- Avoid other “grid‑like” structures; use prose instead. "
    "- Deliver a piece that fulfills the voice and purpose while respecting the formatting rules."
)

# --- Helper functions ---------------------------------------------------------

def read_file(path: pathlib.Path) -> str:
    """Read a file and return its content as a string."""
    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        sys.stderr.write(f"Error reading {path}: {e}\n")
        sys.exit(1)


def post_ollama(payload: Dict[str, Any]) -> Dict[str, Any]:
    """POST JSON payload to the OLLAMA generate endpoint and return parsed JSON."""
    url = f"http://{DEFAULT_OLLAMA_HOST}:11434/api/generate"
    try:
        response = requests.post(url, json=payload, timeout=300)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        sys.stderr.write(f"Error contacting OLLAMA at {url}: {e}\n")
        sys.exit(1)


def select_parameters(idea_content: str, context_content: str) -> Dict[str, str]:
    """First API call – ask the model to choose voice, piece type, etc."""
    first_prompt = f"""Analyze the following topic research and select the most appropriate writing parameters for content marketing.

Use ONLY this JSON format for output (no other text):
{{
  "voice": "Your chosen voice option (e.g., TheNewYorker)",
  "piece_type": "Your chosen piece type (e.g., explainer)",
  "primary_goal": "Your chosen primary goal (e.g., educate)",
  "target_audience": "Your chosen target audience (e.g., enterprise)",
  "technical_depth": "Your chosen technical depth (e.g., med)",
  "justification": "Explanation of why these choices were made",
  "pain_point": "Summary of the main pain point users are experiencing"
}}

Content Marketing Context:
- This content is part of a content marketing strategy
- Consider the marketing funnel position: Top of Funnel (TOFU), Middle of Funnel (MOFU), or Bottom of Funnel (BOFU)
- TOFU: Awareness & Education - attract broad audience, answer general questions, rank for high-volume keywords
- MOFU: Consideration & Comparison - nurture leads evaluating solutions
- BOFU: Decision & Conversion - convert leads into customers
- Content Marketing Best Practices:
  - Focus on user pain points and benefits rather than product features
  - Include clear calls-to-action where appropriate
  - Optimize for search engines with relevant keywords
  - Maintain consistent brand voice throughout
  - Provide actionable insights that readers can apply immediately

Writing style descriptions:
New Yorker: {VOICE_DEFINITIONS["TheNewYorker"]}
The Atlantic: {VOICE_DEFINITIONS["TheAtlantic"]}
Wired: {VOICE_DEFINITIONS["Wired"]}

Topic research content:
{idea_content}
Visit all URLs listed in the SOURCE section, read their content carefully and use the content at the URLs to extract the pain points, and use the content to guide the research.

Instructions:
1. Analyze the topic and determine which of the three **voices** best fits
2. Select appropriate **piece type** from: explainer, tutorial, methods deep dive, case study, product update, standards/policy analysis, news reaction
3. Select **primary goal** from: educate, persuade, announce, compare, troubleshoot
4. Select **target audience** from: enterprise, public sector, academic, hobbyist
5. Select **technical depth** from: low, med, high
6. Consider the marketing funnel position (TOFU/MOFU/BOFU) when making your selections - how does this content position itself in the customer journey?
7. Provide a **justification** explaining why these specific choices were made, including how they align with the content marketing strategy and funnel position
8. Extract and summarize the main pain point that users are experiencing from the research content and URLs. Be very descriptive of the exact problems and pains, with specific examples gathered from the research. 
It is very important to have as much detail as possible so as to be able to address a solution specifically to the pain points you find, and not a generic solution.

Output ONLY the JSON object above with your selections."""
    payload = {
        "model": DEFAULT_MODEL,
        "prompt": first_prompt,
        "stream": False,
    }
    result = post_ollama(payload)
    response_text = result.get("response", "").strip()

    # Try direct parsing first
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        # Fallback: extract the longest {...} block using regex
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if not match:
            sys.stderr.write("Failed to locate JSON object in OLLAMA response.\n")
            sys.exit(1)
        json_candidate = match.group(0)
        try:
            return json.loads(json_candidate)
        except json.JSONDecodeError as exc:
            sys.stderr.write(f"JSON parsing error after regex extraction: {exc}\\n")
            sys.exit(1)


def generate_blog_post(
    idea_content: str,
    context_content: str,
    titles_content: str,
    company_operation_content: str,
    selected: Dict[str, str],
) -> str:
    """Second API call – generate the full blog post using the chosen parameters."""
    voice_key = selected["voice"]
    voice_content = VOICE_DEFINITIONS.get(voice_key, "")
    voice_prompt = f"Write in the voice of a seasoned journalist at {voice_content}"

    system_prompt = (
        f"You are a content creator for Construkted Reality, tasked with writing a blog post. "
        f"Your writing style is that of a seasoned journalist at {voice_content}. "
        f"Reasoning: high, extra context {context_content}. "
        f"Company operation details: {company_operation_content}. "
        f"Piece Type: {selected['piece_type']}. "
        f"Primary Goal: {selected['primary_goal']}. "
        f"Target Audience: {selected['target_audience']}. "
        f"Technical Depth: {selected['technical_depth']}. "
        f"\n\n**Core Instructions**:\n"
        f"- Mention our product, Construkted Reality, where it naturally fits as a solution to the problems discussed. Do not force it.\n"
        f"- Do not fabricate information about how Construkted Reality works or its features.\n"
        f"- For images, create numeric placeholders in the body of the post (e.g., [IMAGE 1], [IMAGE 2]). At the end of the article, create an 'Image Prompt Summary' section with detailed prompts for an image generation LLM for each placeholder.\n"
        f"- Display all sources used in the response under a 'Sources' section.\n"
        f"- Follow these formatting rules: {FORMATTING_RULES}"
    )

    prompt = (
        f"Using the provided research, write a full blog post. \n"
        f"The primary goal is to validate and suggest solutions to the user pain points identified in the research.\n"
        f"The secondary goal is to position Construkted Reality as the solution to the user pain point.\n"
        f"**Article Research and Draft Content**:\n{idea_content}\n\n"
        f"**Instructions**:\n"
        f"1. Visit all URLs listed in the SOURCE section of the research. Use their content to deepen your understanding of the pain points.\n"
        f"2. Craft a new, compelling title for the article using the following guidance: {titles_content}\n"
        f"3. Write the full blog post, addressing the extracted pain points and integrating solutions."
    )


    payload = {
        "model": DEFAULT_MODEL,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
    }
    result = post_ollama(payload)
    return result.get("response", "")


def make_output_path(base_name: str) -> pathlib.Path:
    """Determine a non‑colliding output path inside DESTINATION_FOLDER."""
    dest = DESTINATION_FOLDER / f"{base_name}.md"
    if not dest.parent.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)

    if not dest.exists():
        return dest

    # Find highest existing numeric suffix
    pattern = re.compile(rf"^{re.escape(base_name)}-(\d{{2}})\.md$")
    max_counter = 0
    for p in dest.parent.iterdir():
        m = pattern.match(p.name)
        if m:
            try:
                num = int(m.group(1))
                if num > max_counter:
                    max_counter = num
            except ValueError:
                pass

    counter = max_counter + 1
    while True:
        suffix = f"{counter:02d}"
        candidate = dest.parent / f"{base_name}-{suffix}.md"
        if not candidate.exists():
            return candidate
        counter += 1


def main() -> None:
    if not SOURCE_FOLDER.is_dir():
        sys.stderr.write(f"Source folder '{SOURCE_FOLDER}' does not exist.\n")
        sys.exit(1)

    total_files = len(list(SOURCE_FOLDER.glob("*.md")))
    if total_files == 0:
        sys.stderr.write("No markdown files found in the source folder.\n")
        sys.exit(0)

    # Load static auxiliary files once
    context_content = read_file(CONTEXT_FILE)
    titles_content = read_file(TITLES_FILE)
    company_operation_content = read_file(COMPANY_OPERATION_FILE)


    for idx, idea_path in enumerate(sorted(SOURCE_FOLDER.glob("*.md")), start=1):
        print(f"[{idx}/{total_files}] Processing {idea_path.name}")
        idea_content = read_file(idea_path)

        # --- First API call -------------------------------------------------
        selected = select_parameters(idea_content, context_content)

        # Verify we got a voice; otherwise skip
        if not selected.get("voice"):
            print(f"  Warning: Voice selection failed for {idea_path.name}; skipping.")
            continue

        # Echo selected parameters (mirrors Bash script output)
        print("  Selected parameters:")
        #for key in ["voice", "piece_type", "primary_goal", "target_audience", "technical_depth", "justification", "pain_point"]:        
        for key in ["voice", "piece_type", "primary_goal", "target_audience", "technical_depth"]:
            print(f"    {key.replace('_', ' ').title()}: {selected.get(key, '')}")

        # --- Second API call -----------------------------------------------
        response = generate_blog_post(
            idea_content,
            context_content,
            titles_content,
            company_operation_content,
            selected,
        )

        # Append metadata
        metadata = f""" 
---
### Content Creation Metadata
- **Voice**: {selected['voice']}
- **Piece Type**: {selected['piece_type']}
- **Primary Goal**: {selected['primary_goal']}
- **Target Audience**: {selected['target_audience']}
- **Technical Depth**: {selected['technical_depth']}
- **Justification**: {selected['justification']}
- **Pain Point**: {selected['pain_point']}
- **Company Operation Context**: {company_operation_content[:200]}...
---
"""
        full_content = response + metadata

        # Determine output file name
        base_name = idea_path.stem
        output_path = make_output_path(base_name)

        # Write out
        output_path.write_text(full_content, encoding="utf-8")
        print(f"  Saved draft to {output_path}\n")


if __name__ == "__main__":
    main()
