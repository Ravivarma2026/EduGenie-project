"""Concept explanation module.

Uses the local LaMini-Flan-T5-783M model (CPU friendly) when available and
automatically falls back to Gemini so the feature always works.
"""
import os
import threading

from gemini_client import generate

BACKEND = os.getenv("EXPLAIN_BACKEND", "auto").strip().lower()
LOCAL_MODEL_NAME = os.getenv("LOCAL_MODEL_NAME", "MBZUAI/LaMini-Flan-T5-783M").strip()

_pipe = None
_pipe_failed = False
_lock = threading.Lock()


def _load_local_pipeline():
    """Lazy-load the local model once. Returns None if unavailable."""
    global _pipe, _pipe_failed
    if _pipe is not None or _pipe_failed:
        return _pipe
    with _lock:
        if _pipe is not None or _pipe_failed:
            return _pipe
        try:
            from transformers import pipeline

            print(f"Loading local model {LOCAL_MODEL_NAME} (first run downloads it)...")
            _pipe = pipeline("text2text-generation", model=LOCAL_MODEL_NAME)
        except Exception as exc:
            print(f"Local model unavailable ({exc}); using Gemini for explanations.")
            _pipe_failed = True
    return _pipe


def _explain_local(topic: str):
    pipe = _load_local_pipeline()
    if pipe is None:
        return None
    prompt = f"Explain the concept of '{topic}' in simple words for a beginner student."
    out = pipe(
        prompt,
        max_new_tokens=256,
        do_sample=False,
        no_repeat_ngram_size=3,
        repetition_penalty=1.2,
    )
    text = out[0]["generated_text"].strip()
    return text or None


def _explain_gemini(topic: str) -> str:
    prompt = (
        f"Explain the concept of '{topic}' in very simple language for a beginner student. "
        "Use a short analogy or everyday example, and keep it under 150 words."
    )
    return generate(prompt)


def explain_topic(topic: str) -> str:
    if BACKEND != "gemini":
        try:
            result = _explain_local(topic)
            if result:
                return result
        except Exception as exc:
            print(f"Local explanation failed ({exc}); falling back to Gemini.")
    return _explain_gemini(topic)
