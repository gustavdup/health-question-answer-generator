# Health Question Answer Generator

A minimal Python 3 batch processor that retrieves answers to structured health questions using the OpenAI Assistants API. The system is synchronous, resume-safe, and designed for processing large batches of questions with automatic error handling and retry logic.

## Features

- ✅ Batch processes structured health questions from text files
- ✅ Uses OpenAI Assistants API (threads, messages, runs)
- ✅ Resume-safe: skip already processed questions
- ✅ Exponential backoff retry logic for rate limits
- ✅ Continues processing on individual failures
- ✅ CSV output with full tracking (thread_id, run_id, status)
- ✅ Clean synchronous Python implementation

## Project Structure

```
Question Answer Generator/
├── src/
│   ├── __init__.py        # Makes src a Python package
│   └── run_batch.py       # Main batch processing script
├── data/
│   └── topics.txt         # Input: structured questions (see format below)
├── outputs.csv            # Output: generated at runtime
├── .env.example           # Template for environment variables
├── .env                   # Your actual credentials (create from .env.example)
├── .gitignore             # Git ignore rules
├── requirements.txt       # Python dependencies
├── setup.sh               # Setup script for macOS/Linux
├── setup.bat              # Setup script for Windows
└── README.md              # This file
```

## Setup

### Quick Setup (Recommended)

The easiest way to set up the project is using the provided setup scripts:

**On macOS/Linux:**
```bash
cd "Question Answer Generator"
./setup.sh
```

**On Windows:**
```cmd
cd "Question Answer Generator"
setup.bat
```

These scripts will:
1. Create a virtual environment
2. Install all dependencies
3. Create a `.env` file from the template

After running the setup script, **edit `.env`** and add your OpenAI credentials.

### Manual Setup

If you prefer to set up manually:

#### 1. Clone or Download the Project

Ensure you have this project directory on your local machine.

#### 2. Create a Virtual Environment

It's recommended to use a Python virtual environment to isolate dependencies.

```bash
# Navigate to the project directory
cd "Question Answer Generator"

# Create virtual environment
python3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

#### 3. Install Dependencies

With your virtual environment activated:

```bash
pip install -r requirements.txt
```

This installs:
- `openai>=1.40.0` - Official OpenAI Python SDK
- `python-dotenv>=1.0.0` - For loading environment variables
- `pandas>=2.0.0` - For data handling (optional but useful)
- `tenacity>=8.0.0` - For retry logic with exponential backoff

#### 4. Configure Environment Variables

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```
OPENAI_API_KEY=sk-your-actual-openai-api-key
ASSISTANT_ID=asst_your-actual-assistant-id
```

**Important:** 
- Your OpenAI Assistant should already have system instructions configured.
- The script only sends user messages with context and questions.

#### 5. Prepare Your Input File

The script reads questions from `data/topics.txt`. An example file is already provided. See the **Input Format** section below for details on the structure.

## Usage

### Run the Interactive Answer Generator

The main way to use this tool is through the interactive script:

```bash
python src/generate_answers.py
```

or

```bash
python -m src.generate_answers
```

### What Happens

1. The script displays a menu of all topic files in `data/`
2. You select a file by typing its number (1-10)
3. The script processes all questions in that file
4. Results are saved to `outputs/` with a unique timestamped filename

Example: If you select `1_energy_fatigue.txt`, the output will be saved as `outputs/1_energy_fatigue_1729702345.csv`

1. The script reads `data/topics.txt` and parses all questions
2. Checks `outputs.csv` for already-processed questions (resume capability)
3. For each new question:
   - Creates a new OpenAI thread
   - Sends a structured message with context + question
   - Polls the run until completed
   - Extracts the assistant's response
   - Appends results to `outputs.csv`
4. Prints progress: "Processing i of N"
5. Continues even if individual questions fail (logs error in CSV)

### Resume Capability

If the script is interrupted or you rerun the same file, simply execute:

```bash
python src/generate_answers.py
```

Select the same file number, and the script will automatically skip questions already present in the corresponding output file (matched by exact question text).

## Input Format

The `data/topics.txt` file has a specific structure with repeating sections:

### Structure

```
Topic 1: Energy & Fatigue
💗 Female
🩺 Myself (No Kids)
I'm constantly tired—could this be thyroid or anemia?
Why do I feel drained even when I rest?
What small changes could boost my daily energy?
👩‍👧 Myself (With Kids)
How can I recover energy while raising kids nonstop?
Is my exhaustion just stress or something medical?
...
👶 My Kids
My child's always tired—what could be causing it?
...
🏡 My Family (No Kids)
Why do we all feel drained after simple days?
...
💞 My Family (With Kids)
Our whole family feels tired—where should we start?
...
🩵 Male
🩺 Myself (No Kids)
...
💚 Gender Neutral
💬 Myself (No Kids)
...
```

### Parsing Rules

1. **Topic Lines:** Start with "Topic X: ..." → captures topic name
   - Example: `Topic 1: Energy & Fatigue`

2. **Gender Headers:** Set the current gender context
   - `💗 Female` → gender = "Female"
   - `🩵 Male` → gender = "Male"
   - `💚 Gender Neutral` → gender = "Gender Neutral"

3. **Context Headers:** Define care focus and kids status
   - `🩺 Myself (No Kids)` → care_focus = "Myself", has_kids = "No"
   - `👩‍👧` or `👨‍👧 Myself (With Kids)` → care_focus = "Myself", has_kids = "Yes"
   - `👶 My Kids` → care_focus = "My Kids", has_kids = "Yes"
   - `🏡 My Family (No Kids)` → care_focus = "My Family", has_kids = "No"
   - `💞 My Family (With Kids)` → care_focus = "My Family", has_kids = "Yes"
   - `💬` → Generic emoji for Gender Neutral sections

4. **Questions:** All non-blank lines following a context header
   - Leading numbers (e.g., "4." or "10.") are automatically stripped
   - Each question becomes one record

### Role Inference

The script automatically infers user role from gender + has_kids:

| Gender | Has Kids | Role |
|--------|----------|------|
| Female | Yes | mother |
| Male | Yes | father |
| Gender Neutral | Yes | parent |
| Any | No | individual |

## Message Construction

For each question, the script sends a structured message to the assistant:

```
Context Summary: Topic = [topic]; Gender = [gender]; Care focus = [care_focus]; Has kids = [Yes|No]; Inferred role = [role].

The user has just completed onboarding and provided the following:
• Gender: [Female | Male | Gender Neutral]
• Care focus: [Myself | My Kids | My Family]
• Has kids: [Yes | No]
From this, infer whether the user is a [mother | father | parent | individual].

Write a short, calm, and reassuring message addressed to the person, as Dr Gabi. Assume you already have a trusted relationship with them.
Your response should:
• Start with one brief empathetic sentence or two that acknowledges their situation.
• Follow with 2–3 very short bullet points (each under one line) explaining how you can help in their context.
• End with one short reflective question that encourages engagement.
Keep it under 100 words total — warm, supportive, and conversational, never promotional or overly detailed.
Do not use the person's name; you may reference their role when helpful (e.g., "as a mother", "for your family").

User Question:
[exact question text]
```

The assistant should already have system instructions; this message provides the per-question context.

## Output Format

Results are saved to `outputs.csv` with the following columns:

| Column | Description |
|--------|-------------|
| `topic` | The topic name (e.g., "Energy & Fatigue") |
| `gender` | Female, Male, or Gender Neutral |
| `care_focus` | Myself, My Kids, or My Family |
| `has_kids` | Yes or No |
| `role` | mother, father, parent, or individual |
| `question` | The exact question text |
| `response` | The assistant's text response |
| `thread_id` | OpenAI thread ID |
| `run_id` | OpenAI run ID |
| `status` | completed, failed, timeout, cancelled, expired |
| `error` | Error message if status != completed |

## Error Handling

- **Retry Logic:** Uses exponential backoff (2s to 60s, up to 5 attempts) via `tenacity`
- **Rate Limits:** Automatically retries on rate limit errors
- **Transient Errors:** Network issues, API timeouts → retry
- **Permanent Failures:** Recorded in CSV with error message, processing continues
- **Timeout:** If a run takes >5 minutes, it's marked as timeout and script moves on

## Troubleshooting

### "Missing OPENAI_API_KEY or ASSISTANT_ID"

- Ensure `.env` file exists in the project root
- Check that both variables are set correctly

### "No such file or directory: data/topics.txt"

- Ensure `data/topics.txt` exists
- Run script from project root or use absolute paths

### Assistant responses are empty

- Verify your Assistant ID is correct
- Check that the assistant has system instructions configured
- Review thread/run IDs in `outputs.csv` on OpenAI dashboard

### Rate limit errors

- The script automatically retries with exponential backoff
- If persistent, consider adding delays between questions or upgrading API tier

## Development Notes

- **Synchronous:** Uses blocking API calls, no async complexity
- **Resume-Safe:** Matching on exact question text; change questions if needed
- **Minimal Dependencies:** Core functionality uses only `openai`, `python-dotenv`, `tenacity`
- **No Abstractions:** Single file, straightforward logic for easy debugging

## License

This project is provided as-is for batch processing health questions with OpenAI Assistants API.

---

**Questions or Issues?**

Check the OpenAI API documentation for Assistants: https://platform.openai.com/docs/assistants/overview
