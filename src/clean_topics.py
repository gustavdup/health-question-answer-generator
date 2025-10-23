#!/usr/bin/env python3
"""
Clean up topic files - remove leading numbers from questions.
"""

import re
from pathlib import Path

def clean_file(file_path):
    """Remove leading numbers (like '1. ', '10. ') from questions."""
    print(f"Cleaning: {file_path.name}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    cleaned_lines = []
    changes_made = 0
    
    for line in lines:
        # Remove leading numbers like "1. ", "10. ", etc.
        original = line
        cleaned = re.sub(r'^\d+\.\s+', '', line)
        
        if cleaned != original:
            changes_made += 1
        
        cleaned_lines.append(cleaned)
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(cleaned_lines)
    
    print(f"  ✓ Removed {changes_made} question numbers\n")
    return changes_made

def main():
    """Clean all topic files in data/ folder."""
    data_dir = Path(__file__).parent.parent / "data"
    
    # Get all numbered topic files (1_*.txt through 8_*.txt)
    topic_files = sorted([
        f for f in data_dir.glob("[1-8]_*.txt") 
        if f.is_file()
    ])
    
    if not topic_files:
        print("No topic files found!")
        return
    
    print("=" * 60)
    print("CLEANING TOPIC FILES")
    print("=" * 60)
    print()
    
    total_changes = 0
    for file_path in topic_files:
        total_changes += clean_file(file_path)
    
    print("=" * 60)
    print(f"✓ Complete! Cleaned {len(topic_files)} files")
    print(f"  Total question numbers removed: {total_changes}")
    print("=" * 60)

if __name__ == "__main__":
    main()
