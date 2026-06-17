"""
SUBRATI Stealth Conversation Mode
==================================
Listens to conversation, detects questions, auto-suggests replies.
Learns and evolves from every conversation.

HOTKEYS:
  ← Left Arrow  → Start focused listening (capturing question)
  → Right Arrow → Generate answer NOW
  ↑ Up Arrow    → Mark last answer as good (learns)
  ↓ Down Arrow  → Clear/reset conversation

AUTO MODE:
  Even without hotkeys, SUBRATI auto-detects questions and suggests.

Voice commands:
  "speak"      → voice replies ON
  "silent"     → text-only replies
  "exit"       → stop
"""

import threading
from pynput import keyboard

from llm_chain import get_response
from voice_input import init_voice_input, listen, listen_continuous
from voice_output import speak
from memory import (
    load_training_context, load_memory, get_memory_context,
    detect_question, record_session, record_good_response,
    evolve_from_conversation
)


# --- HOTKEY STATE ---
class HotkeyState:
    """Thread-safe hotkey state shared between keyboard listener and main loop."""
    def __init__(self):
        self.focused_listening = False   # Left arrow pressed = capture question
        self.answer_now = False          # Right arrow pressed = generate answer
        self.mark_good = False           # Up arrow = mark good
        self.reset_conv = False          # Down arrow = reset

hotkey_state = HotkeyState()


def _on_key_press(key):
    """Handle hotkey presses (runs in background thread)."""
    global hotkey_state
    try:
        if key == keyboard.Key.left:
            hotkey_state.focused_listening = True
            print("\n   ⏺️  FOCUSED LISTENING — capturing question...")
        elif key == keyboard.Key.right:
            hotkey_state.answer_now = True
            print("\n   ▶️  GENERATING ANSWER...")
        elif key == keyboard.Key.up:
            hotkey_state.mark_good = True
        elif key == keyboard.Key.down:
            hotkey_state.reset_conv = True
    except AttributeError:
        pass


def _build_system_prompt(training_context: str, memory_context: str) -> str:
    """Build the full system prompt from training + memory."""
    return f"""You are SUBRATI, a hidden interview/conversation coach running in stealth mode.
You hear a live conversation and help with smart, relevant answers.

CONTEXT & TRAINING:
{training_context}

LEARNED PATTERNS:
{memory_context}

CRITICAL RULES:
- If the question matches your training material, use that answer but adapt naturally.
- If the question is NOT in your training, answer from general knowledge — be helpful anyway.
- Give ONLY the answer. No labels, no "you could say", no explanations.
- For interview questions: be structured, concise, and use IKEA/real examples.
- For technical questions: include code snippets if relevant.
- For general questions: be direct and informative.
- Keep answers spoken-length: 3-5 sentences for interviews, 1-2 for casual.
- Sound like the user speaking, not an AI."""


def run_stealth_mode():
    """
    Stealth conversation assistant with hotkey support.
    
    Hotkeys:
      ← Left:  Start focused capture (question)
      → Right: Trigger answer generation
      ↑ Up:    Mark last suggestion as good
      ↓ Down:  Reset conversation
      
    Also auto-detects questions without hotkeys.
    """
    global hotkey_state

    print("""
╔══════════════════════════════════════════════════════╗
║       🕵️ SUBRATI - Stealth Interview Coach           ║
║                                                      ║
║  HOTKEYS:                                            ║
║    ← Left Arrow  = Start capturing question          ║
║    → Right Arrow = Answer NOW                        ║
║    ↑ Up Arrow    = Mark last answer as good          ║
║    ↓ Down Arrow  = Reset conversation                ║
║                                                      ║
║  AUTO: Also detects questions automatically          ║
║  Say "speak" for voice / "silent" for text           ║
║  Say "exit" to stop                                  ║
╚══════════════════════════════════════════════════════╝
    """)

    print("🔧 Initializing...")
    model, recognizer = init_voice_input()

    # Load training context & memory
    training_context = load_training_context()
    memory_context = get_memory_context()

    if training_context:
        print(f"📚 Training loaded ({len(training_context)} chars of context)")
    else:
        print("⚠️  No training context. Edit training/context.txt to personalize.")

    # Start keyboard listener (background thread)
    kb_listener = keyboard.Listener(on_press=_on_key_press)
    kb_listener.daemon = True
    kb_listener.start()
    print("⌨️  Hotkeys active (←=capture, →=answer, ↑=good, ↓=reset)")

    print("✅ Listening now...\n")

    conversation_history = []
    suggestions_given = []
    last_suggestion = ""
    last_question = ""
    output_mode = "silent"
    max_history = 30
    focused_capture = []  # Buffer for focused listening mode

    while True:
        try:
            # --- CHECK HOTKEY STATES ---
            
            # Up arrow: mark good
            if hotkey_state.mark_good:
                hotkey_state.mark_good = False
                if last_suggestion and last_question:
                    record_good_response(last_question, last_suggestion)
                    print("   ✅ Learned! Saved as good response.\n")
                continue

            # Down arrow: reset
            if hotkey_state.reset_conv:
                hotkey_state.reset_conv = False
                conversation_history.clear()
                focused_capture.clear()
                suggestions_given.clear()
                print("   🔄 Conversation cleared.\n")
                continue

            # Right arrow: answer NOW with whatever we have
            if hotkey_state.answer_now:
                hotkey_state.answer_now = False
                hotkey_state.focused_listening = False
                
                # Use focused capture if available, else last conversation
                if focused_capture:
                    question_text = " ".join(focused_capture)
                    focused_capture.clear()
                elif conversation_history:
                    question_text = conversation_history[-1]
                else:
                    print("   ⚠️  Nothing captured yet. Speak first.")
                    continue
                
                print(f"   🎯 Answering: \"{question_text[:80]}...\"")
                suggestion = _get_answer(
                    question_text, conversation_history,
                    training_context, memory_context
                )
                last_suggestion = suggestion
                last_question = question_text
                suggestions_given.append(suggestion)
                _output(suggestion, output_mode)
                continue

            # --- LISTEN TO CONVERSATION ---
            if hotkey_state.focused_listening:
                # Focused mode: shorter capture, accumulate
                text = listen_continuous(recognizer)
                if text:
                    focused_capture.append(text)
                    print(f"   🎯 Captured: \"{text}\"")
                continue

            # --- NORMAL AUTO-LISTEN MODE ---
            text = listen_continuous(recognizer)

            if not text:
                continue

            text_lower = text.lower().strip()

            # --- VOICE COMMANDS ---
            if any(w in text_lower for w in ["exit", "quit", "stop subrati"]):
                record_session(conversation_history, suggestions_given)
                if len(conversation_history) >= 5:
                    print("   🧠 Learning from this conversation...")
                    evolve_from_conversation(conversation_history, suggestions_given)
                    # Auto-generate summary on exit
                    from summarize import summarize_conversation, save_summary
                    print("   📋 Generating call summary...")
                    summary_data = summarize_conversation(conversation_history)
                    filepath = save_summary(summary_data)
                    print(f"   💾 Summary saved: {filepath}")
                _output("Session saved. Goodbye.", output_mode)
                break

            if text_lower in ["speak", "speak mode", "voice mode", "voice"]:
                output_mode = "speak"
                print("\n   🔊 Voice mode ON\n")
                continue

            if any(w in text_lower for w in ["silent", "quietly", "text only", "silent mode"]):
                output_mode = "silent"
                print("\n   📝 Silent mode ON\n")
                continue

            if text_lower in ["good", "thanks", "nice", "perfect", "that's good"]:
                if last_suggestion and last_question:
                    record_good_response(last_question, last_suggestion)
                    print("   ✅ Learned!\n")
                continue

            # --- MANUAL TRIGGER ---
            if any(trigger in text_lower for trigger in [
                "suggest", "what should i say", "help me",
                "coach me", "what do i say", "what to say", "answer"
            ]):
                if conversation_history:
                    suggestion = _get_answer(
                        conversation_history[-1], conversation_history,
                        training_context, memory_context
                    )
                    last_suggestion = suggestion
                    last_question = conversation_history[-1]
                    suggestions_given.append(suggestion)
                    _output(suggestion, output_mode)
                continue

            # --- SUMMARIZE TRIGGER ---
            if any(trigger in text_lower for trigger in [
                "summarize", "summary", "wrap up", "action items"
            ]):
                from summarize import generate_live_summary, summarize_conversation, save_summary
                print("   📋 Generating summary & action items...")
                summary = generate_live_summary(conversation_history)
                _output(summary, output_mode)
                # Also save full summary to file
                summary_data = summarize_conversation(conversation_history)
                filepath = save_summary(summary_data)
                print(f"   💾 Full summary saved: {filepath}")
                continue

            # --- CAPTURE CONVERSATION ---
            conversation_history.append(text)
            if len(conversation_history) > max_history:
                conversation_history.pop(0)

            print(f"   💬 \"{text}\"")

            # --- AUTO-DETECT QUESTIONS & ANSWER ---
            if detect_question(text):
                print("   ❓ Question detected → generating answer...")
                suggestion = _get_answer(
                    text, conversation_history,
                    training_context, memory_context
                )
                last_suggestion = suggestion
                last_question = text
                suggestions_given.append(suggestion)
                _output(suggestion, output_mode)

        except KeyboardInterrupt:
            record_session(conversation_history, suggestions_given)
            if len(conversation_history) >= 5:
                evolve_from_conversation(conversation_history, suggestions_given)
            print("\n\n👋 Session saved. Stealth mode off.")
            break
        except Exception as e:
            print(f"\n   ❌ Error: {e}")
    
    # Cleanup
    kb_listener.stop()


def _get_answer(question: str, history: list, training_ctx: str, memory_ctx: str) -> str:
    """
    Get answer for a question. Uses training if available, otherwise general AI knowledge.
    Works for both trained topics AND out-of-box questions.
    """
    system_prompt = _build_system_prompt(training_ctx, memory_ctx)

    # Build context from recent conversation
    recent = history[-8:] if history else []
    context_text = "\n".join(f"- {line}" for line in recent)

    prompt = f"""{system_prompt}

CONVERSATION SO FAR:
{context_text}

QUESTION/STATEMENT TO RESPOND TO:
"{question}"

Give me the best answer. If this matches something in your training context, use that answer adapted naturally. If not, answer from your general knowledge — be helpful, structured, and practical. Give ONLY the answer, nothing else."""

    return get_response(prompt)


def _output(text: str, mode: str):
    """Output response in the chosen mode."""
    if mode == "speak":
        speak(text)
    else:
        # Silent mode — clear visual box on screen
        lines = text.split('. ')
        print(f"\n   ╔{'═' * 54}╗")
        print(f"   ║ 💡 ANSWER:")
        for line in lines:
            line = line.strip()
            if line:
                # Wrap long lines
                while len(line) > 52:
                    print(f"   ║  {line[:52]}")
                    line = line[52:]
                print(f"   ║  {line}")
        print(f"   ╚{'═' * 54}╝\n")


if __name__ == "__main__":
    run_stealth_mode()
