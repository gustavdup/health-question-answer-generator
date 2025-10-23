#!/usr/bin/env python3
"""
Create a test file with one random question from each topic.
"""

import sys
import random
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.run_batch import parse_input_file

def create_random_test_file():
    """Create a test file with one random question from each topic file."""
    data_dir = Path(__file__).parent.parent / "data"
    
    # Get all main topic files (1-8), excluding test files
    topic_files = sorted([
        f for f in data_dir.glob("[1-8]_*.txt") 
        if f.is_file() and "test" not in f.name.lower()
    ])
    
    if not topic_files:
        print("No topic files found!")
        return
    
    print("=" * 60)
    print("Creating random test file from all topics")
    print("=" * 60)
    print()
    
    output_lines = []
    selected_questions = []
    
    # Track what we've used to ensure diversity
    used_genders = []
    used_contexts = []
    
    for topic_file in topic_files:
        # Parse the file to get all questions
        all_records = parse_input_file(topic_file)
        
        if not all_records:
            print(f"⚠️  No questions found in {topic_file.name}")
            continue
        
        # Try to select a question with diverse gender/context
        # Prioritize combinations we haven't used yet
        selected = None
        attempts = 0
        max_attempts = 50
        
        while attempts < max_attempts:
            candidate = random.choice(all_records)
            gender_context = (candidate['gender'], candidate['care_focus'], candidate['has_kids'])
            
            # If we have fewer than 3 selections, just pick anything
            if len(selected_questions) < 3:
                selected = candidate
                break
            
            # Try to find something we haven't used
            if gender_context not in used_contexts:
                selected = candidate
                break
            
            attempts += 1
        
        # If we couldn't find a unique combo after many attempts, just use the last candidate
        if selected is None:
            selected = candidate
        
        # Track what we've used
        used_genders.append(selected['gender'])
        used_contexts.append((selected['gender'], selected['care_focus'], selected['has_kids']))
        selected_questions.append(selected)
        
        print(f"✓ Selected from {topic_file.name}:")
        print(f"  Topic: {selected['topic']}")
        print(f"  Gender: {selected['gender']}, Context: {selected['care_focus']} ({selected['has_kids']} kids)")
        print(f"  Question: {selected['question'][:60]}...")
        print()
        
        # Build the output format
        topic_line = f"Topic {len(selected_questions)}: {selected['topic']}\n"
        output_lines.append(topic_line)
        output_lines.append("\n")
        
        # Add gender emoji
        if selected['gender'] == "Female":
            output_lines.append("💗 Female\n")
        elif selected['gender'] == "Male":
            output_lines.append("🩵 Male\n")
        else:  # Gender Neutral
            output_lines.append("💚 Gender Neutral\n")
        output_lines.append("\n")
        
        # Add context header
        if selected['care_focus'] == "Myself" and selected['has_kids'] == "No":
            context_emoji = "🩺"
        elif selected['care_focus'] == "Myself" and selected['has_kids'] == "Yes":
            context_emoji = "👩‍👧" if selected['gender'] == "Female" else "👨‍👧" if selected['gender'] == "Male" else "💬"
        elif selected['care_focus'] == "My Kids":
            context_emoji = "👶"
        elif selected['care_focus'] == "My Family" and selected['has_kids'] == "No":
            context_emoji = "🏡"
        elif selected['care_focus'] == "My Family" and selected['has_kids'] == "Yes":
            context_emoji = "💞"
        else:
            context_emoji = "💬"
        
        care_text = selected['care_focus']
        kids_text = f" ({'With' if selected['has_kids'] == 'Yes' else 'No'} Kids)"
        if selected['care_focus'] != "My Kids":
            context_line = f"{context_emoji} {care_text}{kids_text}\n"
        else:
            context_line = f"{context_emoji} {care_text}\n"
        
        output_lines.append(context_line)
        output_lines.append(f"{selected['question']}\n")
        output_lines.append("\n")
        output_lines.append("\n")
    
    # Write to output file
    output_file = data_dir / "10_random_test.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)
    
    print("=" * 60)
    print(f"✓ Created: {output_file.name}")
    print(f"  Total questions: {len(selected_questions)}")
    print("=" * 60)

if __name__ == "__main__":
    # Set random seed for reproducibility (optional - remove for true randomness)
    # random.seed(42)
    create_random_test_file()
