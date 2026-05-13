# memory.py
# Stores all debate sessions in a simple dictionary (no database needed)
# Key = session_id, Value = debate data

import uuid

# This acts as our "database" - just a Python dict in RAM
debates = {}


def create_session(topic: str, ai_stance: str) -> str:
    """Create a new debate session and return its unique ID."""
    session_id = str(uuid.uuid4())  # Generate a random unique ID

    debates[session_id] = {
        "topic": topic,
        "ai_stance": ai_stance,       # e.g. "against" or "for"
        "history": [],                 # List of {role, text} dicts
        "scores": [],                  # List of {round, user_score, ai_score}
        "round": 0                     # Track which round we're on
    }

    return session_id


def get_session(session_id: str) -> dict:
    """Fetch a session by ID. Returns None if not found."""
    return debates.get(session_id, None)


def add_message(session_id: str, role: str, text: str):
    """Add a message to debate history. Role = 'user' or 'ai'."""
    if session_id in debates:
        debates[session_id]["history"].append({
            "role": role,
            "text": text
        })
        debates[session_id]["round"] += 1  # Increment round count


def add_score(session_id: str, round_num: int, user_score: int, ai_score: int):
    """Save scores for a round."""
    if session_id in debates:
        debates[session_id]["scores"].append({
            "round": round_num,
            "user_score": user_score,
            "ai_score": ai_score
        })


def get_history_text(session_id: str) -> str:
    """
    Return full debate history as a single formatted string.
    This is passed to Gemini so it remembers past arguments.
    """
    session = get_session(session_id)
    if not session:
        return ""

    lines = []
    for msg in session["history"]:
        prefix = "Human" if msg["role"] == "user" else "AI Debater"
        lines.append(f"{prefix}: {msg['text']}")

    return "\n".join(lines)


def delete_session(session_id: str):
    """Clean up session from memory."""
    if session_id in debates:
        del debates[session_id]
