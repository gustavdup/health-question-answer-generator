# Health Question Answer Generator

An interactive Python batch processor that generates answers to structured health questions using the OpenAI Assistants API. Select from 8 health topics, process questions with context-aware prompts, and get timestamped CSV outputs with full tracking.

## Features

- ✅ **Interactive file selector** - Choose which topic to process from a menu
- ✅ **8 health topics** - Energy, Sleep, Stress, Nutrition, Hormones, Illness, Immunity, Mental Health
- ✅ **Context-aware prompts** - Gender, care focus (Myself/Kids/Family), and parental status
- ✅ **OpenAI Assistants API** - Threaded conversations with automatic polling
- ✅ **Resume-safe** - Skip already processed questions automatically
- ✅ **Timestamped outputs** - Each run creates a unique CSV in `outputs/` folder
- ✅ **Error handling** - Exponential backoff retry logic for rate limits
- ✅ **Full tracking** - CSV includes prompt, response, thread_id, run_id, and status
- ✅ **Random test generator** - Create test files with diverse question samples

## Project Structure

```
health-question-answer-generator/
├── src/
│   ├── __init__.py              # Makes src a Python package
│   ├── generate_answers.py     # Main entry point - interactive file selector
│   ├── run_batch.py             # Core batch processing engine
│   ├── create_random_test.py   # Generate random test files
│   ├── clean_topics.py          # Utility to clean question numbering
│   └── normalize_topics.py      # Utility to normalize file spacing
├── data/
│   ├── 1_energy_fatigue.txt     # Topic 1: Energy & Fatigue questions
│   ├── 2_sleep_recovery.txt     # Topic 2: Sleep & Recovery questions
│   ├── 3_stress_anxiety.txt     # Topic 3: Stress & Anxiety questions
│   ├── 4_nutrition_eating.txt   # Topic 4: Nutrition & Eating questions
│   ├── 5_hormones_balance.txt   # Topic 5: Hormones & Balance questions
│   ├── 6_illness_symptoms.txt   # Topic 6: Illness & Symptoms questions
│   ├── 7_immunity_prevention.txt # Topic 7: Immunity & Prevention questions
│   ├── 8_mental_health_mood.txt # Topic 8: Mental Health & Mood questions
│   └── 10_random_test.txt       # Random test file (1 Q per topic)
├── outputs/                     # Generated CSV files with timestamps
├── .env.example                 # Template for environment variables
├── .env                         # Your credentials (create from .env.example)
├── .gitignore                   # Git ignore rules
├── requirements.txt             # Python dependencies
├── setup.sh                     # Setup script for macOS/Linux
├── setup.bat                    # Setup script for Windows
└── README.md                    # This file
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

1. **Menu displays** all topic files in `data/` (numbered 1-10)
2. **You select** a file by typing its number
3. **Script processes** all questions in that file:
   - Parses questions with their context (topic, gender, care focus, has kids)
   - Checks for already-processed questions (resume capability)
   - Creates a new OpenAI thread for each question
   - Sends context-aware prompt to the assistant
   - Polls the run until completed (max 5 minutes)
   - Extracts and saves the response
4. **Progress updates** show "Processing i of N" with status
5. **Output saved** to `outputs/` with format: `filename_timestamp.csv`

**Example:** Select `1_energy_fatigue.txt` → Output: `outputs/1_energy_fatigue_1729702345.csv`

### Resume Capability

If the script is interrupted or you rerun the same file, simply execute:

```bash
python src/generate_answers.py
```

Select the same file number, and the script will automatically skip questions already present in the corresponding output file (matched by exact question text).

## Additional Tools

### Generate Random Test File

Create a test file with one random question from each of the 8 main topics:

```bash
python -m src.create_random_test
```

This creates `data/10_random_test.txt` with diverse gender and context combinations.

### Clean Topic Files

Remove leading numbers from questions:

```bash
python src/clean_topics.py
```

## Input Format

The topic files in `data/` follow a specific structure with repeating sections:

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

For each question, the script builds a context-aware prompt:

```
Context:
• Topic: [topic name]
• Gender: [Female | Male | Gender Neutral]
• Care focus: [Myself | My Kids | My Family]
• Has kids: [Yes | No]
• Inferred role: [mother | father | parent | individual]

Write a short, calm, and reassuring message addressed to the person, as Dr Gabi. 
Assume you already have a trusted relationship with them.

Your response should:
• Start with one brief empathetic sentence or two that acknowledges their situation.
• Follow with 2–3 short bullet points (each under one line) explaining how you can help in their context.
• End with one short reflective statement that leaves the user feeling hopeful and intrigued.
• Never ask the user a question as they can't respond at this stage.

Keep it under 150 words total, but lean towards 100 where possible.
Tone: warm, supportive, and conversational, never promotional or overly detailed.
Reference their role when helpful (e.g., "as a mother", "for your family").

User Question:
[exact question text]
```

The assistant should have system instructions; this prompt provides per-question context.

## Output Format

Results are saved to `outputs/filename_timestamp.csv` with the following columns:

| Column | Description |
|--------|-------------|
| `topic` | The topic name (e.g., "Energy & Fatigue") |
| `gender` | Female, Male, or Gender Neutral |
| `care_focus` | Myself, My Kids, or My Family |
| `has_kids` | Yes or No |
| `role` | mother, father, parent, or individual |
| `prompt` | The full prompt sent to the assistant |
| `question` | The exact question text |
| `response` | The assistant's text response |
| `thread_id` | OpenAI thread ID for debugging |
| `run_id` | OpenAI run ID for debugging |
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

### "INPUT_FILE and OUTPUT_FILE must be set"

- Don't run `run_batch.py` directly
- Use `generate_answers.py` as the entry point instead

### Assistant responses are empty

- Verify your Assistant ID is correct
- Check that the assistant has system instructions configured
- Review thread/run IDs in `outputs.csv` on OpenAI dashboard

### Rate limit errors

- The script automatically retries with exponential backoff
- If persistent, consider adding delays between questions or upgrading API tier

## Development Notes

- **Synchronous:** Uses blocking API calls, no async complexity
- **Resume-Safe:** Matching on exact question text in output CSV
- **Modular:** `generate_answers.py` is the entry point, `run_batch.py` is the engine
- **Multiple topics per file:** Parser supports multiple "Topic X:" sections in one file
- **Minimal Dependencies:** Core uses `openai`, `python-dotenv`, `tenacity`
- **Clean Output:** Each run creates a timestamped CSV in `outputs/` folder

## License

This project is provided as-is for batch processing health questions with OpenAI Assistants API.

---

**Questions or Issues?**

Check the OpenAI API documentation for Assistants: https://platform.openai.com/docs/assistants/overview
