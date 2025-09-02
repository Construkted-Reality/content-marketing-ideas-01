#!/usr/bin/env python3
"""
Simple script to parse blog post idea files and standardize their formatting.
This script processes each file separately to avoid mixing content.
"""

import re
import json
import os
from typing import List, Dict


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


def parse_mobile_lidar_file(file_path: str) -> List[Dict]:
    """
    Parse the mobile LiDAR blog ideas file.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by the separator lines
    sections = re.split(r'\n#{10,}\n', content.strip())
    
    # Remove empty sections
    sections = [s for s in sections if s.strip()]
    
    # Extract URL references
    url_references = extract_url_references(content)
    
    ideas = []
    
    for i, section in enumerate(sections):
        # Skip if empty
        if not section.strip():
            continue
            
        # Extract title - looks for "## Blog Post Idea X: \"Title\""
        title_match = re.search(r'^##\s*Blog Post Idea\s+(\d+):\s*"([^"]+)"', section, re.MULTILINE)
        if not title_match:
            continue
            
        idea_number = int(title_match.group(1))
        title = title_match.group(2)
        
        # Extract sections
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
        
        # Clean up content
        pain_point = pain_point_match.group(1).strip() if pain_point_match else ""
        target_audience = target_audience_match.group(1).strip() if target_audience_match else ""
        content_details = content_details_match.group(1).strip() if content_details_match else ""
        
        # Clean whitespace
        pain_point = re.sub(r'\s+', ' ', pain_point)
        target_audience = re.sub(r'\s+', ' ', target_audience)
        content_details = re.sub(r'\s+', ' ', content_details)
        
        ideas.append({
            "id": idea_number,
            "title": title,
            "pain_point": pain_point,
            "target_audience": target_audience,
            "content_details": content_details,
            "urls": urls
        })
    
    return ideas


def parse_photogrammetry_file(file_path: str) -> List[Dict]:
    """
    Parse the photogrammetry blog ideas file.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by the separator lines
    sections = re.split(r'\n#{10,}\n', content.strip())
    
    # Remove empty sections
    sections = [s for s in sections if s.strip()]
    
    # Extract URL references
    url_references = extract_url_references(content)
    
    ideas = []
    
    for i, section in enumerate(sections):
        # Skip if empty
        if not section.strip():
            continue
            
        # Extract title - looks for "## X. Title"
        title_match = re.search(r'^##\s*(\d+\.\s+.+)', section, re.MULTILINE)
        if not title_match:
            continue
            
        # Extract the number from the title
        title_line = title_match.group(1)
        # Extract number from "1. Why Your..." pattern
        number_match = re.match(r'^(\d+)\.', title_line)
        if not number_match:
            continue
            
        idea_number = int(number_match.group(1))
        title = title_line.strip()
        
        # Extract sections
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
        
        # Clean up content
        pain_point = pain_point_match.group(1).strip() if pain_point_match else ""
        target_audience = target_audience_match.group(1).strip() if target_audience_match else ""
        content_details = content_details_match.group(1).strip() if content_details_match else ""
        
        # Clean whitespace
        pain_point = re.sub(r'\s+', ' ', pain_point)
        target_audience = re.sub(r'\s+', ' ', target_audience)
        content_details = re.sub(r'\s+', ' ', content_details)
        
        ideas.append({
            "id": idea_number,
            "title": title,
            "pain_point": pain_point,
            "target_audience": target_audience,
            "content_details": content_details,
            "urls": urls
        })
    
    return ideas


def main():
    """Main function to run the parser."""
    input_dir = "research/perplexity/cleaned_chats"
    output_file = "parsed_blog_ideas.json"
    
    if not os.path.exists(input_dir):
        print(f"Input directory {input_dir} does not exist")
        return
    
    all_ideas = []
    
    # Process each file
    for filename in os.listdir(input_dir):
        if filename.endswith('.md') and not filename.startswith('.'):
            file_path = os.path.join(input_dir, filename)
            print(f"Processing {filename}...")
            
            if "mobile-lidar" in filename:
                ideas = parse_mobile_lidar_file(file_path)
                print(f"  Found {len(ideas)} mobile LiDAR blog post ideas")
                all_ideas.extend(ideas)
            elif "photogrammetry" in filename:
                ideas = parse_photogrammetry_file(file_path)
                print(f"  Found {len(ideas)} photogrammetry blog post ideas")
                all_ideas.extend(ideas)
    
    # Write to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_ideas, f, indent=2, ensure_ascii=False)
    
    print(f"\nProcessed {len(all_ideas)} total blog post ideas")
    print(f"Output saved to {output_file}")
    
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
