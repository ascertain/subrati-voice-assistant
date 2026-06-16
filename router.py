"""
SUBRATI Smart Router
Routes queries to appropriate handling mode.
"""

import requests


def route_query(text: str) -> str:
    """Classify user query into mode: code, chat, or search."""
    text_lower = text.lower()

    # Code-related keywords
    if any(k in text_lower for k in [
        "code", "function", "bug", "error", "build", "python",
        "javascript", "program", "script", "debug", "compile",
        "class", "variable", "loop", "syntax", "api", "database"
    ]):
        return "code"

    # Search/real-time keywords
    if any(k in text_lower for k in [
        "latest", "news", "price", "weather", "today",
        "current", "update", "stock", "score"
    ]):
        return "search"

    # Default to chat
    return "chat"


def enhance_prompt(text: str, mode: str) -> str:
    """Add mode-specific context to the prompt."""
    if mode == "code":
        return f"[Coding Assistant Mode] {text}\n\nProvide a clear, concise technical answer."
    elif mode == "search":
        # Try to get quick web info via DuckDuckGo
        search_context = _quick_search(text)
        if search_context:
            return f"Based on this info: {search_context}\n\nUser asked: {text}\n\nGive a brief spoken answer."
        return f"[Search Mode - no live data available] {text}\n\nAnswer based on your training data and note if info might be outdated."
    else:
        return text


def _quick_search(query: str) -> str:
    """Quick DuckDuckGo instant answer (free, no API key needed)."""
    try:
        response = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": 1},
            timeout=5,
        )
        data = response.json()
        # Try abstract first, then answer
        abstract = data.get("AbstractText", "")
        if abstract:
            return abstract[:500]
        answer = data.get("Answer", "")
        if answer:
            return answer[:500]
    except Exception:
        pass
    return ""
