# 🚀 SUBRATI - Cloud-First Voice Assistant

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Groq](https://img.shields.io/badge/LLM-Groq%20API-orange.svg)](https://groq.com)

> **A fast, free, lightweight voice AI assistant that runs on any PC.**  
> No GPU needed. No heavy local models. Just smart API routing.

---

## ⚡ Features

- 🎤 **Offline Speech Recognition** — Vosk STT runs locally on CPU (no internet needed for listening)
- 🔊 **Neural Text-to-Speech** — Edge TTS provides natural-sounding voices at zero cost
- 🧠 **Smart LLM Fallback Chain** — Groq → Gemini → HuggingFace (never stuck if one API is down)
- 🚀 **Sub-second AI Responses** — Groq delivers lightning-fast inference
- 🎯 **Intelligent Query Routing** — Automatically classifies chat/code/search queries
- 🔍 **Free Web Search** — DuckDuckGo integration for real-time information
- 💻 **Text Mode** — Test without microphone using `--text` flag
- 🆓 **100% Free** — All APIs have generous free tiers

---

## 🏗️ Architecture

```
🎤 Voice Input (Vosk - offline)
        ↓
   Smart Router (chat / code / search)
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
🔊 Edge TTS Output (neural voice)
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
# 🎤 Full voice mode (mic + speaker)
python main.py

# 📝 Text-only mode (no mic required, great for testing)
python main.py --text
```

---

## 📁 Project Structure

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

## 🎯 Smart Routing Modes

SUBRATI automatically detects your intent and routes accordingly:

| Mode | Trigger Keywords | What Happens |
|------|-----------------|--------------|
| **💬 Chat** | General questions, greetings | Direct LLM conversational response |
| **💻 Code** | "code", "function", "bug", "error", "python", "debug" | Technical coding-focused answers |
| **🔍 Search** | "latest", "news", "price", "weather", "today" | DuckDuckGo lookup + LLM summarization |

---

## 🤖 LLM Models Used

| Provider | Model | Use Case |
|----------|-------|----------|
| **Groq** | `llama-3.3-70b-versatile` | Primary - fastest inference |
| **Google** | `gemini-1.5-flash` | Fallback - reliable |
| **HuggingFace** | `Mistral-7B-Instruct-v0.2` | Last resort - always available |

---

## 🔊 Voice Configuration

### Available TTS Voices (Edge TTS)

Edit `EDGE_TTS_VOICE` in `config.py`:

| Voice | Language | Gender |
|-------|----------|--------|
| `en-US-GuyNeural` | English (US) | Male (default) |
| `en-US-JennyNeural` | English (US) | Female |
| `en-GB-SoniaNeural` | English (UK) | Female |
| `en-AU-NatashaNeural` | English (AU) | Female |
| `en-IN-NeerjaNeural` | English (India) | Female |

---

## 🛠️ Customization

### Change AI personality

Edit `SYSTEM_PROMPT` in `config.py`:

```python
SYSTEM_PROMPT = """You are SUBRATI, a fast and helpful voice assistant.
Keep responses concise and natural for spoken delivery."""
```

### Add new routing keywords

Edit `router.py` → `route_query()` function to add custom trigger words.

### Switch LLM models

Edit `config.py` to change `GROQ_MODEL`, `GEMINI_MODEL`, or `HF_MODEL`.

---

## 📝 First Run Notes

- On first launch in **voice mode**, SUBRATI automatically downloads a small Vosk speech model (~50MB). This only happens once.
- The `pygame` library is used for audio playback. If you hear no audio, ensure your system audio is working.
- Say **"exit"**, **"quit"**, or **"goodbye"** to stop the assistant.

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `No Groq API key` | Add your key to `.env` file |
| `400 Bad Request from Groq` | Model may be deprecated — check available models at Groq console |
| `No audio output` | Ensure `pygame` is installed and speakers are working |
| `Microphone not detected` | Check `sounddevice` can see your mic: `python -c "import sounddevice; print(sounddevice.query_devices())"` |
| `Vosk model download fails` | Manually download from https://alphacephei.com/vosk/models and extract to `vosk-model/` folder |

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `vosk` | Offline speech-to-text (CPU, fast) |
| `sounddevice` | Microphone audio capture |
| `edge-tts` | Free neural text-to-speech |
| `requests` | HTTP calls to LLM APIs |
| `python-dotenv` | Load `.env` configuration |
| `pygame` | Audio file playback |

---

## 🗺️ Roadmap

- [ ] Conversation history / memory
- [ ] Wake word detection ("Hey Subrati")
- [ ] Multi-language support
- [ ] Plugin system for custom commands
- [ ] GUI interface (optional)
- [ ] Streaming responses for faster perceived speed

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🙏 Acknowledgments

- [Groq](https://groq.com) — Lightning-fast free LLM inference
- [Vosk](https://alphacephei.com/vosk/) — Offline speech recognition
- [Edge TTS](https://github.com/rany2/edge-tts) — Free neural voices
- [DuckDuckGo](https://duckduckgo.com) — Free instant answer API

---

**Made with ⚡ by SUBRATI**
