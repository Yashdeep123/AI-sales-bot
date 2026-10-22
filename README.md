# AI Sales Voice Bot

An interactive voice sales bot built with Python and Flask. The bot handles sales calls, asks qualifying discovery questions, pitches products based on customer pain points, handles objections, records call audio with consent, and generates post-call summaries with automatic sales status classification.

---

## Features

- **Interactive Voice Calls**: Real-time speech-to-text (STT) and text-to-speech (TTS) with live waveform animation.
- **Consultative Sales Dialogue**: Follows structured sales methodology—discovers customer bottlenecks, handles objections (pricing, competitors, timing, authority), and guides prospects to book a live demo or assessment.
- **Needs-Based Pitching**: Adapts responses to stated pain points (e.g. infrastructure cost reduction, high availability/downtime, Generative AI on Bedrock, security and compliance).
- **Multilingual Support**: Supports English, Hindi (`hi-IN`), and Telugu (`te-IN`).
- **2-Way Call Audio Recording**: Captures both customer speech and bot audio into playable `.webm` files with inline player and download option.
- **Post-Call Intelligence & Summarization**: Automatically extracts overview summary, customer requirements, objections raised, and concrete next steps.
- **Sales Status Classification**: Assigns one of 6 statuses:
  - `Converted`
  - `Interested`
  - `Follow-up Required`
  - `Not Interested`
  - `Demo Requested`
  - `No Response`
- **Call History**: Stores calls in a persistent JSON database (`data/calls.json`) with search and status filtering.

---

## Tech Stack

- **Backend**: Python 3, Flask
- **Frontend**: Vanilla HTML5, CSS3, ES6 JavaScript (Web Speech API, Web Audio API, MediaRecorder)
- **AI / LLM Integration**: Rule-based fallback state machine with optional OpenAI `gpt-4o-mini` support

---

## Getting Started

### 1. Prerequisites
- Python 3.9+
- A modern browser with microphone permissions (Chrome, Edge, Brave)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Setup (Optional)
If you want to use OpenAI for live completions instead of the rule engine:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```
*(The bot functions out-of-the-box without an API key using the built-in conversational engine).*

### 4. Run the Application
```bash
python3 app.py
```
Open your browser at `http://127.0.0.1:8000`.

---

## Testing

Run unit tests and conversation simulations:

```bash
# Run AWS sales bot test suite (28 tests)
python3 -m unittest test_aws_sales_bot.py

# Run expert sales behavior and guidelines test suite (19 tests)
python3 -m unittest test_expert_sales_bot.py

# Run full multi-turn offline simulation across 5 personas
python3 run_sales_bot_simulation.py
```

---

## Project Structure

```
.
├── app.py                     # Flask web app and REST endpoints
├── products.py                # Product catalog, pricing, and objection playbooks
├── sales_agent.py             # Sales dialogue engine and response logic
├── summarizer.py              # Post-call summarizer and 6-status classifier
├── requirements.txt           # Python dependencies
├── data/
│   └── calls.json             # Saved call records and transcripts
├── recordings/                # Recorded audio files (.webm)
├── templates/
│   └── index.html             # Web UI template
├── static/
│   ├── css/style.css          # UI styles
│   └── js/main.js             # Voice recognition, TTS, and call handling
├── test_aws_sales_bot.py      # Catalog, API, and objection tests
├── test_expert_sales_bot.py   # Discovery, needs-based, and polite tone tests
└── run_sales_bot_simulation.py# Multi-turn offline persona simulator
```
