"""
SUBRATI Call Summary & Action Items Generator
==============================================
After a conversation/meeting/interview, generates:
- Full summary of what was discussed
- Key decisions made
- Action items with owners
- Follow-up needed

Usage:
    python summarize.py                    # Summarize last session
    python summarize.py --file notes.txt   # Summarize from file
"""

import os
import sys
import json
from datetime import datetime
from llm_chain import get_response
from memory import load_training_context

SUMMARY_DIR = "summaries"


def summarize_conversation(conversation: list, context: str = "") -> dict:
    """Generate a structured summary with action items from a conversation."""
    
    convo_text = "\n".join(f"- {line}" for line in conversation)
    
    prompt = f"""Analyze this conversation/meeting and produce a structured summary.

CONVERSATION:
{convo_text}

{f"CONTEXT: {context}" if context else ""}

Generate a summary in this EXACT format:

## Summary
[2-3 sentence overview of what was discussed]

## Key Points
- [bullet point 1]
- [bullet point 2]
- [bullet point 3]

## Decisions Made
- [decision 1]
- [decision 2]

## Action Items
- [ ] [Action item 1] — Owner: [who]
- [ ] [Action item 2] — Owner: [who]
- [ ] [Action item 3] — Owner: [who]

## Follow-up Needed
- [What needs to happen next]

## Mood/Tone
[Brief note on how the conversation went — positive, tense, productive, etc.]

Be specific and practical. If you can identify who said what, attribute action items accordingly."""

    result = get_response(prompt)
    return {
        "timestamp": datetime.now().isoformat(),
        "conversation_length": len(conversation),
        "summary": result,
        "raw_conversation": conversation,
    }


def save_summary(summary_data: dict, filename: str = None):
    """Save summary to file."""
    os.makedirs(SUMMARY_DIR, exist_ok=True)
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"summary_{timestamp}.txt"
    
    filepath = os.path.join(SUMMARY_DIR, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# Call Summary — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"# Conversation length: {summary_data['conversation_length']} exchanges\n")
        f.write(f"{'=' * 60}\n\n")
        f.write(summary_data["summary"])
        f.write(f"\n\n{'=' * 60}\n")
        f.write(f"# Raw Conversation Log:\n")
        for i, line in enumerate(summary_data["raw_conversation"], 1):
            f.write(f"  {i}. {line}\n")
    
    return filepath


def summarize_last_session():
    """Load and summarize the last recorded session from memory."""
    memory_file = os.path.join("training", "memory.json")
    
    if not os.path.exists(memory_file):
        print("❌ No session history found. Run SUBRATI first to record a conversation.")
        return
    
    with open(memory_file, "r", encoding="utf-8") as f:
        memory = json.load(f)
    
    sessions = memory.get("sessions", [])
    if not sessions:
        print("❌ No sessions recorded yet.")
        return
    
    last_session = sessions[-1]
    conversation = last_session.get("last_lines", [])
    
    if not conversation:
        print("❌ Last session has no conversation data.")
        return
    
    print(f"📋 Summarizing last session ({len(conversation)} lines)...")
    print("   ⏳ Generating summary & action items...\n")
    
    context = load_training_context()
    summary_data = summarize_conversation(conversation, context)
    
    # Print to screen
    print("=" * 60)
    print(summary_data["summary"])
    print("=" * 60)
    
    # Save to file
    filepath = save_summary(summary_data)
    print(f"\n💾 Saved to: {filepath}")
    
    return summary_data


def summarize_from_file(filepath: str):
    """Summarize conversation from a text file (one line per statement)."""
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return
    
    with open(filepath, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    
    print(f"📋 Summarizing {len(lines)} lines from {filepath}...")
    print("   ⏳ Generating summary & action items...\n")
    
    context = load_training_context()
    summary_data = summarize_conversation(lines, context)
    
    print("=" * 60)
    print(summary_data["summary"])
    print("=" * 60)
    
    out_filepath = save_summary(summary_data)
    print(f"\n💾 Saved to: {out_filepath}")
    
    return summary_data


def generate_live_summary(conversation_history: list) -> str:
    """Generate a quick summary during a live session (called from stealth mode)."""
    if len(conversation_history) < 3:
        return "Not enough conversation to summarize yet."
    
    convo_text = "\n".join(f"- {line}" for line in conversation_history)
    
    prompt = f"""Quick summary of this conversation so far (2-3 sentences) + any action items:

{convo_text}

Format:
SUMMARY: [brief overview]
ACTIONS: [bullet list of action items, or "None yet"]"""

    return get_response(prompt)


if __name__ == "__main__":
    if "--file" in sys.argv:
        idx = sys.argv.index("--file")
        if idx + 1 < len(sys.argv):
            summarize_from_file(sys.argv[idx + 1])
        else:
            print("Usage: python summarize.py --file <path>")
    else:
        summarize_last_session()
