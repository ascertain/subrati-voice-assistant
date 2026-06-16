"""
SUBRATI LLM Fallback Chain
Priority: Groq (fastest) → Gemini → HuggingFace → offline message
"""

import requests
import json
from config import (
    GROQ_API_KEY, GEMINI_API_KEY, HF_API_KEY,
    GROQ_MODEL, GEMINI_MODEL, HF_MODEL, SYSTEM_PROMPT
)


def call_groq(prompt: str) -> str:
    """Primary LLM - Groq (sub-second response)."""
    if not GROQ_API_KEY:
        raise ValueError("No Groq API key")

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 512,
        },
        timeout=10,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()


def call_gemini(prompt: str) -> str:
    """Secondary LLM - Google Gemini (free tier)."""
    if not GEMINI_API_KEY:
        raise ValueError("No Gemini API key")

    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}",
        headers={"Content-Type": "application/json"},
        json={
            "contents": [{"parts": [{"text": f"{SYSTEM_PROMPT}\n\nUser: {prompt}"}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 512,
            },
        },
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()


def call_huggingface(prompt: str) -> str:
    """Tertiary LLM - HuggingFace Inference API (free fallback)."""
    if not HF_API_KEY:
        raise ValueError("No HuggingFace API key")

    response = requests.post(
        f"https://api-inference.huggingface.co/models/{HF_MODEL}",
        headers={"Authorization": f"Bearer {HF_API_KEY}"},
        json={
            "inputs": f"<s>[INST] {SYSTEM_PROMPT}\n\n{prompt} [/INST]",
            "parameters": {
                "max_new_tokens": 512,
                "temperature": 0.7,
            },
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    if isinstance(data, list):
        text = data[0].get("generated_text", "")
        # Strip the prompt from the response
        if "[/INST]" in text:
            text = text.split("[/INST]")[-1].strip()
        return text
    return str(data)


def get_response(prompt: str) -> str:
    """
    Smart fallback chain: Groq → Gemini → HuggingFace → offline.
    Returns the first successful response.
    """
    # Try Groq first (fastest)
    try:
        result = call_groq(prompt)
        if result:
            return result
    except Exception as e:
        print(f"  [Groq failed: {e}]")

    # Try Gemini second
    try:
        result = call_gemini(prompt)
        if result:
            return result
    except Exception as e:
        print(f"  [Gemini failed: {e}]")

    # Try HuggingFace last
    try:
        result = call_huggingface(prompt)
        if result:
            return result
    except Exception as e:
        print(f"  [HuggingFace failed: {e}]")

    # All failed
    return "I'm having trouble connecting to my AI services right now. Please check your API keys in the .env file."
