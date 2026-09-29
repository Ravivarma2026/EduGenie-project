@echo off
REM One-click setup + run for Windows
cd /d "%~dp0"
if not exist .venv ( py -3 -m venv .venv || python -m venv .venv )
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if not exist .env copy .env.example .env
echo.
echo Open http://127.0.0.1:8000  (edit .env first and add GEMINI_API_KEY)
uvicorn main:app --reload
