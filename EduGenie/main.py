"""EduGenie - Google Gemini powered learning assistant (FastAPI backend)."""
from pathlib import Path

from fastapi import FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from explanation_module import explain_topic
from gemini_client import MODEL_NAME, GeminiError
from learning_path import get_learning_recommendations
from qna import answer_question_with_gemini
from quiz_module import generate_quiz
from summary_module import summarize_text

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="EduGenie", description="Gemini powered learning assistant", version="1.0.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


class TopicRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=500)


class TextRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=20000)


def error_response(message: str, status_code: int) -> JSONResponse:
    return JSONResponse(content={"error": message}, status_code=status_code)


@app.exception_handler(GeminiError)
async def gemini_error_handler(request: Request, exc: GeminiError):
    return error_response(str(exc), 503)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return error_response("Please enter some text (it cannot be empty or too long).", 400)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {"model": MODEL_NAME})


@app.get("/health")
async def health():
    return {"status": "ok", "model": MODEL_NAME}


# ---------------------------- API ROUTES ----------------------------

# Q&A - GET API using Gemini
@app.get("/qa")
async def answer_question(question: str = Query(..., min_length=1, max_length=2000)):
    return {"question": question, "answer": answer_question_with_gemini(question)}


# Explanation - POST API
@app.post("/explain")
@app.post("/explain/", include_in_schema=False)
async def explain_api(payload: TopicRequest):
    topic = payload.topic.strip()
    if not topic:
        return error_response("Please provide a topic.", 400)
    return {"topic": topic, "explanation": explain_topic(topic)}


# Summarization - POST API
@app.post("/summarize")
@app.post("/summarize/", include_in_schema=False)
async def summarize_api(payload: TextRequest):
    text = payload.text.strip()
    if not text:
        return error_response("Please provide text to summarize.", 400)
    return {"summary": summarize_text(text)}


# Quiz generation - POST API
@app.post("/quiz")
@app.post("/quiz/", include_in_schema=False)
async def quiz_api(payload: TextRequest):
    text = payload.text.strip()
    if not text:
        return error_response("Please provide a passage or topic.", 400)
    return {"quiz": generate_quiz(text)}


# Learning recommendations - POST API
@app.post("/learn/recommendations")
@app.post("/learn/recommendations/", include_in_schema=False)
async def learning_api(payload: TopicRequest):
    topic = payload.topic.strip()
    if not topic:
        return error_response("Please provide a topic.", 400)
    return {"topic": topic, "recommendations": get_learning_recommendations(topic)}
