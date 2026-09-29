"""Summarization module (Gemini)."""
from gemini_client import generate


def summarize_text(text: str) -> str:
    prompt = (
        "Summarize the following educational text in simple language. Keep the core "
        "ideas, remove redundancy, and use short bullet points if it helps clarity.\n\n"
        f"{text}"
    )
    return generate(prompt)
