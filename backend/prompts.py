# prompts.py
# All prompt templates live here — easy to edit and understand


def get_opening_prompt(topic: str, ai_stance: str) -> str:
    """
    Prompt for AI's first argument.
    AI introduces its stance and gives a strong opening argument.
    """
    return f"""
You are a confident debate partner. The debate topic is: "{topic}"

Your stance: You are {ai_stance} this topic.

Give a clear, logical opening argument in 3-4 sentences.
Be persuasive but not aggressive.
Do NOT use bullet points — speak naturally like a debater.
Start directly with your argument.
"""


def get_counter_prompt(topic: str, ai_stance: str, history: str, user_argument: str) -> str:
    """
    Prompt for AI's counter-argument.
    Passes full history so AI remembers what was said before.
    """
    return f"""
You are a debate partner arguing {ai_stance} the topic: "{topic}"

Here is the debate so far:
{history}

The human just said: "{user_argument}"

Your job:
1. Briefly acknowledge what they said (1 sentence)
2. Point out the flaw or weakness in their argument (1-2 sentences)
3. Reinforce your own position with a new supporting point (2 sentences)

Keep it under 5 sentences total. Be logical and direct. No bullet points.
"""


def get_summary_prompt(topic: str, ai_stance: str, history: str) -> str:
    """
    Prompt to generate a final debate summary.
    """
    return f"""
The following debate just concluded on the topic: "{topic}"
The AI was arguing {ai_stance} the topic.

Full debate:
{history}

Write a short debate summary (5-6 sentences) that:
- Describes the main points both sides made
- Notes which side had stronger arguments (be honest)
- Ends with a concluding thought on the topic

Write in a neutral, analytical tone.
"""


def get_scoring_prompt(user_argument: str, ai_argument: str) -> str:
    """
    Prompt to score both arguments in a round.
    Returns JSON with scores out of 10.
    """
    return f"""
Compare these two debate arguments and score them.

Human's argument: "{user_argument}"
AI's argument: "{ai_argument}"

Score each out of 10 based on:
- Logic and reasoning
- Use of evidence or examples
- Clarity

Reply ONLY with this JSON format (no extra text):
{{"user_score": <number>, "ai_score": <number>, "reason": "<one sentence why>"}}
"""
