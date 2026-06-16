# 🚀 SUBRATI - AI Voice Assistant & Stealth Conversation Coach

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Groq](https://img.shields.io/badge/LLM-Groq%20API-orange.svg)](https://groq.com)

> **A fast, free, AI-powered voice assistant with stealth conversation coaching, hotkey controls, auto-learning, and call summarization.**  
> No GPU needed. No heavy local models. Just smart API routing.

---

## ⚡ Features

- 🎤 **Offline Speech Recognition** — Vosk STT runs locally (no internet needed for listening)
- 🔊 **Neural Text-to-Speech** — Edge TTS (free, natural voices)
- 🧠 **Smart LLM Fallback Chain** — Groq → Gemini → HuggingFace (never stuck)
- 🚀 **Sub-second AI Responses** — Groq delivers lightning-fast inference
- 🕵️ **Stealth Conversation Coach** — Listens to conversations, auto-suggests replies silently
- ⌨️ **Hotkey Controls** — Arrow keys for capture/answer/learn/reset
- 📚 **Training System** — Teach SUBRATI your context, it learns and evolves
- 🤖 **Auto Question Detection** — Senses questions and suggests answers automatically
- 💡 **Out-of-Box Answers** — Helps even for topics not in training (general AI knowledge)
- 📋 **Call Summary & Actions** — Auto-generates meeting summaries with action items
- 🧪 **Self-Learning** — Remembers what worked, gets better over time
- 🆓 **100% Free** — All APIs have generous free tiers

---

## 🏗️ Architecture

```
🎤 Microphone (always listening)
        ↓
   Vosk STT (offline, on CPU)
        ↓
   ┌──────────────────────────────┐
   │     Smart Router             │
   │  ← Left Key = Capture       │
   │  → Right Key = Answer       │
   │  Auto-detect = Questions    │
   └──────────────────────────────┘
        ↓
 ┌───────────────────┐
 │   Groq API        │  ⚡ PRIMARY (sub-second, Llama 3.3 70B)
 └───────────────────┘
        ↓ (fallback)
 ┌───────────────────┐
 │   Gemini API      │  🥈 SECONDARY (Google AI free tier)
 └───────────────────┘
        ↓ (fallback)
 ┌───────────────────┐
 │  HuggingFace API  │  🥉 TERTIARY (Mistral 7B)
 └───────────────────┘
        ↓
 ┌───────────────────┐
 │  Training Context │  📚 Your prepared answers + learned patterns
 └───────────────────┘
        ↓
🔊 Edge TTS (voice) OR 📝 Screen (silent)
```

---

## 📋 Prerequisites

- **Python 3.10+** (tested with 3.13)
- **Windows 10/11** (also works on Linux/macOS)
- **Microphone** (for voice mode; not needed for text mode)
- **Internet connection** (for API calls and TTS)

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/subrati-voice-assistant.git
cd subrati-voice-assistant
```

### 2. Create virtual environment

```bash
python -m venv myenv

# Windows
myenv\Scripts\activate

# Linux/macOS
source myenv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Get your FREE API keys

| Service | Sign Up URL | Role | Speed |
|---------|-------------|------|-------|
| **Groq** | https://console.groq.com/keys | ⚡ Primary LLM | Sub-second |
| **Google AI** | https://aistudio.google.com/app/apikey | Backup LLM | Fast |
| **HuggingFace** | https://huggingface.co/settings/tokens | Last resort | Slower |

> 💡 **Minimum requirement**: Only the **Groq API key** is needed to get started. The others are optional fallbacks.

### 5. Configure API keys

```bash
# Copy the template
cp .env.example .env

# Edit .env and add your keys
# Windows: notepad .env
# Linux: nano .env
```

Your `.env` file should look like:
```env
GROQ_API_KEY=gsk_your_key_here
GEMINI_API_KEY=your_gemini_key_here
HF_API_KEY=hf_your_token_here
```

### 6. Run SUBRATI

```bash
# 🕵️ Stealth mode — conversation coach (DEFAULT)
python main.py

# 🎤 Voice assistant mode (ask questions, get spoken answers)
python main.py --assistant

# 📝 Text-only mode (keyboard, no mic)
python main.py --text

# 📋 Summarize last conversation
python summarize.py

# 📋 Summarize from a notes file
python summarize.py --file notes.txt
```

---

## 📁 Project Structure

```
subrati/
├── main.py              # Entry point (routes to modes)
├── stealth_mode.py      # 🕵️ Stealth conversation coach + hotkeys
├── summarize.py         # 📋 Call summary & action items generator
├── config.py            # Configuration, API keys, models
├── llm_chain.py         # LLM fallback chain (Groq → Gemini → HF)
├── router.py            # Smart query router + DuckDuckGo
├── voice_input.py       # Vosk STT (offline, smart silence detection)
├── voice_output.py      # Edge TTS (neural text-to-speech)
├── memory.py            # Learning system (loads training, saves patterns)
├── requirements.txt     # Python dependencies
├── .env.example         # API key template
├── .env                 # Your API keys (git-ignored)
├── .gitignore           # Git ignore rules
├── training/            # 📚 Training & learning data
│   ├── context.txt      # Your personal context (edit this!)
│   ├── interview_prep.txt  # Interview preparation context
│   ├── interview_qa.txt    # Full Q&A for all rounds
│   ├── memory.json      # Auto-saved conversation patterns
│   └── learnings.json   # Auto-evolved learnings
├── summaries/           # 📋 Generated call summaries (auto-created)
│   └── summary_*.txt    # One file per session
└── README.md            # This file
```
subrati/
├── main.py              # Main entry point & voice/text assistant loop
├── config.py            # Configuration, API keys, model settings
├── llm_chain.py         # LLM fallback chain (Groq → Gemini → HuggingFace)
├── router.py            # Smart query router + DuckDuckGo search
├── voice_input.py       # Vosk STT (offline speech-to-text)
├── voice_output.py      # Edge TTS (neural text-to-speech)
├── requirements.txt     # Python dependencies
├── .env.example         # API key template
├── .env                 # Your actual API keys (git-ignored)
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

---

## 🕵️ Stealth Conversation Coach (Main Feature)

The default mode. SUBRATI listens to conversations, detects questions, and suggests answers silently on screen.

### How It Works

1. **Start:** `python main.py`
2. **Listens** to everything being said (captures to screen)
3. **Auto-detects questions** → shows suggested answer silently
4. **Hotkeys** for manual control:

### ⌨️ Hotkey Controls

| Key | Action | Description |
|-----|--------|-------------|
| **← Left Arrow** | Start capture | Begin focused listening (capture the question) |
| **→ Right Arrow** | Answer NOW | Generate answer for captured/last question |
| **↑ Up Arrow** | Mark good | Tell SUBRATI this answer was helpful (learns) |
| **↓ Down Arrow** | Reset | Clear conversation history |

### Voice Commands

| Command | Action |
|---------|--------|
| "speak" | Switch to voice output 🔊 |
| "silent" | Switch to text-only (default) 📝 |
| "suggest" / "help me" | Force a suggestion |
| "summarize" / "wrap up" | Generate call summary + action items |
| "exit" | Stop (auto-saves summary + learns) |

### Three Ways to Get Answers

| Method | When | How |
|--------|------|-----|
| **Auto-detect** | Always | Senses questions, suggests automatically |
| **Hotkeys** | Manual control | ← to capture, → to answer |
| **Voice** | Quick trigger | Say "suggest" or "help me" |

### Out-of-Box Intelligence

- Question matches **training** → uses prepared answer (adapted naturally)
- Question is **new/unknown** → answers from general AI knowledge
- **Never stuck** — helps with anything

---

## 📚 Training System

### 1. Initial Training (you write)

Edit `training/context.txt`:
```text
## About Me
- Name: John
- Communication style: direct, uses examples

## Rules
- Keep answers simple
- Use real-world examples from my work
```

### 2. Prepared Q&A

Add any `.txt` file in `training/` with Q&A pairs — SUBRATI loads them all.

### 3. Self-Learning (automatic)

- **Press ↑ Up** after a good suggestion → saves to memory
- **On exit** → analyzes conversation, extracts learnings
- **Next session** → uses learnings for better answers

---

## 📋 Call Summary & Action Items

After any conversation, SUBRATI generates:
- Summary of discussion
- Key decisions made
- Action items with owners
- Follow-up needed

**Trigger:** Say "summarize" during a call, or run `python summarize.py` after.  
**Auto-save:** Summaries saved to `summaries/` on exit.

---

## 🎯 Smart Routing (Assistant Mode)

| Mode | Trigger Keywords | What Happens |
|------|-----------------|--------------|
| **💬 Chat** | General questions | LLM response |
| **💻 Code** | "code", "function", "bug", "error" | Technical answers |
| **🔍 Search** | "latest", "news", "price", "weather" | DuckDuckGo + LLM |

---

## 🤖 LLM Models

| Provider | Model | Speed |
|----------|-------|-------|
| **Groq** | `llama-3.3-70b-versatile` | ⚡ Sub-second |
| **Google** | `gemini-1.5-flash` | Fast |
| **HuggingFace** | `Mistral-7B-Instruct-v0.2` | Slower |

---

## 🔊 TTS Voices

Edit `EDGE_TTS_VOICE` in `config.py`:

| Voice | Language |
|-------|----------|
| `en-US-GuyNeural` | English US Male (default) |
| `en-US-JennyNeural` | English US Female |
| `en-GB-SoniaNeural` | English UK Female |
| `en-IN-NeerjaNeural` | English India Female |

---

## 📝 First Run

- Downloads Vosk model (~50MB) — one time only
- Hotkeys need terminal window focused
- Summaries auto-saved to `summaries/`

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| No Groq API key | Add key to `.env` file |
| 400 from Groq | Update `GROQ_MODEL` in config.py |
| No audio | Check pygame + speakers |
| No mic detected | `python -c "import sounddevice; print(sounddevice.query_devices())"` |
| Vosk download fails | Manual download from https://alphacephei.com/vosk/models |
| Hotkeys not working | Ensure terminal is focused, pynput installed |
| Training not loading | Check `.txt` files exist in `training/` |

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `vosk` | Offline speech-to-text |
| `sounddevice` | Microphone capture |
| `edge-tts` | Neural TTS |
| `requests` | API calls |
| `python-dotenv` | .env config |
| `pygame` | Audio playback |
| `pynput` | Keyboard hotkeys |

---

## 🤝 Contributing

1. Fork the repo
2. Create feature branch: `git checkout -b feature/my-feature`
3. Commit: `git commit -m 'Add feature'`
4. Push: `git push origin feature/my-feature`
5. Open Pull Request

---

## 📄 License

MIT License — free to use, modify, distribute.

---

**Made with ⚡ by SUBRATI**
