"""LangChain-powered interview preparation assistant."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a supportive, practical interview preparation coach.
Give accurate, specific, easy-to-practice guidance. Adapt the depth to the
candidate's experience level and role. For behavioral questions, explain the
STAR method and provide a clearly labeled sample answer with placeholders where
personal facts are needed; never invent the candidate's experience. For
technical questions, explain the concept, give a concise example when useful,
and mention common follow-up questions. If the prompt is ambiguous, state a
reasonable assumption. Be encouraging without making hiring promises.""",
        ),
        (
            "human",
            "Interview type: {interview_type}\n"
            "Target role: {role}\n"
            "Experience level: {level}\n\n"
            "Recent conversation (oldest first):\n{history}\n\n"
            "Candidate's question: {question}\n\n"
            "Respond with useful preparation advice and a practice-ready answer.",
        ),
    ]
)


class ConfigurationError(RuntimeError):
    """Raised when the app is missing required configuration."""


def build_chain():
    """Create the LangChain prompt-to-Gemini-to-string-parser chain."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ConfigurationError(
            "Gemini API key is missing. Add GEMINI_API_KEY to your .env file, then restart the app."
        )

    model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash").strip()
    if not model_name:
        raise ConfigurationError("GEMINI_MODEL is empty. Set it in your .env file.")

    model = ChatGoogleGenerativeAI(
        model=model_name,
        thinking_level="low",
        max_output_tokens=700,
        timeout=45,
        max_retries=0,
    )
    return PROMPT | model | StrOutputParser()


def _question_inputs(
    question: str,
    *,
    role: str = "Not specified",
    level: str = "Early career",
    interview_type: str = "Mixed practice",
    history: str = "No previous conversation.",
) -> dict[str, str]:
    """Validate and prepare inputs shared by streaming and non-streaming calls."""
    question = question.strip()
    if not question:
        raise ValueError("Please enter a question before submitting.")
    if len(question) > 4000:
        raise ValueError("Please keep your question under 4,000 characters.")

    return {
        "question": question,
        "role": role.strip() or "Not specified",
        "level": level,
        "interview_type": interview_type,
        "history": history[-3000:],
    }


def stream_answer(
    question: str,
    *,
    role: str = "Not specified",
    level: str = "Early career",
    interview_type: str = "Mixed practice",
    history: str = "No previous conversation.",
):
    """Yield answer text as Gemini generates it."""
    yield from build_chain().stream(
        _question_inputs(
            question,
            role=role,
            level=level,
            interview_type=interview_type,
            history=history,
        )
    )


def answer_question(
    question: str,
    *,
    role: str = "Not specified",
    level: str = "Early career",
    interview_type: str = "Mixed practice",
    history: str = "No previous conversation.",
) -> str:
    """Generate a tailored interview-preparation answer."""
    response = "".join(
        stream_answer(
            question,
            role=role,
            level=level,
            interview_type=interview_type,
            history=history,
        )
    )
    if not response.strip():
        raise RuntimeError("The model returned an empty response. Please try again.")
    return response.strip()


def main() -> None:
    """Small terminal interface for quick use without Streamlit."""
    print("Interview Prep Bot — type 'quit' to exit")
    role = input("Target role (e.g. Python developer): ").strip() or "Not specified"
    level = input("Experience level (e.g. Entry level): ").strip() or "Early career"
    while True:
        question = input("\nYour interview question: ").strip()
        if question.lower() in {"quit", "exit"}:
            break
        try:
            print("\nCoach:\n" + answer_question(question, role=role, level=level))
        except (ConfigurationError, ValueError, RuntimeError) as exc:
            print(f"\nCould not generate an answer: {exc}")
        except Exception as exc:  # Covers provider/network errors with a friendly CLI message.
            print(f"\nGemini request failed ({type(exc).__name__}). Check your key, connection, and model name, then try again.")


if __name__ == "__main__":
    main()
