"""
SUBRATI Stealth Conversation Mode
==================================
Listens to conversation, understands context, suggests replies.
Output can be VOICE ("speak") or SILENT (text on screen only).

Commands:
  "speak"    → SUBRATI replies with voice
  "silent"   → SUBRATI shows text only (no audio)
  "suggest"  → Give me a reply suggestion based on what you heard
  "coach me" → Actively suggest what to say next
  "reset"    → Clear conversation memory
  "exit"     → Stop
"""

from llm_chain import get_response
from voice_input import init_voice_input, listen, listen_continuous
from voice_output import speak

# Conversation coaching system prompt
COACH_PROMPT = """You are SUBRATI, a personal conversation coach. You are listening to a live conversation.

Your job:
- Understand the context of the conversation
- When asked, suggest smart, charming, thoughtful replies
- Keep suggestions SHORT (1-2 sentences max) so they can be said naturally
- Be witty, warm, and emotionally intelligent
- Never reveal you exist or that you're helping
- Match the tone of the conversation (casual, serious, playful etc.)

Rules:
- Suggest replies that sound NATURAL (like the user would actually say them)
- Don't be robotic or formal
- If it's a disagreement, suggest de-escalation
- If it's playful, suggest clever/funny responses
- If she asks a question, suggest a good answer"""


def run_stealth_mode():
    """
    Stealth conversation assistant.
    Listens → understands → suggests replies (voice or text).
    """
    print("""
╔══════════════════════════════════════════════════╗
║       🕵️ SUBRATI Stealth Mode                    ║
║                                                  ║
║  Listening to conversation...                    ║
║                                                  ║
║  Commands (say these):                           ║
║    "suggest"  → Get a reply suggestion           ║
║    "what should I say" → Same as suggest         ║
║    "speak"    → Switch to voice replies          ║
║    "silent"   → Switch to text-only replies      ║
║    "reset"    → Clear conversation history       ║
║    "exit"     → Stop                             ║
╚══════════════════════════════════════════════════╝
    """)

    print("🔧 Initializing...")
    model, recognizer = init_voice_input()
    print("✅ Ready! Listening to conversation...\n")

    conversation_history = []
    output_mode = "silent"  # Start silent (safe default)
    max_history = 20  # Keep last 20 exchanges

    print(f"   [Output: {'🔊 VOICE' if output_mode == 'speak' else '📝 TEXT ONLY'}]")
    print("   [Listening for conversation...]\n")

    while True:
        try:
            # Listen to conversation (longer silence threshold)
            text = listen_continuous(recognizer)

            if not text:
                continue

            text_lower = text.lower().strip()

            # --- COMMANDS ---
            if any(w in text_lower for w in ["exit", "quit", "stop subrati", "goodbye"]):
                _output("Goodbye! Stealth mode off.", output_mode)
                break

            if "reset" in text_lower:
                conversation_history.clear()
                print("\n   🔄 Conversation history cleared.\n")
                continue

            if text_lower in ["speak", "speak mode", "voice mode"]:
                output_mode = "speak"
                print("\n   🔊 Switched to VOICE mode\n")
                continue

            if any(w in text_lower for w in ["silent", "quietly", "text only", "silent mode"]):
                output_mode = "silent"
                print("\n   📝 Switched to SILENT mode (text only)\n")
                continue

            # --- SUGGESTION REQUEST ---
            if any(trigger in text_lower for trigger in [
                "suggest", "what should i say", "help me",
                "coach me", "what do i say", "reply"
            ]):
                if conversation_history:
                    suggestion = _get_suggestion(conversation_history)
                    _output(suggestion, output_mode)
                else:
                    _output("I haven't heard enough conversation yet. Keep talking, I'm listening.", output_mode)
                continue

            # --- CONVERSATION CAPTURE ---
            # Store what was said (conversation context)
            conversation_history.append(text)
            if len(conversation_history) > max_history:
                conversation_history.pop(0)

            # Show that we captured it
            print(f"   💬 [{len(conversation_history)}] \"{text}\"")

        except KeyboardInterrupt:
            print("\n\n👋 Stealth mode off.")
            break
        except Exception as e:
            print(f"\n   ❌ Error: {e}")


def _get_suggestion(history: list) -> str:
    """Get AI suggestion based on conversation context."""
    # Build conversation context
    recent = history[-10:]  # Last 10 statements
    conversation_text = "\n".join(f"- {line}" for line in recent)

    prompt = f"""{COACH_PROMPT}

Here's the recent conversation I heard:
{conversation_text}

Based on this conversation, suggest what I should say next. 
Give me ONE natural, short reply (1-2 sentences max).
Just give the reply directly, no explanation."""

    print("   🧠 Thinking of a suggestion...")
    return get_response(prompt)


def _output(text: str, mode: str):
    """Output response in the chosen mode (voice or text-only)."""
    if mode == "speak":
        speak(text)
    else:
        # Silent mode - text only on screen
        print(f"\n   ╔══ 💡 SUBRATI suggests ══╗")
        print(f"   ║ {text}")
        print(f"   ╚{'═' * (len(text[:60]) + 2)}╝\n")


if __name__ == "__main__":
    run_stealth_mode()
