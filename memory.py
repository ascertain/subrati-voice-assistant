"""
SUBRATI Memory & Learning System
==================================
- Loads initial training context
- Saves conversation patterns
- Learns what suggestions worked (evolves over time)
- Auto-builds knowledge about conversation dynamics
"""

import os
import json
from datetime import datetime

TRAINING_FILE = os.path.join("training", "context.txt")
INTERVIEW_FILE = os.path.join("training", "interview_prep.txt")
INTERVIEW_QA_FILE = os.path.join("training", "interview_qa.txt")
MEMORY_FILE = os.path.join("training", "memory.json")
LEARNINGS_FILE = os.path.join("training", "learnings.json")


def load_training_context() -> str:
    """Load the user's training context file(s)."""
    parts = []
    for filepath in [TRAINING_FILE, INTERVIEW_FILE, INTERVIEW_QA_FILE]:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                parts.append(f.read())
    return "\n\n".join(parts)


def load_memory() -> dict:
    """Load conversation memory (patterns, topics, what worked)."""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "sessions": [],
        "common_questions": [],
        "good_responses": [],
        "topics_discussed": [],
        "patterns": []
    }


def save_memory(memory: dict):
    """Save updated memory to disk."""
    os.makedirs("training", exist_ok=True)
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)


def load_learnings() -> list:
    """Load accumulated learnings (what works, what doesn't)."""
    if os.path.exists(LEARNINGS_FILE):
        with open(LEARNINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_learning(learning: str):
    """Add a new learning to the knowledge base."""
    learnings = load_learnings()
    learnings.append({
        "text": learning,
        "timestamp": datetime.now().isoformat(),
    })
    # Keep last 100 learnings
    learnings = learnings[-100:]
    os.makedirs("training", exist_ok=True)
    with open(LEARNINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(learnings, f, indent=2, ensure_ascii=False)


def record_session(conversation: list, suggestions_given: list):
    """Record a conversation session for future learning."""
    memory = load_memory()

    session = {
        "date": datetime.now().isoformat(),
        "conversation_length": len(conversation),
        "last_lines": conversation[-10:] if conversation else [],
        "suggestions_given": suggestions_given[-5:] if suggestions_given else [],
    }
    memory["sessions"].append(session)

    # Keep only last 50 sessions
    memory["sessions"] = memory["sessions"][-50:]

    save_memory(memory)


def record_good_response(question: str, response: str):
    """Mark a suggestion as good (user said 'good' or 'thanks')."""
    memory = load_memory()
    memory["good_responses"].append({
        "question": question,
        "response": response,
        "timestamp": datetime.now().isoformat(),
    })
    # Keep last 50 good responses
    memory["good_responses"] = memory["good_responses"][-50:]
    save_memory(memory)


def get_memory_context() -> str:
    """Build a context string from memory for the AI."""
    memory = load_memory()
    learnings = load_learnings()

    context_parts = []

    # Add good responses that worked before
    if memory.get("good_responses"):
        context_parts.append("## Responses that worked well before:")
        for item in memory["good_responses"][-10:]:
            context_parts.append(f"- When asked: \"{item['question']}\" → Good reply: \"{item['response']}\"")

    # Add learnings
    if learnings:
        context_parts.append("\n## Things I've learned:")
        for item in learnings[-10:]:
            context_parts.append(f"- {item['text']}")

    return "\n".join(context_parts)


def detect_question(text: str) -> bool:
    """Detect if someone is asking a question that needs a response."""
    text_lower = text.lower().strip()

    # Direct question indicators
    question_words = [
        "what", "why", "how", "when", "where", "who", "which",
        "do you", "did you", "are you", "have you", "can you",
        "will you", "would you", "could you", "should we",
        "don't you", "isn't it", "aren't you", "won't you",
        "what do you think", "what about", "how about",
    ]

    # Check for question marks or question starters
    if "?" in text:
        return True

    if any(text_lower.startswith(w) for w in question_words):
        return True

    # Implied questions / requests
    implied = [
        "tell me", "i want to know", "i need", "can we",
        "let's", "shall we", "you never", "you always",
        "i wish you", "why can't you",
    ]
    if any(phrase in text_lower for phrase in implied):
        return True

    return False


def evolve_from_conversation(conversation: list, suggestions: list):
    """
    Auto-learn from the conversation.
    Analyzes patterns and saves learnings for future use.
    """
    from llm_chain import get_response

    if len(conversation) < 5:
        return  # Not enough data

    recent = conversation[-15:]
    convo_text = "\n".join(f"- {line}" for line in recent)

    # Ask AI to extract learnings
    prompt = f"""Analyze this conversation and extract 1-3 SHORT learnings about the relationship dynamics, communication patterns, or what topics came up. Each learning should be one line.

Conversation:
{convo_text}

Format: just bullet points, nothing else. Be specific and practical."""

    try:
        result = get_response(prompt)
        if result:
            # Save each line as a learning
            for line in result.strip().split("\n"):
                line = line.strip().lstrip("-•* ")
                if line and len(line) > 10:
                    save_learning(line)
    except Exception:
        pass  # Silent fail - don't interrupt
