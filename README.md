# MyGarage UK

A UK-focused vehicle management platform for storing cars, viewing MOT history, tracking maintenance, and eventually generating useful vehicle insights from MOT and service data.

## Stack

- Frontend: Next.js + TypeScript + Tailwind CSS
- Backend: FastAPI + Python
- Database: PostgreSQL
- HTTP client: HTTPX
- Tests: Pytest
- Local infrastructure: Docker Compose

## Repository layout

- `frontend/` — web UI
- `backend/` — REST API and domain logic
- `docs/` — architecture notes, API decisions and project documentation
- `compose.yaml` — local PostgreSQL

## First local run

1. Copy `.env.example` to `.env`.
2. Start PostgreSQL:
   `docker compose up -d db`
3. Backend:
   - `cd backend`
   - `python -m venv .venv`
   - activate the virtual environment
   - `pip install -e ".[dev]"`
   - `uvicorn app.main:app --reload`
4. Frontend:
   - `cd frontend`
   - `npm install`
   - `npm run dev`
5. Open `http://localhost:3000` and FastAPI docs at `http://localhost:8000/docs`.

## MVP roadmap

1. Foundation: frontend, API, database and CI
2. Vehicle CRUD
3. DVSA MOT API integration
4. MOT history dashboard + mileage graph
5. Service history
6. Vehicle insights
7. Authentication
8. Reminders and notifications
