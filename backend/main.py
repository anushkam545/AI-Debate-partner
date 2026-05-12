# main.py
# FastAPI backend — defines all API routes
# Run with: uvicorn main:app --reload

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import our custom modules
from memory import create_session, get_session, add_message, get_history_text, add_score
from debate_engine import get_opening_argument, get_counter_argument, get_debate_summary
from scoring import score_round

# Create the FastAPI app
app = FastAPI(title="AI Debate Partner", version="1.0")

# Allow Streamlit frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your domain
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request/Response Models (what data each endpoint expects) ---

class StartDebateRequest(BaseModel):
    topic: str          # e.g. "Social media is harmful"
    user_stance: str    # "for" or "against"

class ArgumentRequest(BaseModel):
    session_id: str
    user_argument: str  # What the user just said

class EndDebateRequest(BaseModel):
    session_id: str


# --- Routes ---

@app.get("/")
def root():
    """Health check — visit this to confirm backend is running."""
    return {"message": "AI Debate Partner backend is running!"}


@app.post("/start_debate")
def start_debate(req: StartDebateRequest):
    """
    Start a new debate session.
    AI takes the OPPOSITE stance of the user.
    Returns: session_id, ai_stance, opening_argument
    """
    # AI takes opposite side
    ai_stance = "against" if req.user_stance == "for" else "for"

    # Create a new session in memory
    session_id = create_session(req.topic, ai_stance)

    # Get AI's opening argument from Gemini
    opening = get_opening_argument(req.topic, ai_stance)

    # Save AI's opening to history
    add_message(session_id, "ai", opening)

    return {
        "session_id": session_id,
        "ai_stance": ai_stance,
        "opening_argument": opening
    }


@app.post("/send_argument")
def send_argument(req: ArgumentRequest):
    """
    User sends their argument, AI responds with a counter.
    Maintains full conversation memory.
    Returns: ai_counter, round_scores
    """
    session = get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Save user's argument to history
    add_message(req.session_id, "user", req.user_argument)

    # Get full history to give Gemini context
    history = get_history_text(req.session_id)

    # Get AI counter-argument
    counter = get_counter_argument(
        topic=session["topic"],
        ai_stance=session["ai_stance"],
        history=history,
        user_argument=req.user_argument
    )

    # Save AI's counter to history
    add_message(req.session_id, "ai", counter)

    # Score this round
    scores = score_round(req.user_argument, counter)
    round_num = session["round"]
    add_score(req.session_id, round_num, scores["user_score"], scores["ai_score"])

    return {
        "ai_counter": counter,
        "round": round_num,
        "scores": scores
    }


@app.get("/get_history/{session_id}")
def get_history(session_id: str):
    """Return full debate history for a session."""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "topic": session["topic"],
        "ai_stance": session["ai_stance"],
        "history": session["history"],
        "scores": session["scores"]
    }


@app.post("/end_debate")
def end_debate(req: EndDebateRequest):
    """
    End the debate and return a summary + total scores.
    """
    session = get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    history = get_history_text(req.session_id)

    # Generate summary via Gemini
    summary = get_debate_summary(session["topic"], session["ai_stance"], history)

    # Calculate total scores
    total_user = sum(s["user_score"] for s in session["scores"])
    total_ai = sum(s["ai_score"] for s in session["scores"])

    return {
        "summary": summary,
        "total_user_score": total_user,
        "total_ai_score": total_ai,
        "rounds_played": len(session["scores"])
    }
