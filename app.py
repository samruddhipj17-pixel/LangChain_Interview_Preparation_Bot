"""Streamlit interface for the Interview Prep Bot."""

from __future__ import annotations

import streamlit as st

from interview_bot import ConfigurationError, stream_answer

st.set_page_config(
    page_title="Interview Prep Bot",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .stApp { background: radial-gradient(ellipse at 15% 0%, #f0f4ff 0%, #f8fafc 42%, #fff 100%); }
      .block-container { max-width: 1050px; padding-top: 2.2rem; }
      [data-testid="stChatMessage"] { border: 1px solid #e7eaf1; border-radius: 16px; padding: 1rem; background: #fff; }
      .hero { padding: 1.5rem 1.8rem; border-radius: 22px; background: linear-gradient(120deg,#172554,#3730a3 68%,#6d28d9); color: white; margin-bottom: 1.5rem; }
      .hero h1 { color: white; margin: 0 0 .3rem 0; letter-spacing: -.03em; }
      .hero p { color: #dbeafe; margin: 0; font-size: 1.05rem; }
      div[data-testid="stMetric"] { background: white; border: 1px solid #e7eaf1; border-radius: 14px; padding: .8rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="hero"><h1>🎯 Interview Prep Bot</h1>'
    "<p>Practice thoughtful answers, understand the reasoning, and walk into your next interview prepared.</p></div>",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Your interview")
    role = st.text_input("Target role", placeholder="e.g. Junior Python Developer")
    level = st.selectbox(
        "Experience level",
        ["Student / fresher", "Early career", "Mid-level", "Senior", "Career changer"],
        index=0,
    )
    interview_type = st.selectbox(
        "Practice focus",
        ["Mixed practice", "Behavioral", "Technical", "HR / introduction", "Situational"],
    )
    st.divider()
    st.caption("Tip: Share the role and a little context to get more tailored practice.")
    if st.button("Start a new session", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

col_a, col_b, col_c = st.columns(3)
with col_a:
    st.metric("Practice modes", "5")
with col_b:
    st.metric("Your context", "Personalized" if role.strip() else "Add a role")
with col_c:
    st.metric("Session questions", str(sum(m["role"] == "user" for m in st.session_state.messages)))

st.write("")
if not st.session_state.messages:
    st.subheader("Start with a question")
    suggestions = [
        "Tell me about yourself.",
        "How should I explain a challenging project?",
        "What is the difference between a list and a tuple in Python?",
        "How do I answer ‘What is your greatest weakness?’",
    ]
    cols = st.columns(2)
    for index, suggestion in enumerate(suggestions):
        with cols[index % 2]:
            if st.button(suggestion, key=f"suggestion_{index}", use_container_width=True):
                st.session_state.pending_question = suggestion

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

pending = st.session_state.pop("pending_question", None)
question = st.chat_input("Ask an interview question…") or pending
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    prior_messages = st.session_state.messages[:-1]
    history = "\n".join(f"{m['role'].title()}: {m['content']}" for m in prior_messages)
    with st.chat_message("assistant"):
        try:
            response = st.write_stream(
                stream_answer(
                    question,
                    role=role or "Not specified",
                    level=level,
                    interview_type=interview_type,
                    history=history or "No previous conversation.",
                )
            )
            if not response:
                raise RuntimeError("Gemini returned an empty answer.")
            st.session_state.messages.append({"role": "assistant", "content": response})
        except ConfigurationError as exc:
            st.error(str(exc))
            st.info("Add your Gemini API key to `.env`, then restart Streamlit.")
        except ValueError as exc:
            st.warning(str(exc))
        except Exception as exc:
            st.error("The request timed out or Gemini is temporarily unavailable. Please try again.")
            st.caption(f"Details: {type(exc).__name__}")

st.caption("AI-generated practice guidance can be imperfect. Personalize sample answers with your real experience.")
