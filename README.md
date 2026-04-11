# AI Exam Preparation Strategy Planner

A deployment-ready Python project for generating personalized exam study strategies with AI. The app uses FastAPI on the backend, serves a browser UI, keeps Groq API calls on the server, and now includes user login, saved study plans, and PDF export.

## Features

- Python-first architecture with a clean `app/` package layout
- **Premium Glassmorphism UI** with a seamless Light/Dark mode toggle
- AI-powered strategy generation through `/api/generate-strategy` utilizing the latest Chat Completions SDK
- Server-side API key handling ensures secure communication with Groq
- Deterministic fallback mode when no AI key is configured
- Seamless **tab-based login and registration** flows
- SQLite persistence for saved study plans
- PDF export for the current generated plan or any saved plan
- Responsive UI built with Jinja2 templates and vanilla JavaScript
- Health check endpoint at `/health`

## Stack

- Python
- FastAPI
- Jinja2
- Vanilla JavaScript
- SQLite
- OpenAI Python SDK (used for Groq API)
- ReportLab

## Project Structure

```text
app/
  ai.py
  db.py
  main.py
  models.py
  pdf.py
  static/
    auth.js
    planner.js
    styles.css
  templates/
    login.html
    planner.html
requirements.txt
Procfile
runtime.txt
.env.example
```

## Local Setup

1. Create a virtual environment:

```bash
python -m venv .venv
```

2. Activate it.

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` and set:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
SESSION_SECRET=replace_with_a_long_random_secret
```

5. Run the app:

```bash
uvicorn app.main:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Environment Variables

- `GROQ_API_KEY`: required for live AI responses.
- `GROQ_MODEL`: optional model override (Defaults to `llama-3.1-8b-instant`).
- `SESSION_SECRET`: required in production for secure login sessions

## Deployment

This project is ready for Render, Railway, Heroku, or any platform that can run ASGI apps.

- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health check path: `/health`
- Persistent storage: `planner.db`
- Python version: see `runtime.txt`

## Notes

- The AI call is made on the backend, not in the browser.
- If `GROQ_API_KEY` is missing, the app still works using the fallback planner.
- Saved plans are tied to the logged-in user session.
- PDF export works for both the current generated plan and saved plans.
