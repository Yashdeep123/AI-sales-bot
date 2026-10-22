# NexusVoice AI Sales Bot 🎙️🤖

> **Intern Assignment Submission for Sankar Group**  
> An interactive, production-ready AI Voice Sales Bot built in Python that conducts voice sales conversations for SaaS products, displays live chat transcripts in real time, records 2-way call audio with consent, generates an executive AI summary with objections and next steps, automatically assigns sales statuses, and maintains a complete call history.

---

## 🚀 Key Features & Assignment Compliance

| Requirement | Implementation Detail | Status |
| :--- | :--- | :---: |
| **1. Voice Conversation** | Autonomous sales bot with natural speech synthesis (TTS), speech-to-text (STT), value proposition pitching, lead qualification, and objection handling. | ✅ Complete |
| **2. Multi-Language** | Full conversational support in **English**, **Hindi (हिन्दी)**, and **Telugu (తెలుగు)** with native voice synthesis and recognition. | ✅ Complete |
| **3. Live Chat Screen** | Real-time chat stream with avatar indicators, live speech/typing animation, and synchronized transcript generation. | ✅ Complete |
| **4. Call Controls** | **Start Call**, **End Call**, **Mute/Unmute Mic**, live duration counter (`00:00`), and real-time status pill (`Ready`, `Connecting`, `AI Speaking`, `Listening`, `Call Ended`). | ✅ Complete |
| **5. Call Recording & Playback** | Pre-call recording consent prompt; Web Audio API + MediaRecorder 2-way call audio capture into playable `.webm` audio with scrubber and download button. | ✅ Complete |
| **6. AI Summary** | Post-call analysis automatically extracts: **Overview Summary**, **Customer Requirements**, **Objections Raised**, and **Actionable Next Steps**. | ✅ Complete |
| **7. Sales Status Classification** | Deterministic & LLM-backed classification strictly into one of the 6 required categories: `Converted`, `Interested`, `Follow-up Required`, `Not Interested`, `Demo Requested`, `No Response`. | ✅ Complete |
| **8. Call History** | Persistent server-side storage (`data/calls.json`) with inline audio player, search, status filter, and transcript review drawer. | ✅ Complete |

---

## 🛠️ Architecture & Technology Stack

- **Backend**: Python 3, Flask REST API
- **Frontend**: Modern Vanilla HTML5, CSS3, ES6+ JavaScript
- **Design System**: High-aesthetic glassmorphism, dynamic audio canvas waveform, responsive dark theme
- **Speech Stack**:
  - **Speech-to-Text**: Web Speech API (`webkitSpeechRecognition` / `SpeechRecognition`)
  - **Text-to-Speech**: Browser `SpeechSynthesis` with localized language voices (`en-US`, `hi-IN`, `te-IN`)
  - **Audio Recording**: Web Audio API (`AudioContext`) merging microphone input and bot speech into a unified `MediaRecorder` stream (`audio/webm`)
- **AI Intelligence**:
  - Built-in conversational state machine & sales objection handler (Zero external API keys required to test).
  - Optional OpenAI / Gemini LLM proxy support (configurable via the UI Settings modal).

---

## 🏃 Quick Start (Local Setup)

### 1. Prerequisites
- Python 3.9+
- A modern web browser with microphone support (Google Chrome, Microsoft Edge, or Brave recommended)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python3 app.py
```

### 4. Open in Browser
Navigate to:
```
http://127.0.0.1:8000
```

---

## 🌐 Live Website Deployment Options

To submit a **Working Website Link**:

### Option A: Free 1-Click Deployment to Render (Recommended)
1. Push this repository to your GitHub account.
2. Go to [Render.com](https://render.com) and click **New Web Service**.
3. Connect your GitHub repository.
4. Settings:
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python3 app.py`
5. Click **Deploy Web Service** to receive your live `https://<your-app>.onrender.com` link.

### Option B: Instant Public URL via Ngrok or Localtunnel (Testing)
```bash
# Using ngrok:
ngrok http 8000

# OR using localtunnel (no account needed):
npx localtunnel --port 8000
```
This generates a live public HTTPS link instantly.

---

## 📹 Video Walkthrough Guide (Suggested 2-Minute Script)

When recording your submission explanation video, follow this flow:
1. **Introduction (15 sec)**:
   - Introduce yourself and state the project: *AI Voice Sales Bot for SaaS products*.
   - Point out the active SaaS product (*NexusPulse AI*), pricing tiers, and language selector (English, Hindi, Telugu).
2. **Starting the Call & Consent (20 sec)**:
   - Click **Start Call**.
   - Highlight the **Call Recording Consent Modal** with privacy disclosure.
   - Accept consent: show call duration timer starting and canvas waveform activating.
3. **Interactive Voice Conversation (45 sec)**:
   - Speak into your microphone (or click the quick simulation chips):
     - *Customer*: *"Hi, can you explain what it does and what it costs?"*
     - *Bot*: Responds with pricing ($99 Starter, $299 Growth) and benefits.
     - *Customer*: *"That sounds a bit too expensive for our budget."*
     - *Bot*: Gracefully handles the objection highlighting 4x ROI and the 14-day risk-free trial.
     - *Customer*: *"I'd love to book a 15-minute live demo!"*
     - *Bot*: Confirms live demo scheduling.
   - Notice the **Live Chat Screen** updating with speech indicators, avatars, and timestamps in real time.
4. **Ending the Call & AI Summary (30 sec)**:
   - Click **End Call**.
   - Show the **Post-Call AI Intelligence Modal**:
     - Point out the **Automated Sales Status** badge (`Demo Requested`).
     - Play back the **Call Voice Recording** using the inline player and show the **Download** button.
     - Highlight the **Executive Summary**, **Customer Requirements**, **Objections Raised**, and **Next Steps**.
5. **Call History (10 sec)**:
   - Click **Call History** to display previous calls, audio players, search, and status filters.

---

## 📂 Project Directory Structure

```
AI voice bot/
├── app.py                # Main Flask application and REST endpoints
├── products.py           # SaaS product catalog, value props, and objection playbooks
├── sales_agent.py        # Conversational dialogue engine & multi-language prompts
├── summarizer.py         # AI Call Summarizer & 6-status classification engine
├── requirements.txt      # Python dependencies
├── data/
│   └── calls.json        # Persistent JSON database of all call records
├── recordings/           # Directory where 2-way call audio files (.webm) are saved
├── templates/
│   └── index.html        # Main web UI template
├── static/
│   ├── css/
│   │   └── style.css     # Glassmorphic dark theme stylesheet
│   └── js/
│       └── main.js       # Web Speech, Web Audio, and client state engine
└── README.md             # Documentation & submission guide
```

---

## 🏆 Assessment Criteria Check

- [x] **Voice Conversation**: Real interactive voice agent selling SaaS products.
- [x] **Language Support**: English, Hindi, and Telugu.
- [x] **Live Chat Screen**: Simultaneous live message display.
- [x] **Call Controls**: Start, End, Mute, Duration timer, and status.
- [x] **Call Recording**: 2-way recording with explicit consent prompt and playback.
- [x] **AI Summary**: Short summary, requirements, objections, next steps.
- [x] **Sales Status**: Exact 6 assigned statuses with colored badges.
- [x] **Call History**: Complete persistent log with inline playback and summaries.
# AI-sales-bot
