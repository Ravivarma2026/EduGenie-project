"""API tests. Gemini is mocked, so no API key or internet is needed.

Run:  pytest -v
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["EXPLAIN_BACKEND"] = "gemini"

import pytest
from fastapi.testclient import TestClient

import gemini_client
import main
import quiz_module

client = TestClient(main.app)

SAMPLE_QUIZ = [
    {"question": f"Question {i}?", "options": ["A1", "B1", "C1", "D1"], "answer": "B1"}
    for i in range(3)
]


@pytest.fixture(autouse=True)
def fake_gemini(monkeypatch):
    def fake_generate(prompt, json_mode=False):
        if json_mode:
            return "```json\n" + json.dumps(SAMPLE_QUIZ) + "\n```"
        return "Mocked Gemini answer"

    monkeypatch.setattr(gemini_client, "generate", fake_generate)
    for module in ("qna", "summary_module", "learning_path", "quiz_module", "explanation_module"):
        monkeypatch.setattr(f"{module}.generate", fake_generate)


def test_home_page():
    r = client.get("/")
    assert r.status_code == 200 and "EduGenie" in r.text


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_qa():
    r = client.get("/qa", params={"question": "Which is the largest ocean?"})
    assert r.status_code == 200 and r.json()["answer"] == "Mocked Gemini answer"


def test_explain_and_validation():
    r = client.post("/explain/", json={"topic": "gravity"})
    assert r.status_code == 200 and r.json()["explanation"]
    assert client.post("/explain/", json={"topic": ""}).status_code == 400


def test_summarize():
    r = client.post("/summarize/", json={"text": "Long text " * 20})
    assert r.status_code == 200 and "summary" in r.json()


def test_quiz_shape():
    r = client.post("/quiz", json={"text": "Pythagoras theorem"})
    quiz = r.json()["quiz"]
    assert r.status_code == 200 and len(quiz) == 3
    assert all(len(q["options"]) == 4 and q["answer"] in q["options"] for q in quiz)


def test_learning_path():
    r = client.post("/learn/recommendations", json={"topic": "SQL"})
    assert r.status_code == 200 and "recommendations" in r.json()


def test_quiz_letter_answer_is_normalized():
    raw = [{"question": "Q?", "options": ["w", "x", "y", "z"], "answer": "C"}]
    assert quiz_module._normalize(raw)[0]["answer"] == "y"


def test_missing_api_key_returns_503(monkeypatch):
    def boom(*a, **k):
        raise gemini_client.GeminiError("GEMINI_API_KEY is not set.")

    monkeypatch.setattr("qna.generate", boom)
    r = client.get("/qa", params={"question": "hi"})
    assert r.status_code == 503 and "GEMINI_API_KEY" in r.json()["error"]
