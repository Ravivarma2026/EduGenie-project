"""Shared Google Gemini client used by every EduGenie module."""
import os
import re

from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip() or "gemini-2.5-flash"

_client = None


class GeminiError(Exception):
    """Raised for any problem talking to Gemini (missing key, API error, empty reply)."""


def _get_client():
    global _client
    if _client is not None:
        return _client
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        raise GeminiError(
            "GEMINI_API_KEY is not set. Copy .env.example to .env and add your key "
            "(https://aistudio.google.com/app/apikey), then restart the server."
        )
    try:
        from google import genai
    except ImportError as exc:  # pragma: no cover
        raise GeminiError(
            "The 'google-genai' package is not installed. Run: pip install -r requirements.txt"
        ) from exc
    _client = genai.Client(api_key=api_key)
    return _client


def generate(prompt: str, json_mode: bool = False) -> str:
    """Send a prompt to Gemini and return the response text."""
    client = _get_client()
    kwargs = {"model": MODEL_NAME, "contents": prompt}
    if json_mode:
        try:
            from google.genai import types

            kwargs["config"] = types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        except Exception:  # pragma: no cover - fall back to plain text mode
            pass
    try:
        response = client.models.generate_content(**kwargs)
    except Exception as exc:
        raise GeminiError(f"Gemini API error: {exc}") from exc

    text = getattr(response, "text", None)
    if not text or not text.strip():
        raise GeminiError("Gemini returned an empty response. Try rephrasing your input.")
    return text.strip()


def clean_json_block(text: str) -> str:
    """Strip Markdown ```json code fences from a model reply."""
    return re.sub(r"```(?:json)?\s*\n?(.*?)```", r"\1", text, flags=re.DOTALL).strip()
