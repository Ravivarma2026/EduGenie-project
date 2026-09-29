# EduGenie: Google Gemini Powered Learning Assistant

A lightweight AI learning assistant built with **FastAPI** and a dark neon **HTML/CSS/JS** frontend.

| Feature | Endpoint | Engine |
|---|---|---|
| Question answering | `GET /qa?question=...` | Gemini |
| Concept explanation | `POST /explain/` `{"topic": "..."}` | Local LaMini-Flan-T5-783M (optional), falls back to Gemini |
| Quiz (3 MCQs x 4 options) | `POST /quiz` `{"text": "..."}` | Gemini (JSON) |
| Summarization | `POST /summarize/` `{"text": "..."}` | Gemini |
| Learning path | `POST /learn/recommendations` `{"topic": "..."}` | Gemini |

Extra: `GET /health`, interactive API docs at `/docs`.

## Folder structure

```
EduGenie/
├── main.py                 # FastAPI app + routes
├── gemini_client.py        # shared Gemini client (reads .env)
├── explanation_module.py   # concept explanation (local T5 or Gemini)
├── qna.py                  # question answering
├── quiz_module.py          # quiz generation + validation
├── summary_module.py       # summarization
├── learning_path.py        # learning recommendations
├── templates/index.html    # frontend page
├── static/style.css        # styling
├── static/app.js           # frontend logic
├── tests/test_api.py       # automated tests (Gemini mocked)
├── requirements.txt        # core dependencies
├── requirements-local.txt  # optional: local LaMini-Flan-T5 model
├── requirements-dev.txt    # pytest + httpx
├── .env.example            # copy to .env and add your key
└── .vscode/                # launch, settings, extensions
```

## 1. Prerequisites

- **Python 3.10+** (check: `python --version`) - tick *Add Python to PATH* when installing
- **VS Code** with the *Python* extension
- A free **Gemini API key**: https://aistudio.google.com/app/apikey

## 2. Setup in VS Code

1. Unzip the project, then **File > Open Folder...** and select the `EduGenie` folder.
2. Open the terminal: **Terminal > New Terminal**.
3. Create and activate a virtual environment:
   - Windows (PowerShell): `python -m venv .venv` then `.venv\Scripts\Activate.ps1`
     (if blocked, run once: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`)
   - macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create your env file: copy `.env.example` to `.env` (`copy .env.example .env` on Windows,
   `cp .env.example .env` on macOS/Linux) and paste your key: `GEMINI_API_KEY=...`
6. Press `Ctrl+Shift+P` > **Python: Select Interpreter** > choose the `.venv` one.
   (On macOS/Linux, change the interpreter path in `.vscode/settings.json` to `.venv/bin/python`.)

Shortcut: double-click `run.bat` (Windows) or run `./run.sh` (macOS/Linux) to do steps 3-4 and start the server.

## 3. Run

```
uvicorn main:app --reload
```
Open **http://127.0.0.1:8000**. Or press **F5** in VS Code (uses `.vscode/launch.json`, debugger attached).

## 4. Test

Automated (no API key needed, Gemini is mocked):
```
pip install -r requirements-dev.txt
pytest -v
```

Manual, in the browser, try one task each:
1. **Ask a Question**: "Which is the largest ocean?"
2. **Explain**: "quantum computing"
3. **Generate Quiz**: "The Pythagoras Theorem" (answer options; wrong picks reveal the right answer and a score appears)
4. **Summarize**: paste a long paragraph
5. **Recommend Learning Path**: "SQL"

Or with curl:
```
curl "http://127.0.0.1:8000/qa?question=Which%20is%20the%20largest%20ocean%3F"
curl -X POST http://127.0.0.1:8000/quiz -H "Content-Type: application/json" -d "{\"text\":\"Pythagoras theorem\"}"
```
Swagger UI: http://127.0.0.1:8000/docs

## Optional: local explanation model (LaMini-Flan-T5-783M)

```
pip install -r requirements-local.txt
```
The first explanation downloads about 3 GB. With `EXPLAIN_BACKEND=auto` (default) EduGenie uses it when installed,
otherwise Gemini. Set `EXPLAIN_BACKEND=gemini` to skip it.

## Troubleshooting

| Problem | Fix |
|---|---|
| `GEMINI_API_KEY is not set` | Create `.env` from `.env.example`, add your key, restart the server |
| `404 model not found` | Set `GEMINI_MODEL` in `.env` to a current model (e.g. `gemini-2.5-flash`) |
| `429` quota errors | Free-tier rate limit: wait a minute and retry |
| `uvicorn` not recognized | Activate the virtual environment first |
| Port 8000 busy | `uvicorn main:app --reload --port 8001` |

Never commit `.env` or share your API key.
