import os
from dotenv import load_dotenv

load_dotenv()

# API Keys - set these in .env file
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
HF_API_KEY = os.getenv("HF_API_KEY", "")

# Model settings
GROQ_MODEL = "llama-3.3-70b-versatile"
GEMINI_MODEL = "gemini-1.5-flash"
HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

# Voice settings
VOSK_MODEL_PATH = "vosk-model"  # Will be downloaded on first run
EDGE_TTS_VOICE = "en-US-GuyNeural"  # Fast natural male voice
# Alternatives: "en-US-JennyNeural", "en-GB-SoniaNeural"

# System prompt
SYSTEM_PROMPT = """You are SUBRATI, a fast and helpful voice assistant. 
Keep responses concise and natural for spoken delivery (2-4 sentences max unless asked for detail).
Be direct and informative."""
