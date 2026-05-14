# frontend/app.py
# Streamlit UI for AI Debate Partner
# Run with: streamlit run app.py

import streamlit as st
import requests

# ─── Config ───────────────────────────────────────────────
BACKEND_URL = "http://localhost:8000"  # Change if backend runs elsewhere

# Page setup
st.set_page_config(
    page_title="AI Debate Partner",
    page_icon="🎤",
    layout="centered"
)

# ─── Session State Init ────────────────────────────────────
# Streamlit reruns on every interaction — session_state persists data across reruns

if "session_id" not in st.session_state:
    st.session_state.session_id = None       # Backend session ID

if "debate_started" not in st.session_state:
    st.session_state.debate_started = False  # Has debate begun?

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []       # List of {role, text, score}

if "topic" not in st.session_state:
    st.session_state.topic = ""

if "ai_stance" not in st.session_state:
    st.session_state.ai_stance = ""

if "debate_ended" not in st.session_state:
    st.session_state.debate_ended = False

if "summary_data" not in st.session_state:
    st.session_state.summary_data = None


# ─── Helper: call backend ─────────────────────────────────

def api_post(endpoint: str, data: dict) -> dict | None:
    """POST to backend, return JSON or None on error."""
    try:
        res = requests.post(f"{BACKEND_URL}/{endpoint}", json=data, timeout=30)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend. Is `uvicorn main:app --reload` running?")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Request failed: {str(e)}")
        return None


# ─── UI: Header ───────────────────────────────────────────

st.title("🎤 AI Debate Partner")
st.caption("Pick a topic, choose your side — and debate the AI!")
st.divider()


# ─── UI: Setup Panel (shown before debate starts) ─────────

if not st.session_state.debate_started:

    st.subheader("⚙️ Setup Your Debate")

    topic = st.text_input(
        "💬 Debate Topic",
        placeholder="e.g. Social media does more harm than good"
    )

    user_stance = st.radio(
        "🙋 Your Stance",
        options=["for", "against"],
        horizontal=True,
        help="The AI will automatically take the opposite side."
    )

    if st.button("🚀 Start Debate", use_container_width=True):
        if not topic.strip():
            st.warning("Please enter a debate topic first.")
        else:
            with st.spinner("AI is preparing its opening argument..."):
                result = api_post("start_debate", {
                    "topic": topic.strip(),
                    "user_stance": user_stance
                })

            if result:
                # Save to session state
                st.session_state.session_id = result["session_id"]
                st.session_state.topic = topic.strip()
                st.session_state.ai_stance = result["ai_stance"]
                st.session_state.debate_started = True

                # Add AI opening to chat history
                st.session_state.chat_history.append({
                    "role": "ai",
                    "text": result["opening_argument"],
                    "score": None
                })

                st.rerun()  # Refresh page to show debate view


# ─── UI: Debate Panel (shown after debate starts) ──────────

else:
    # Topic + stance info bar
    stance_label = "FOR 👍" if st.session_state.ai_stance == "for" else "AGAINST 👎"
    st.markdown(
        f"**Topic:** {st.session_state.topic}   |   "
        f"**AI is:** {stance_label}   |   "
        f"**You are:** {'AGAINST 👎' if st.session_state.ai_stance == 'for' else 'FOR 👍'}"
    )
    st.divider()

    # ── Chat History Display ──────────────────────────────
    st.subheader("💬 Debate")

    for i, msg in enumerate(st.session_state.chat_history):

        if msg["role"] == "ai":
            # AI message — show on left with robot icon
            with st.chat_message("assistant", avatar="🤖"):
                st.write(msg["text"])

        else:
            # User message — show on right with person icon
            with st.chat_message("user", avatar="🙋"):
                st.write(msg["text"])

                # Show score below user message (scores come after user turn)
                if msg.get("score"):
                    s = msg["score"]

                    # Score numbers row
                    col1, col2 = st.columns(2)
                    col1.metric("Your Score", f"{s['user_score']}/10")
                    col2.metric("AI Score",   f"{s['ai_score']}/10")

                    # Overall verdict
                    st.caption(f"⚖️ **Verdict:** {s.get('reason', '')}")

                    # Detailed feedback side by side
                    col3, col4 = st.columns(2)

                    with col3:
                        st.markdown("**🧑 Your Argument**")
                        st.success(f"✅ {s.get('user_good', 'N/A')}")
                        st.error(f"❌ {s.get('user_bad', 'N/A')}")

                    with col4:
                        st.markdown("**🤖 AI Argument**")
                        st.success(f"✅ {s.get('ai_good', 'N/A')}")
                        st.error(f"❌ {s.get('ai_bad', 'N/A')}")

    # ── Input Area (hidden after debate ends) ─────────────
    if not st.session_state.debate_ended:

        st.divider()
        user_input = st.text_area(
            "✍️ Your Argument",
            placeholder="Type your argument here...",
            height=100,
            key="user_input_box"
        )

        col1, col2 = st.columns([3, 1])

        with col1:
            submit = st.button("📨 Submit Argument", use_container_width=True)

        with col2:
            end = st.button("🏁 End Debate", use_container_width=True)

        # ── Submit argument ───────────────────────────────
        if submit:
            if not user_input.strip():
                st.warning("Please enter your argument before submitting.")
            else:
                with st.spinner("AI is crafting a counter-argument..."):
                    result = api_post("send_argument", {
                        "session_id": st.session_state.session_id,
                        "user_argument": user_input.strip()
                    })

                if result:
                    # Save user message with score
                    st.session_state.chat_history.append({
                        "role": "user",
                        "text": user_input.strip(),
                        "score": result["scores"]
                    })

                    # Save AI counter
                    st.session_state.chat_history.append({
                        "role": "ai",
                        "text": result["ai_counter"],
                        "score": None
                    })

                    st.rerun()

        # ── End debate ────────────────────────────────────
        if end:
            with st.spinner("Generating debate summary..."):
                result = api_post("end_debate", {
                    "session_id": st.session_state.session_id
                })

            if result:
                st.session_state.debate_ended = True
                st.session_state.summary_data = result
                st.rerun()

    # ── Summary Panel (shown after debate ends) ───────────
    if st.session_state.debate_ended and st.session_state.summary_data:
        st.divider()
        st.subheader("🏆 Debate Summary")

        data = st.session_state.summary_data

        # Final scores
        col1, col2, col3 = st.columns(3)
        col1.metric("Your Total Score", f"{data['total_user_score']}")
        col2.metric("AI Total Score", f"{data['total_ai_score']}")
        col3.metric("Rounds Played", f"{data['rounds_played']}")

        # Winner banner
        if data["total_user_score"] > data["total_ai_score"]:
            st.success("🎉 You won the debate! Great arguments!")
        elif data["total_ai_score"] > data["total_user_score"]:
            st.error("🤖 AI won this round. Better luck next time!")
        else:
            st.info("🤝 It's a tie! Well matched debate.")

        # AI-generated summary
        st.markdown("### 📝 Analysis")
        st.write(data["summary"])

        st.divider()

        # Reset button — start a new debate
        if st.button("🔄 Start New Debate", use_container_width=True):
            # Clear all session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()