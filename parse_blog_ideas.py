#!/usr/bin/env python3
"""
Script to parse blog post idea files and standardize their formatting.
This script reads markdown files containing blog post ideas and extracts
the structured data, associating URLs with their corresponding ideas.
"""

import re
import json
import os
from typing import List, Dict, Tuple


def parse_blog_ideas_file(file_path: str) -> List[Dict]:
    """
    Parse a blog ideas markdown file and return structured data.
    
    Args:
        file_path (str): Path to the markdown file
        
    Returns:
        List[Dict]: List of blog post idea dictionaries
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split content into sections based on the separator
    # Handle both types of separators
    sections = re.split(r'\n#{10,}\n', content.strip())
    
    # Remove the last empty section if it exists
    if sections and not sections[-1].strip():
        sections.pop()
    
    # Extract URL references from the end of the file
    url_references = extract_url_references(content)
    
    blog_ideas = []
    
    # Process each section
    for i, section in enumerate(sections):
        # Skip empty sections
        if not section.strip():
            continue
            
        # Extract the blog post idea
        idea = parse_blog_idea_section(section, url_references, i + 1)
        if idea:
            blog_ideas.append(idea)
    
    return blog_ideas


def extract_url_references(content: str) -> Dict[str, str]:
    """
    Extract URL references from the end of the content.
    
    Args:
        content (str): Full file content
        
    Returns:
        Dict[str, str]: Dictionary mapping reference numbers to URLs
    """
    # Find the URL reference section (everything after the last separator)
    # Look for the pattern [^number]: url
    url_pattern = r'\[\^(\d+)\]\s*:\s*(https?://[^\n]+)'
    
    # Find all URL references
    matches = re.findall(url_pattern, content, re.MULTILINE)
    
    # Create dictionary mapping reference numbers to URLs
    url_refs = {}
    for ref_num, url in matches:
        url_refs[f"[^{ref_num}]"] = url.strip()
    
    return url_refs


def parse_blog_idea_section(section: str, url_references: Dict[str, str], idea_number: int) -> Dict:
    """
    Parse a single blog idea section.
    
    Args:
        section (str): Raw section content
        url_references (Dict[str, str]): URL reference mappings
        idea_number (int): The idea number
        
    Returns:
        Dict: Parsed blog idea dictionary
    """
    # Extract title
    title_match = re.search(r'^##\s*(?:Blog Post Idea\s+\d+:\s*)?"([^"]+)"', section, re.MULTILINE)
    if not title_match:
        # Try alternative pattern for photogrammetry file
        title_match = re.search(r'^##\s*(\d+\.\s+.+)', section, re.MULTILINE)
        if not title_match:
            return None
    
    title = title_match.group(1).strip()
    
    # Extract sections using regex patterns
    pain_point_match = re.search(r'\*\*Pain Point\*\*:\s*(.*?)(?=\*\*Target Audience\*\*|\*\*Content Details\*\*|$)', 
                                section, re.DOTALL | re.MULTILINE)
    target_audience_match = re.search(r'\*\*Target Audience\*\*:\s*(.*?)(?=\*\*Content Details\*\*|$)', 
                                     section, re.DOTALL | re.MULTILINE)
    content_details_match = re.search(r'\*\*Content Details\*\*:\s*(.*?)(?=$)', 
                                     section, re.DOTALL | re.MULTILINE)
    
    # Extract references from the content to find associated URLs
    references_in_content = re.findall(r'\[\^(\d+)\]', section)
    
    # Get URLs associated with this idea
    urls = []
    for ref in references_in_content:
        ref_key = f"[^{ref}]"
        if ref_key in url_references:
            urls.append(url_references[ref_key])
    
    # Clean up the extracted content
    pain_point = pain_point_match.group(1).strip() if pain_point_match else ""
    target_audience = target_audience_match.group(1).strip() if target_audience_match else ""
    content_details = content_details_match.group(1).strip() if content_details_match else ""
    
    # Clean up the content by removing extra whitespace and newlines
    pain_point = re.sub(r'\s+', ' ', pain_point)
    target_audience = re.sub(r'\s+', ' ', target_audience)
    content_details = re.sub(r'\s+', ' ', content_details)
    
    return {
        "id": idea_number,
        "title": title,
        "pain_point": pain_point,
        "target_audience": target_audience,
        "content_details": content_details,
        "urls": urls
    }


def process_all_files(input_directory: str, output_file: str) -> None:
    """
    Process all blog ideas files in the input directory.
    
    Args:
        input_directory (str): Directory containing markdown files
        output_file (str): Output JSON file path
    """
    all_ideas = []
    
    # Find all markdown files in the directory
    for filename in os.listdir(input_directory):
        if filename.endswith('.md') and not filename.startswith('.'):
            file_path = os.path.join(input_directory, filename)
            print(f"Processing {filename}...")
            ideas = parse_blog_ideas_file(file_path)
            all_ideas.extend(ideas)
            print(f"  Found {len(ideas)} blog post ideas")
    
    # Write to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_ideas, f, indent=2, ensure_ascii=False)
    
    print(f"\nProcessed {len(all_ideas)} total blog post ideas")
    print(f"Output saved to {output_file}")


def main():
    """Main function to run the parser."""
    # Process the two example files
    input_dir = "research/perplexity/cleaned_chats"
    output_file = "parsed_blog_ideas.json"
    
    if not os.path.exists(input_dir):
        print(f"Input directory {input_dir} does not exist")
        return
    
    print("Parsing blog post ideas files...")
    process_all_files(input_dir, output_file)
    
    # Display sample of results
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"\nSample of parsed data ({len(data)} items):")
        for i, idea in enumerate(data[:3]):  # Show first 3 items
            print(f"\n--- Idea {idea['id']}: {idea['title']} ---")
            print(f"Pain Point: {idea['pain_point'][:100]}...")
            print(f"URLs: {len(idea['urls'])} references")
            
    except Exception as e:
        print(f"Error reading output file: {e}")


if __name__ == "__main__":
    main()
