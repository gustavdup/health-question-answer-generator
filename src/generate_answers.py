#!/usr/bin/env python3
"""
Interactive script - lets you select which topic file to process.
Outputs are saved to outputs/ folder with timestamp.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

# Import the batch processor
from src import run_batch

def list_topic_files():
    """List all topic files in data/ folder."""
    data_dir = Path(__file__).parent.parent / "data"
    topic_files = sorted([f for f in data_dir.glob("*.txt") if f.is_file()])
    return topic_files

def display_menu(files):
    """Display the file selection menu."""
    print("=" * 70)
    print("TOPIC FILE SELECTOR")
    print("=" * 70)
    print()
    print("Available topic files:")
    print()
    
    for idx, file in enumerate(files, 1):
        print(f"  [{idx}] {file.name}")
    
    print()
    print("  [0] Exit")
    print()

def get_user_choice(max_choice):
    """Get and validate user input."""
    while True:
        try:
            choice = input(f"Select a file (0-{max_choice}): ").strip()
            choice_num = int(choice)
            
            if 0 <= choice_num <= max_choice:
                return choice_num
            else:
                print(f"❌ Please enter a number between 0 and {max_choice}")
        except ValueError:
            print("❌ Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\nExiting...")
            sys.exit(0)

def create_output_filename(input_file: Path):
    """Create output filename with timestamp."""
    # Get the base name without extension (e.g., "1_energy_fatigue")
    base_name = input_file.stem
    
    # Get current Unix timestamp
    timestamp = int(datetime.now().timestamp())
    
    # Create filename: basename_timestamp.csv
    output_filename = f"{base_name}_{timestamp}.csv"
    
    return output_filename

def main():
    """Main interactive function."""
    # Get base directory
    base_dir = Path(__file__).parent.parent
    
    # Create outputs directory if it doesn't exist
    outputs_dir = base_dir / "outputs"
    outputs_dir.mkdir(exist_ok=True)
    
    # List all topic files
    topic_files = list_topic_files()
    
    if not topic_files:
        print("❌ No topic files found in data/ folder")
        sys.exit(1)
    
    # Display menu
    display_menu(topic_files)
    
    # Get user choice
    choice = get_user_choice(len(topic_files))
    
    if choice == 0:
        print("Exiting...")
        sys.exit(0)
    
    # Get selected file (adjust for 0-based indexing)
    selected_file = topic_files[choice - 1]
    
    # Create output filename
    output_filename = create_output_filename(selected_file)
    output_path = outputs_dir / output_filename
    
    print()
    print("=" * 70)
    print(f"Processing: {selected_file.name}")
    print(f"Output to:  outputs/{output_filename}")
    print("=" * 70)
    print()
    
    # Override run_batch file paths
    run_batch.INPUT_FILE = selected_file
    run_batch.OUTPUT_FILE = output_path
    
    # Run the batch processor
    try:
        run_batch.main()
    except KeyboardInterrupt:
        print("\n\n❌ Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
