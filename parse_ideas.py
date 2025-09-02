#!/usr/bin/env python3
"""
parse_ideas.py

A utility script to parse markdown or plain‑text files containing blog‑post ideas,
associate footnote URLs with their respective ideas, and output the data in a
structured format (JSON or SQLite).

Usage:
    python parse_ideas.py --input <path> [--output <path>] [--format json|sqlite] [--track]

Options:
    --input   Path to the source .md or .txt file (required).
    --output  Destination file. If omitted, defaults to:
                - ideas.json for JSON output
                - ideas.db   for SQLite output
    --format  Output format: "json" (default) or "sqlite".
    --track   Include optional metadata columns (article, voice, piece_type, etc.)
              with empty defaults, enabling later scripts to fill them in.
"""

import argparse
import json
import os
import re
import sqlite3
import sys
from dataclasses import asdict, dataclass, field
from typing import List, Dict, Optional


@dataclass
class Idea:
    title: str
    pain_point: str
    target_audience: str
    content_details: str
    sources: List[str] = field(default_factory=list)
    # Optional metadata fields (empty by default)
    article: Optional[str] = None
    voice: Optional[str] = None
    piece_type: Optional[str] = None
    marketing_post_type: Optional[str] = None
    primary_goal: Optional[str] = None
    target_audience_meta: Optional[str] = None
    technical_depth: Optional[str] = None
    keywords: Optional[str] = None
    length: Optional[str] = None
    sections: Optional[str] = None
    call_to_action: Optional[str] = None
    pain_point_meta: Optional[str] = None


def load_footnotes(text: str) -> Dict[str, str]:
    """
    Extract footnote definitions of the form [^n]: URL from the end of the file.
    Returns a mapping from footnote key (e.g., "1") to URL string.
    """
    footnote_pattern = re.compile(r'^\[\^([^\]]+)\]:\s*(\S+)', re.MULTILINE)
    return {m.group(1): m.group(2) for m in footnote_pattern.finditer(text)}


def extract_ideas(raw_text: str) -> List[Idea]:
    """
    Parse the raw markdown text and return a list of Idea objects.
    The delimiter for each idea is a line starting with "## Blog Post Idea".
    If no such sections exist, treat the whole file as a single idea.
    """
    footnotes = load_footnotes(raw_text)

    # Check for explicit idea delimiters
    if not re.search(r'(?m)^## Blog Post Idea', raw_text):
        # Fallback: single idea from the entire document
        # Use the first markdown heading as the title if available
        title_match = re.search(r'^\s*#\s+(.+)$', raw_text, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else "Untitled"

        # Extract any footnote references in the whole text
        refs = re.findall(r'\[\^([^\]]+)\]', raw_text)
        sources = [footnotes.get(ref, "") for ref in refs if footnotes.get(ref)]

        # Since the file does not contain structured sections, leave them empty
        idea = Idea(
            title=title,
            pain_point="",
            target_audience="",
            content_details="",
            sources=sources,
        )
        return [idea]

    # Split on the delimiter line (keep the delimiter with the following block)
    blocks = re.split(r'(?m)^## Blog Post Idea', raw_text)
    ideas: List[Idea] = []

    # The first split part may contain pre‑amble; ignore if empty
    for block in blocks[1:]:
        # Prepend the delimiter back for easier parsing
        block = "## Blog Post Idea" + block

        # Extract title
        title_match = re.search(r'## Blog Post Idea\s*\d+:\s*"([^"]+)"', block)
        title = title_match.group(1).strip() if title_match else "Untitled"

        # Helper to extract a section between **Header**: and the next **Header** or end
        def get_section(header: str) -> str:
            pattern = rf'\*\*{re.escape(header)}\*\*:\s*(.*?)(?=\n\*\*|\Z)'
            m = re.search(pattern, block, re.DOTALL)
            return m.group(1).strip() if m else ""

        pain_point = get_section("Pain Point")
        target_audience = get_section("Target Audience")
        content_details = get_section("Content Details")

        # Find all footnote references inside this block
        refs = re.findall(r'\[\^([^\]]+)\]', block)
        sources = [footnotes.get(ref, "") for ref in refs if footnotes.get(ref)]

        idea = Idea(
            title=title,
            pain_point=pain_point,
            target_audience=target_audience,
            content_details=content_details,
            sources=sources,
        )
        ideas.append(idea)

    return ideas


def write_json(ideas: List[Idea], output_path: str):
    data = [asdict(idea) for idea in ideas]
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def write_sqlite(ideas: List[Idea], output_path: str, track: bool):
    conn = sqlite3.connect(output_path)
    cur = conn.cursor()

    # Base columns
    columns = [
        "id INTEGER PRIMARY KEY AUTOINCREMENT",
        "title TEXT",
        "pain_point TEXT",
        "target_audience TEXT",
        "content_details TEXT",
    ]

    # Optional metadata columns
    if track:
        meta_cols = [
            "article TEXT",
            "voice TEXT",
            "piece_type TEXT",
            "marketing_post_type TEXT",
            "primary_goal TEXT",
            "target_audience_meta TEXT",
            "technical_depth TEXT",
            "keywords TEXT",
            "length TEXT",
            "sections TEXT",
            "call_to_action TEXT",
            "pain_point_meta TEXT",
        ]
        columns.extend(meta_cols)

    cur.execute(f"CREATE TABLE ideas ({', '.join(columns)});")
    cur.execute(
        "CREATE TABLE sources (idea_id INTEGER, url TEXT, FOREIGN KEY(idea_id) REFERENCES ideas(id));"
    )

    # Insert ideas
    for idea in ideas:
        base_vals = (
            idea.title,
            idea.pain_point,
            idea.target_audience,
            idea.content_details,
        )
        if track:
            meta_vals = (
                idea.article,
                idea.voice,
                idea.piece_type,
                idea.marketing_post_type,
                idea.primary_goal,
                idea.target_audience_meta,
                idea.technical_depth,
                idea.keywords,
                idea.length,
                idea.sections,
                idea.call_to_action,
                idea.pain_point_meta,
            )
            cur.execute(
                """
                INSERT INTO ideas (title, pain_point, target_audience, content_details,
                article, voice, piece_type, marketing_post_type, primary_goal,
                target_audience_meta, technical_depth, keywords, length, sections,
                call_to_action, pain_point_meta)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                base_vals + meta_vals,
            )
        else:
            cur.execute(
                """
                INSERT INTO ideas (title, pain_point, target_audience, content_details)
                VALUES (?,?,?,?)
                """,
                base_vals,
            )
        idea_id = cur.lastrowid
        for url in idea.sources:
            cur.execute("INSERT INTO sources (idea_id, url) VALUES (?,?)", (idea_id, url))

    conn.commit()
    conn.close()


def main():
    parser = argparse.ArgumentParser(description="Parse blog‑post idea markdown files.")
    parser.add_argument("--input", required=True, help="Path to the source .md or .txt file.")
    parser.add_argument(
        "--output",
        help="Destination file. Defaults: ideas.json (JSON) or ideas.db (SQLite).",
    )
    parser.add_argument(
        "--format",
        choices=["json", "sqlite"],
        default="json",
        help="Output format (default: json).",
    )
    parser.add_argument(
        "--track",
        action="store_true",
        help="Create optional metadata columns (empty by default).",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        sys.stderr.write(f"Error: input file '{args.input}' does not exist.\n")
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as f:
        raw_text = f.read()

    ideas = extract_ideas(raw_text)

    # Determine output path if not supplied
    if args.output:
        out_path = args.output
    else:
        out_path = "ideas.json" if args.format == "json" else "ideas.db"

    if args.format == "json":
        write_json(ideas, out_path)
    else:
        write_sqlite(ideas, out_path, args.track)

    print(f"Successfully wrote {len(ideas)} ideas to '{out_path}'.")


if __name__ == "__main__":
    main()
