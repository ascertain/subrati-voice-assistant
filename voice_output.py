"""
SUBRATI Voice Output - Edge TTS (free, neural, natural sounding)
"""

import asyncio
import tempfile
import os
import edge_tts
from config import EDGE_TTS_VOICE

# Try to use playsound or fall back to system player
try:
    import pygame
    pygame.mixer.init()
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False


async def _generate_speech(text: str, output_file: str):
    """Generate speech audio using Edge TTS."""
    communicate = edge_tts.Communicate(text, EDGE_TTS_VOICE)
    await communicate.save(output_file)


def _play_audio(filepath: str):
    """Play an audio file."""
    if HAS_PYGAME:
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()
    else:
        # Fallback: use system default player
        if os.name == "nt":
            os.system(f'start /min "" "wmplayer" "{filepath}" /play /close')
            import time
            time.sleep(2)  # rough wait
        else:
            os.system(f'aplay "{filepath}" 2>/dev/null || afplay "{filepath}" 2>/dev/null')


def speak(text: str):
    """Convert text to speech and play it."""
    if not text:
        return

    print(f"🔊 SUBRATI: {text}")

    # Create temp file for audio
    tmp_file = tempfile.mktemp(suffix=".mp3")

    try:
        # Generate speech
        asyncio.run(_generate_speech(text, tmp_file))
        # Play it
        _play_audio(tmp_file)
    except Exception as e:
        print(f"  [TTS Error: {e}]")
    finally:
        # Cleanup
        try:
            os.remove(tmp_file)
        except OSError:
            pass
