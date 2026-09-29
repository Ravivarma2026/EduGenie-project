"""Question answering module (Gemini)."""
from gemini_client import generate


def answer_question_with_gemini(question: str) -> str:
    prompt = (
        "You are EduGenie, a friendly and accurate AI tutor. "
        "Answer the student's question clearly and concisely (2-5 sentences unless more "
        "detail is essential). If the question is ambiguous, state your assumption.\n\n"
        f"Question: {question}"
    )
    return generate(prompt)
