"""Learning recommendation module (Gemini)."""
from gemini_client import generate


def get_learning_recommendations(topic: str) -> str:
    prompt = f"""
You are an AI tutor. The student wants to learn about: {topic}.
Suggest a structured and adaptive learning path including key topics, order of learning,
estimated timelines, and resources (links, videos, books, or courses).
Include beginner, intermediate, and advanced levels if needed.
Format the answer in Markdown with headings for each level, bullet points, and finish
with a short "Adaptive Learning Tips" section.
"""
    return generate(prompt)
