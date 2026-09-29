#!/usr/bin/env bash
# One-click setup + run for macOS / Linux
cd "$(dirname "$0")"
[ -d .venv ] || python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
[ -f .env ] || cp .env.example .env
echo
echo "Open http://127.0.0.1:8000  (edit .env first and add GEMINI_API_KEY)"
uvicorn main:app --reload
