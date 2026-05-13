# scoring.py
# Strict debate scoring with detailed feedback
# Robust JSON parsing — handles all Gemini response quirks

import os
import re
import json
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")


# NOTE: All {{ }} in the example JSON are doubled so Python .format() doesn't
# mistake them for variables — they render as single { } when sent to Gemini
STRICT_SCORING_PROMPT = """You are a strict debate judge. Score two arguments.

Human argument: {user_argument}
AI argument: {ai_argument}

RULES:
- Score 1-10. Be harsh and honest.
- One-liner with no reasoning = max 4
- Good structure with examples = 7-9
- Perfect logic and evidence = 10
- Never give equal scores just to seem fair
- Do NOT favour the AI side
- Penalty: just agreeing without reasoning = -3

Evaluate on: Logic, Evidence, Depth

IMPORTANT: Reply with ONLY raw JSON. No intro. No explanation. No markdown. Nothing else.

Example format (fill in real values):
{{"user_score": 7, "ai_score": 8, "user_good": "Clear stance taken.", "user_bad": "Lacked evidence.", "ai_good": "Used real examples.", "ai_bad": "Slightly repetitive.", "reason": "AI had stronger supporting evidence."}}
"""


def score_round(user_argument: str, ai_argument: str) -> dict:
    """Score one debate round. Returns scores + detailed feedback."""

    prompt = STRICT_SCORING_PROMPT.format(
        user_argument=user_argument,
        ai_argument=ai_argument
    )

    raw_text = ""

    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.1,
                "max_output_tokens": 400
            }
        )

        raw_text = response.text.strip()

        # DEBUG: shows in uvicorn terminal — remove once scoring works
        print("\n===== GEMINI SCORING RAW =====")
        print(raw_text)
        print("==============================\n")

        # Clean step 1: remove markdown fences
        raw_text = re.sub(r'```json|```', '', raw_text).strip()

        # Clean step 2: extract JSON object from anywhere in the response
        json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if not json_match:
            return _fallback_score(raw_text)

        scores = json.loads(json_match.group())

        return {
            "user_score": max(1, min(10, int(scores.get("user_score", 5)))),
            "ai_score":   max(1, min(10, int(scores.get("ai_score",   5)))),
            "user_good":  scores.get("user_good", "Made a point."),
            "user_bad":   scores.get("user_bad",  "Needs more evidence."),
            "ai_good":    scores.get("ai_good",   "Argued clearly."),
            "ai_bad":     scores.get("ai_bad",    "Could improve depth."),
            "reason":     scores.get("reason",    "Arguments evaluated.")
        }

    except (json.JSONDecodeError, ValueError, KeyError):
        return _fallback_score(raw_text)

    except Exception as e:
        return _default_score(f"Scoring error: {str(e)}")


def _fallback_score(raw_text: str) -> dict:
    """Last resort: pull numbers out of raw text with regex."""
    try:
        u = re.search(r'"?user_score"?\s*:\s*(\d+)', raw_text)
        a = re.search(r'"?ai_score"?\s*:\s*(\d+)',   raw_text)
        if u and a:
            return {
                "user_score": max(1, min(10, int(u.group(1)))),
                "ai_score":   max(1, min(10, int(a.group(1)))),
                "user_good":  "Partial evaluation only.",
                "user_bad":   "Partial evaluation only.",
                "ai_good":    "Partial evaluation only.",
                "ai_bad":     "Partial evaluation only.",
                "reason":     "Scores recovered from partial response."
            }
    except Exception:
        pass
    return _default_score("Could not calculate scores.")


def _default_score(reason: str) -> dict:
    return {
        "user_score": 5, "ai_score": 5,
        "user_good": "Could not evaluate.", "user_bad": "Could not evaluate.",
        "ai_good":   "Could not evaluate.", "ai_bad":   "Could not evaluate.",
        "reason": reason
    }