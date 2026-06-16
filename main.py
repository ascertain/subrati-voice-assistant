"""
🚀 SUBRATI - Cloud-First Voice Assistant
=========================================
Fast, free, lightweight voice AI.

Pipeline: Mic → Vosk STT → Smart Router → Groq/Gemini/HF → Edge TTS → Speaker

Usage:
    python main.py              # Full voice mode (speak + listen)
    python main.py --text       # Text-only mode (no mic/speaker)
    python main.py --stealth    # Stealth conversation coach mode
"""

import sys
import time
from voice_input import init_voice_input, listen
from voice_output import speak
from router import route_query, enhance_prompt
from llm_chain import get_response


EXIT_WORDS = ["exit", "quit", "stop", "goodbye", "bye", "shut down"]


def print_banner():
    print("""
╔══════════════════════════════════════════════╗
║         ⚡ SUBRATI Voice Assistant ⚡         ║
║                                              ║
║  Cloud-first • Fast • Free                   ║
║  Groq → Gemini → HuggingFace fallback        ║
║                                              ║
║  Commands:                                   ║
║    "speak"  → voice replies ON               ║
║    "silent" → text-only replies              ║
║    "exit"   → stop                           ║
╚══════════════════════════════════════════════╝
    """)


def run_voice_mode():
    """Main voice loop: listen → think → respond (speak or text)."""
    print_banner()

    print("🔧 Initializing voice engine...")
    model, recognizer = init_voice_input()
    print("✅ Ready! Speak to SUBRATI.\n")

    output_mode = "speak"  # Default: voice output
    speak("SUBRATI is ready. How can I help you?")

    while True:
        try:
            # Listen for user speech (waits for full sentence)
            user_text = listen(recognizer)

            if not user_text:
                continue

            text_lower = user_text.lower().strip()

            # Check for exit commands
            if any(word in text_lower for word in EXIT_WORDS):
                _respond("Goodbye! Have a great day.", output_mode)
                break

            # Check for mode switch commands
            if text_lower in ["speak", "speak mode", "voice", "voice mode"]:
                output_mode = "speak"
                _respond("Voice mode on.", output_mode)
                continue

            if any(w in text_lower for w in ["silent", "silent mode", "quietly", "text only", "text mode"]):
                output_mode = "silent"
                print("\n   📝 Switched to SILENT mode (text only on screen)\n")
                continue

            # Route and enhance the query
            mode = route_query(user_text)
            print(f"   [Mode: {mode} | Output: {'🔊' if output_mode == 'speak' else '📝'}]")

            enhanced = enhance_prompt(user_text, mode)

            # Get AI response
            print("   ⏳ Thinking...")
            start = time.time()
            response = get_response(enhanced)
            elapsed = time.time() - start
            print(f"   [Response in {elapsed:.1f}s]")

            # Respond in chosen mode
            _respond(response, output_mode)

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            _respond("Sorry, I encountered an error. Please try again.", output_mode)


def _respond(text: str, mode: str):
    """Output in voice or text-only based on mode."""
    if mode == "speak":
        speak(text)
    else:
        print(f"\n   🤖 SUBRATI: {text}\n")


def run_text_mode():
    """Text-only mode (no voice I/O) for testing."""
    print_banner()
    print("📝 Text mode (type your questions, 'exit' to quit)\n")

    while True:
        try:
            user_text = input("You: ").strip()

            if not user_text:
                continue

            if any(word in user_text.lower() for word in EXIT_WORDS):
                print("👋 Goodbye!")
                break

            mode = route_query(user_text)
            print(f"   [Mode: {mode}]")

            enhanced = enhance_prompt(user_text, mode)

            print("   ⏳ Thinking...")
            start = time.time()
            response = get_response(enhanced)
            elapsed = time.time() - start

            print(f"\n🤖 SUBRATI [{elapsed:.1f}s]: {response}\n")

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except EOFError:
            break


if __name__ == "__main__":
    if "--text" in sys.argv:
        run_text_mode()
    elif "--assistant" in sys.argv:
        run_voice_mode()
    else:
        # Default: stealth conversation listener
        from stealth_mode import run_stealth_mode
        run_stealth_mode()
