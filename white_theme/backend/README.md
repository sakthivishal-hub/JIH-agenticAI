# OpportunityOS — run it

## 1. Backend (FastAPI) + Frontend (served by the same app)

```bash
cd backend
pip install -r requirements.txt --break-system-packages   # or use a venv
alembic upgrade head        # creates/updates tables in DATABASE_URL from .env
uvicorn app.main:app --reload --port 8000
```

Then open **http://localhost:8000/app/** — that's the full website
(sign up, upload a resume, search, get AI matches, save/bookmark, set
email/WhatsApp alerts).

The raw API lives at http://localhost:8000 (e.g. `/docs` for the
interactive Swagger UI) — the frontend just calls it over fetch().

## 2. What's already configured in your `.env`
Database, JWT secret, Tavily, JSearch and Gemini keys are filled in.
`SMTP_*` (email alerts) and `TWILIO_*` (WhatsApp alerts) are empty, so
those two channels currently no-op safely (logged, not sent) until you
fill them in — everything else works without them.

## 3. Deploying it
This wasn't deployed from here (no outbound network in this environment),
but it's a single process now, so any host that runs a Python web
service works the same way locally and in production:
- **Render / Railway / Fly.io**: point at `backend/`, build command
  `pip install -r requirements.txt`, start command
  `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Set the same env
  vars from your `.env` in the host's dashboard (never commit `.env`).
- Postgres: point `DATABASE_URL` at a managed Postgres instance (Render/
  Railway/Neon all have a free tier), then run `alembic upgrade head`
  once against it.
