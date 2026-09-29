"""Quiz generation module (Gemini). Produces 3 MCQs with 4 options each."""
import json

from gemini_client import GeminiError, clean_json_block, generate

NUM_QUESTIONS = 3
NUM_OPTIONS = 4


def _normalize(raw) -> list:
    """Validate the model output and guarantee a clean, predictable structure."""
    if isinstance(raw, dict):
        raw = raw.get("questions", [])
    if not isinstance(raw, list) or not raw:
        raise GeminiError("Quiz response was not a list of questions.")

    quiz = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        question = str(item.get("question", "")).strip()
        options = [str(o).strip() for o in item.get("options", []) if str(o).strip()]
        answer = str(item.get("answer", "")).strip()
        if not question or len(options) < 2:
            continue
        options = options[:NUM_OPTIONS]

        # Accept "A"/"B"/"C"/"D" or "1".."4" as the answer and map it to the option text.
        if answer not in options:
            key = answer.rstrip(".)").strip().upper()
            if len(key) == 1 and key in "ABCD" and ord(key) - 65 < len(options):
                answer = options[ord(key) - 65]
            elif key.isdigit() and 1 <= int(key) <= len(options):
                answer = options[int(key) - 1]
            else:
                lowered = [o.lower() for o in options]
                if answer.lower() in lowered:
                    answer = options[lowered.index(answer.lower())]
                else:
                    continue
        quiz.append({"question": question, "options": options, "answer": answer})

    if not quiz:
        raise GeminiError("Quiz response contained no valid questions.")
    return quiz[:NUM_QUESTIONS]


def generate_quiz(text: str) -> list:
    prompt = f"""
You are a quiz generator.

From the following passage or topic, create {NUM_QUESTIONS} multiple-choice questions.
Each question must include:
- A "question"
- A list of {NUM_OPTIONS} "options" (one correct, three plausible distractors)
- A correct "answer" that must exactly match one of the options.

Return ONLY valid JSON (no Markdown, no commentary), like this:
[
  {{
    "question": "What is ...?",
    "options": ["A", "B", "C", "D"],
    "answer": "A"
  }}
]

Passage or topic:
{text}
"""
    reply = generate(prompt, json_mode=True)
    cleaned = clean_json_block(reply)
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise GeminiError(f"Could not parse quiz JSON: {exc}. Raw reply: {cleaned[:200]}") from exc
    return _normalize(parsed)
