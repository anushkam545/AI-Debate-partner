# debate_engine.py
# Handles all Gemini API calls for debate logic
# This is the "brain" of the app

import os
import google.generativeai as genai
from dotenv import load_dotenv

from prompts import (
    get_opening_prompt,
    get_counter_prompt,
    get_summary_prompt
)

# Load API key from .env file
from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Load Gemini model
# gemini-2.5-flash is fast and free-tier friendly
model = genai.GenerativeModel("gemini-2.5-flash")


def call_gemini(prompt: str) -> str:
    """
    Core function to send a prompt to Gemini and get a text response.
    All other functions in this file use this.
    """

    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.8,     # Slightly creative but still logical
                "max_output_tokens": 1536
            }
        )

        return response.text.strip()

    except Exception as e:
        return f"Error calling Gemini API: {str(e)}"


def get_opening_argument(topic: str, ai_stance: str) -> str:
    """
    Generate AI's opening argument for the debate.
    Called once when debate starts.
    """
    prompt = get_opening_prompt(topic, ai_stance)
    return call_gemini(prompt)


def get_counter_argument(
    topic: str,
    ai_stance: str,
    history: str,
    user_argument: str
) -> str:
    """
    Generate AI's counter to the user's latest argument.
    Passes full history so AI has memory of the whole debate.
    """

    prompt = get_counter_prompt(
        topic,
        ai_stance,
        history,
        user_argument
    )

    return call_gemini(prompt)


def get_debate_summary(topic: str, ai_stance: str, history: str) -> str:
    """
    Generate a final summary of the entire debate.
    Called when user clicks "End Debate".
    """

    prompt = get_summary_prompt(
        topic,
        ai_stance,
        history
    )

    return call_gemini(prompt)