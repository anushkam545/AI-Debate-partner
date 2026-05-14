# 🎤 AI Debate Partner

A GenAI-powered debate application where you argue against an AI on any topic. The AI takes the opposite stance, counters your arguments using full conversation memory, and scores each round with detailed feedback using a strict judging system.

Built with **Python · FastAPI · Streamlit · Gemini 2.5 Flash**.

---

## 🚀 Features

* **Dynamic Stance Assignment** — AI automatically takes the opposite side of whatever position you choose.
* **Conversation Memory** — Full debate history is passed to Gemini on every turn, so the AI never forgets what was said.
* **Strict Argument Scoring** — Each round is scored 1–10 with penalties for weak arguments, vague claims, and repetition.
* **Detailed Round Feedback** — After every round you see what you argued well, what you argued poorly, and an overall verdict.
* **Debate Summary** — At the end, Gemini generates a full neutral analysis of the debate and declares a winner.
* **Session Management** — Multiple independent debate sessions supported via UUID-based in-memory storage.
* **REST API Backend** — Clean FastAPI backend with Swagger docs at `/docs`.

---

## 📁 Project Structure

```
ai-debate-partner/
│
├── backend/
│   ├── main.py           # FastAPI routes (all API endpoints)
│   ├── debate_engine.py  # Gemini API calls for debate logic
│   ├── prompts.py        # All prompt templates for Gemini
│   ├── memory.py         # In-memory session storage (dict-based)
│   └── scoring.py        # Strict argument scoring with detailed feedback
│
├── frontend/
│   └── app.py            # Streamlit UI
│
├── requirements.txt      # Python dependencies
├── .gitignore
└── README.md
```

---

## 🛠️ Tech Stack

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.10+ | Core language |
| FastAPI | 0.111 | REST API backend |
| Uvicorn | 0.30 | ASGI server for FastAPI |
| Streamlit | 1.35 | Frontend UI |
| Gemini 2.5 Flash | Latest | AI debate responses + scoring |
| google-generativeai | 0.7+ | Official Gemini Python SDK |
| Pydantic | 2.7 | Request/response validation |
| Python-dotenv | 1.0 | Load API key from `.env` |

---

## ⚙️ Setup and Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-debate-partner.git
cd ai-debate-partner
```

### 2. Create and Activate a Virtual Environment

```bash
# Create the environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Get Your Gemini API Key

* Go to → https://aistudio.google.com/app/apikey
* Click **Create API Key** → select or create a Google Cloud project
* Copy the generated key

> 💡 If you hit quota limits (429 error), create a **new Google Cloud project** and generate a fresh key under it. Each project gets its own free tier quota.

### 5. Set Up Environment Variables

Create a `.env` file in the **root** of the project:

```
GEMINI_API_KEY=your_actual_gemini_key_here
```

> ⚠️ Never share or commit this file. It is already excluded via `.gitignore`.

---

## ▶️ Running the App

You need **two terminals** running simultaneously.

### Terminal 1 — Start the Backend

```bash
cd backend
uvicorn main:app --reload
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

Visit http://127.0.0.1:8000/docs to explore all API endpoints interactively via Swagger UI.

### Terminal 2 — Start the Frontend

```bash
cd frontend
streamlit run app.py
```

The app will open automatically at → http://localhost:8501

---

## 🎮 How to Use

1. Open http://localhost:8501 in your browser
2. Enter a debate topic — e.g. *"AI will replace human jobs"*
3. Choose your stance — **For** or **Against**
4. Click **Start Debate** — AI gives a strong opening argument for the opposite side
5. Type your argument and click **Submit**
6. AI counters using memory of all previous arguments
7. After each round you receive:
   - 📊 Your score vs AI score (out of 10)
   - ✅ What you argued well
   - ❌ What you argued poorly
   - ⚖️ Overall round verdict
8. Click **End Debate** to get the full summary, analysis, and winner

---

## 🧠 How It Works

```
User enters topic + stance
        ↓
Backend creates UUID session (memory.py)
        ↓
Gemini generates AI opening argument (debate_engine.py)
        ↓
User submits argument → saved to session history
        ↓
Full conversation history passed to Gemini (context memory)
        ↓
Gemini generates counter-argument
        ↓
Strict scoring prompt sent → Gemini returns JSON scores + feedback
        ↓
Scores parsed, clamped 1–10, saved to session
        ↓
User ends debate → Gemini generates neutral summary + declares winner
```

---

## 📝 Prompt Design

The app uses four distinct prompt templates in `prompts.py`, each tuned for a specific task:

* **Opening Prompt** — Instructs Gemini to take a firm stance and deliver a persuasive 3–4 sentence opening argument.
* **Counter Prompt** — Passes full debate history for memory, asks Gemini to acknowledge the user's point, expose its weakness, and reinforce its own position.
* **Scoring Prompt** — A strict judging prompt with explicit rules, penalty deductions, and a JSON-only output requirement.
* **Summary Prompt** — Asks Gemini to write a neutral post-debate analysis and declare a winner based on argument quality.

---

## 💡 Challenges & Solutions

During development, several challenges were encountered and resolved:
* **Challenge**: `429 Quota Exceeded` errors on `gemini-2.0-flash` with `limit: 0`.
  
  **Solution**: Created a new Google Cloud project to get a fresh free-tier quota. Also switched to `gemini-2.5-flash` which has more generous limits.

* **Challenge**: `404 model not found` errors when using `gemini-1.5-flash`.
  
  **Solution**: Used `genai.list_models()` to programmatically list all models available to the API key, then selected a confirmed available model.

* **Challenge**: Scoring always returned 5/5 — Gemini was wrapping JSON in markdown fences or adding intro text, breaking `json.loads()`.
  
  **Solution**: Implemented a 3-layer parsing strategy — strip markdown fences → extract `{ }` block via regex → regex number fallback — ensuring scores are always recovered.

* **Challenge**: `KeyError: '"user_score"'` crash in `scoring.py`.
  
  **Solution**: Python's `.format()` was treating `{` `}` in the prompt's example JSON as variable placeholders. Fixed by doubling all curly braces in the example: `{{` `}}`.

* **Challenge**: AI responses were cut off mid-sentence.
  
  **Solution**: Increased `max_output_tokens` from `512` to `1024` in `debate_engine.py`.
