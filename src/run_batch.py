#!/usr/bin/env python3
"""
Batch process health questions through OpenAI Assistants API.
Reads structured questions from data/topics.txt and writes responses to outputs.csv.
"""

import os
import csv
import time
import re
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

if not OPENAI_API_KEY or not ASSISTANT_ID:
    raise ValueError("Missing OPENAI_API_KEY or ASSISTANT_ID in .env file")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# File paths (must be set by caller before calling main())
BASE_DIR = Path(__file__).parent.parent
INPUT_FILE = None
OUTPUT_FILE = None

# Response template
RESPONSE_TEMPLATE = """

The user has just installed the Dr Gabi app and entered the personal details as part of starting onboarding within the app.
They've selected a specific topic and question related to their health that we need to answer to show them what Dr Gabi can do.
This is the first message Dr Gabi sends after the user’s first question — it should make them feel understood, supported, and confident in her help.
Write a short, calm, and reassuring message addressed to the person, as Dr Gabi. 
Assume you already have a trusted relationship with them.

Your response should:
• Start with one brief empathetic sentence or two that acknowledges their situation.
• Follow with 2–3 short bullet points (each under one line) explaining how you can help in their context.
• End with one short reflective statement that leaves the user feeling hopeful and intrigued — as if there’s more to uncover together. It should make them want to keep exploring or ask another question, without ever mentioning products, features, or trials. The tone should feel quietly confident and human — like a caring expert planting a seed of curiosity.
• Never ask the user a question as they can't respond at this stage.

Keep it under 150 words total, but lean towards 100 where possible. 
Tone: warm, supportive, and conversational, never promotional or overly detailed.
Reference their role in the response when when helpful (e.g., "as a mother", "for your family").

Users Question:
{question}"""


def parse_input_file(file_path: Path) -> List[Dict[str, str]]:
    """
    Parse the topics.txt file into structured records.
    
    Returns list of dicts with keys:
    - topic: str
    - gender: str (Female, Male, Gender Neutral)
    - care_focus: str (Myself, My Kids, My Family)
    - has_kids: str (Yes, No)
    - role: str (mother, father, parent, individual)
    - question: str
    """
    records = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # State tracking
    current_topic = None
    current_gender = None
    current_care_focus = None
    current_has_kids = None
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Topic line: "Topic 1: Energy & Fatigue"
        if line.startswith("Topic "):
            match = re.match(r"Topic \d+:\s*(.+)", line)
            if match:
                current_topic = match.group(1).strip()
            continue
        
        # Gender headers
        if line.startswith("💗") and "Female" in line:
            current_gender = "Female"
            continue
        elif line.startswith("🩵") and "Male" in line:
            current_gender = "Male"
            continue
        elif line.startswith("💚") and "Gender Neutral" in line:
            current_gender = "Gender Neutral"
            continue
        
        # Context headers (care focus + has_kids)
        # 🩺 Myself (No Kids)
        # 👩‍👧 or 👨‍👧 Myself (With Kids)
        # 👶 My Kids
        # 🏡 My Family (No Kids)
        # 💞 My Family (With Kids)
        # 💬 Generic emoji for Gender Neutral
        
        if any(emoji in line for emoji in ["🩺", "👩‍👧", "👨‍👧", "👶", "🏡", "💞", "💬"]):
            # Extract care focus and has_kids from the line
            if "Myself (No Kids)" in line:
                current_care_focus = "Myself"
                current_has_kids = "No"
            elif "Myself (With Kids)" in line:
                current_care_focus = "Myself"
                current_has_kids = "Yes"
            elif "My Kids" in line:
                current_care_focus = "My Kids"
                current_has_kids = "Yes"  # Implicit if you have kids
            elif "My Family (No Kids)" in line:
                current_care_focus = "My Family"
                current_has_kids = "No"
            elif "My Family (With Kids)" in line:
                current_care_focus = "My Family"
                current_has_kids = "Yes"
            continue
        
        # If we have all context set, this is a question line
        if current_topic and current_gender and current_care_focus and current_has_kids:
            # Strip leading numbers like "4." or "10."
            question = re.sub(r"^\d+\.\s*", "", line).strip()
            
            if question:
                # Infer role
                role = infer_role(current_gender, current_has_kids)
                
                records.append({
                    "topic": current_topic,
                    "gender": current_gender,
                    "care_focus": current_care_focus,
                    "has_kids": current_has_kids,
                    "role": role,
                    "question": question
                })
    
    return records


def infer_role(gender: str, has_kids: str) -> str:
    """Infer role from gender and has_kids status."""
    if has_kids == "Yes":
        if gender == "Female":
            return "mother"
        elif gender == "Male":
            return "father"
        else:  # Gender Neutral
            return "parent"
    return "individual"


def build_message(record: Dict[str, str]) -> str:
    """Build the user message to send to the assistant."""
    context_summary = (
        f"Context:\n"
        f"• Topic: {record['topic']}\n"
        f"• Gender: {record['gender']}\n"
        f"• Care focus: {record['care_focus']}\n"
        f"• Has kids: {record['has_kids']}\n"
        f"• Inferred role: {record['role']}\n\n"
    )
    
    template_filled = RESPONSE_TEMPLATE.format(
        question=record['question']
    )
    
    return context_summary + template_filled


@retry(
    retry=retry_if_exception_type((Exception,)),
    wait=wait_exponential(multiplier=1, min=2, max=60),
    stop=stop_after_attempt(5)
)
def call_assistant_api(message: str) -> Dict[str, str]:
    """
    Call OpenAI Assistants API with retry logic.
    
    Returns dict with:
    - response: str (assistant's text reply)
    - thread_id: str
    - run_id: str
    - status: str (completed, failed, etc.)
    - error: str or None
    """
    try:
        # Create a new thread
        thread = client.beta.threads.create()
        thread_id = thread.id
        
        # Add user message to thread
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message
        )
        
        # Create and run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )
        run_id = run.id
        
        # Poll until completion
        max_polls = 60  # 5 minutes max (5 second intervals)
        poll_count = 0
        
        while poll_count < max_polls:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id
            )
            
            if run_status.status == "completed":
                # Get the assistant's messages
                messages = client.beta.threads.messages.list(thread_id=thread_id)
                
                # Find the latest assistant message
                for msg in messages.data:
                    if msg.role == "assistant":
                        # Extract text from message content
                        response_text = ""
                        for content_block in msg.content:
                            if content_block.type == "text":
                                response_text += content_block.text.value
                        
                        return {
                            "response": response_text.strip(),
                            "thread_id": thread_id,
                            "run_id": run_id,
                            "status": "completed",
                            "error": None
                        }
                
                # No assistant message found
                return {
                    "response": "",
                    "thread_id": thread_id,
                    "run_id": run_id,
                    "status": "completed",
                    "error": "No assistant response found"
                }
            
            elif run_status.status in ["failed", "cancelled", "expired"]:
                error_msg = f"Run {run_status.status}"
                if hasattr(run_status, 'last_error') and run_status.last_error:
                    error_msg += f": {run_status.last_error}"
                
                return {
                    "response": "",
                    "thread_id": thread_id,
                    "run_id": run_id,
                    "status": run_status.status,
                    "error": error_msg
                }
            
            # Still processing, wait and poll again
            time.sleep(5)
            poll_count += 1
        
        # Timeout
        return {
            "response": "",
            "thread_id": thread_id,
            "run_id": run_id,
            "status": "timeout",
            "error": "Run timed out after 5 minutes"
        }
    
    except Exception as e:
        # Let tenacity retry handle transient errors
        raise


def load_processed_questions() -> set:
    """Load already processed questions from outputs.csv for resume capability."""
    if not OUTPUT_FILE.exists():
        return set()
    
    processed = set()
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            processed.add(row['question'])
    
    return processed


def append_to_csv(record: Dict[str, str], result: Dict[str, str], prompt: str):
    """Append a result row to outputs.csv."""
    file_exists = OUTPUT_FILE.exists()
    
    with open(OUTPUT_FILE, 'a', newline='', encoding='utf-8') as f:
        fieldnames = [
            'topic', 'gender', 'care_focus', 'has_kids', 'role',
            'prompt', 'question', 'response', 'thread_id', 'run_id', 'status', 'error'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow({
            'topic': record['topic'],
            'gender': record['gender'],
            'care_focus': record['care_focus'],
            'has_kids': record['has_kids'],
            'role': record['role'],
            'prompt': prompt,
            'question': record['question'],
            'response': result['response'],
            'thread_id': result['thread_id'],
            'run_id': result['run_id'],
            'status': result['status'],
            'error': result['error'] or ''
        })


def main():
    """Main batch processing function."""
    # Validate that file paths are set
    if INPUT_FILE is None or OUTPUT_FILE is None:
        raise ValueError(
            "INPUT_FILE and OUTPUT_FILE must be set before calling main(). "
            "Use generate_answers.py as the entry point."
        )
    
    print("=" * 60)
    print("Health Questions Batch Processor")
    print("=" * 60)
    print()
    
    # Parse input file
    print(f"Reading questions from: {INPUT_FILE}")
    records = parse_input_file(INPUT_FILE)
    print(f"Found {len(records)} questions to process")
    print()
    
    # Load already processed questions
    processed_questions = load_processed_questions()
    if processed_questions:
        print(f"Resuming: {len(processed_questions)} questions already processed")
        records = [r for r in records if r['question'] not in processed_questions]
        print(f"Remaining: {len(records)} questions to process")
    print()
    
    if not records:
        print("✓ All questions already processed!")
        return
    
    # Process each record
    total = len(records)
    for i, record in enumerate(records, 1):
        print(f"Processing {i} of {total}: {record['question'][:60]}...")
        
        try:
            # Build message and call API
            message = build_message(record)
            result = call_assistant_api(message)
            
            # Save to CSV with the prompt
            append_to_csv(record, result, message)
            
            if result['status'] == 'completed':
                print(f"  ✓ Success (thread: {result['thread_id'][:8]}...)")
            else:
                print(f"  ✗ Failed: {result['error']}")
        
        except Exception as e:
            # Record failure and continue
            print(f"  ✗ Error: {str(e)}")
            result = {
                "response": "",
                "thread_id": "",
                "run_id": "",
                "status": "failed",
                "error": str(e)
            }
            # Build message for failed attempts too
            message = build_message(record)
            append_to_csv(record, result, message)
        
        print()
    
    print("=" * 60)
    print(f"✓ Batch processing complete!")
    print(f"Results saved to: {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
