"""
🚀 SUBRATI - Cloud-First Voice Assistant
=========================================
Fast, free, lightweight voice AI.

Pipeline: Mic → Vosk STT → Smart Router → Groq/Gemini/HF → Edge TTS → Speaker

Usage:
    python main.py          # Full voice mode
    python main.py --text   # Text-only mode (no mic/speaker)
"""

import sys
import time
from voice_input import init_voice_input, listen
from voice_output import speak
from router import route_query, enhance_prompt
from llm_chain import get_response


WAKE_WORDS = ["subrati", "hey subrati", "sub roti", "sub rati"]
EXIT_WORDS = ["exit", "quit", "stop", "goodbye", "bye", "shut down"]


def print_banner():
    print("""
╔══════════════════════════════════════════════╗
║         ⚡ SUBRATI Voice Assistant ⚡         ║
║                                              ║
║  Cloud-first • Fast • Free                   ║
║  Groq → Gemini → HuggingFace fallback        ║
║                                              ║
║  Say "exit" or "quit" to stop                ║
╚══════════════════════════════════════════════╝
    """)


def run_voice_mode():
    """Main voice loop: listen → think → speak."""
    print_banner()

    print("🔧 Initializing voice engine...")
    model, recognizer = init_voice_input()
    print("✅ Ready! Speak to SUBRATI.\n")

    speak("SUBRATI is ready. How can I help you?")

    while True:
        try:
            # Listen for user speech
            user_text = listen(recognizer)

            if not user_text:
                continue

            # Check for exit commands
            if any(word in user_text.lower() for word in EXIT_WORDS):
                speak("Goodbye! Have a great day.")
                break

            # Route and enhance the query
            mode = route_query(user_text)
            print(f"   [Mode: {mode}]")

            enhanced = enhance_prompt(user_text, mode)

            # Get AI response
            print("   ⏳ Thinking...")
            start = time.time()
            response = get_response(enhanced)
            elapsed = time.time() - start
            print(f"   [Response in {elapsed:.1f}s]")

            # Speak the response
            speak(response)

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            speak("Sorry, I encountered an error. Please try again.")


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
    else:
        run_voice_mode()
