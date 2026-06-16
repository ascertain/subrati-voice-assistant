"""
SUBRATI Voice Input - Vosk STT (offline, fast, CPU-friendly)
"""

import os
import sys
import json
import queue
import zipfile
import urllib.request
import sounddevice as sd
from vosk import Model, KaldiRecognizer

# Vosk model URL (small English model ~50MB)
VOSK_MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
VOSK_MODEL_DIR = "vosk-model"
VOSK_MODEL_NAME = "vosk-model-small-en-us-0.15"

audio_queue = queue.Queue()


def _download_model():
    """Download Vosk model if not present."""
    if os.path.exists(VOSK_MODEL_DIR):
        return

    print("⬇️  Downloading Vosk speech model (first time only, ~50MB)...")
    zip_path = "vosk-model.zip"

    urllib.request.urlretrieve(VOSK_MODEL_URL, zip_path)

    print("📦 Extracting model...")
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(".")

    # Rename extracted folder to standard name
    if os.path.exists(VOSK_MODEL_NAME):
        os.rename(VOSK_MODEL_NAME, VOSK_MODEL_DIR)

    os.remove(zip_path)
    print("✅ Model ready!")


def _audio_callback(indata, frames, time, status):
    """Callback for audio stream - pushes data to queue."""
    if status:
        print(f"  [Audio: {status}]", file=sys.stderr)
    audio_queue.put(bytes(indata))


def init_voice_input() -> tuple:
    """Initialize Vosk model and return (model, recognizer)."""
    _download_model()

    model = Model(VOSK_MODEL_DIR)
    recognizer = KaldiRecognizer(model, 16000)
    return model, recognizer


def listen(recognizer) -> str:
    """
    Listen for speech and return transcribed text.
    Blocks until speech is detected and a pause follows.
    """
    # Clear any old audio data
    while not audio_queue.empty():
        audio_queue.get()

    print("\n🎤 Listening... (speak now)")

    with sd.RawInputStream(
        samplerate=16000,
        blocksize=4000,
        dtype="int16",
        channels=1,
        callback=_audio_callback,
    ):
        while True:
            data = audio_queue.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").strip()
                if text:
                    print(f"   You said: \"{text}\"")
                    return text
