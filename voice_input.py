"""
SUBRATI Voice Input - Vosk STT (offline, fast, CPU-friendly)
With smart silence detection - waits for full sentences.
"""

import os
import sys
import json
import time
import queue
import zipfile
import urllib.request
import sounddevice as sd
from vosk import Model, KaldiRecognizer

# Vosk model URL (small English model ~50MB)
VOSK_MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
VOSK_MODEL_DIR = "vosk-model"
VOSK_MODEL_NAME = "vosk-model-small-en-us-0.15"

# Silence detection settings
SILENCE_TIMEOUT = 2.0       # Seconds of silence after speech to consider sentence done
PARTIAL_TIMEOUT = 3.0       # Max wait for more speech after a partial result

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


def _audio_callback(indata, frames, time_info, status):
    """Callback for audio stream - pushes data to queue."""
    if status:
        print(f"  [Audio: {status}]", file=sys.stderr)
    audio_queue.put(bytes(indata))


def init_voice_input() -> tuple:
    """Initialize Vosk model and return (model, recognizer)."""
    _download_model()

    model = Model(VOSK_MODEL_DIR)
    recognizer = KaldiRecognizer(model, 16000)
    recognizer.SetWords(True)
    return model, recognizer


def listen(recognizer, prompt="🎤 Listening... (speak now, pause when done)") -> str:
    """
    Listen for speech and return transcribed text.
    Waits for a full sentence - collects speech until a proper pause is detected.
    """
    # Clear any old audio data
    while not audio_queue.empty():
        audio_queue.get()

    print(f"\n{prompt}")

    collected_text = []
    last_speech_time = None
    speech_started = False

    with sd.RawInputStream(
        samplerate=16000,
        blocksize=4000,
        dtype="int16",
        channels=1,
        callback=_audio_callback,
    ):
        while True:
            try:
                data = audio_queue.get(timeout=0.5)
            except queue.Empty:
                # Check if we've been silent long enough after speech
                if speech_started and last_speech_time:
                    silence_duration = time.time() - last_speech_time
                    if silence_duration >= SILENCE_TIMEOUT:
                        break
                continue

            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").strip()
                if text:
                    collected_text.append(text)
                    last_speech_time = time.time()
                    speech_started = True
            else:
                # Check partial results to detect ongoing speech
                partial = json.loads(recognizer.PartialResult())
                partial_text = partial.get("partial", "").strip()
                if partial_text:
                    last_speech_time = time.time()
                    speech_started = True

            # If speech started, check silence timeout
            if speech_started and last_speech_time:
                silence_duration = time.time() - last_speech_time
                if silence_duration >= SILENCE_TIMEOUT and collected_text:
                    break

    # Get any remaining text from recognizer
    final = json.loads(recognizer.FinalResult())
    final_text = final.get("text", "").strip()
    if final_text:
        collected_text.append(final_text)

    full_text = " ".join(collected_text).strip()
    if full_text:
        print(f"   📝 Heard: \"{full_text}\"")
    return full_text


def listen_continuous(recognizer) -> str:
    """
    Continuous listening mode for conversation monitoring.
    Captures longer stretches of speech (both speakers).
    Returns text after a longer silence (4 seconds).
    """
    while not audio_queue.empty():
        audio_queue.get()

    collected_text = []
    last_speech_time = None
    speech_started = False
    long_silence = 4.0  # Wait longer in conversation mode

    with sd.RawInputStream(
        samplerate=16000,
        blocksize=4000,
        dtype="int16",
        channels=1,
        callback=_audio_callback,
    ):
        while True:
            try:
                data = audio_queue.get(timeout=0.5)
            except queue.Empty:
                if speech_started and last_speech_time:
                    if time.time() - last_speech_time >= long_silence:
                        break
                continue

            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").strip()
                if text:
                    collected_text.append(text)
                    last_speech_time = time.time()
                    speech_started = True
            else:
                partial = json.loads(recognizer.PartialResult())
                if partial.get("partial", "").strip():
                    last_speech_time = time.time()
                    speech_started = True

            if speech_started and last_speech_time:
                if time.time() - last_speech_time >= long_silence and collected_text:
                    break

    final = json.loads(recognizer.FinalResult())
    final_text = final.get("text", "").strip()
    if final_text:
        collected_text.append(final_text)

    return " ".join(collected_text).strip()
