# Project State

## Recent Updates
- **Phase C2 Complete**:
    - Scaffolded Frontend (Vite + React + TS + Tailwind).
    - Implemented Core Routes (`/login`, `/envelopes`, `/threads/:id`).
    - Implemented Core Components (`TurnBudget`, `BlurReveal`, `InstallPrompt`).
    - Implemented WebSocket Client (`ThreadSocket`).
- **Backend Refinement**:
    - Verified `infra/docker-compose.yml`: Postgres+pgvector, Redis, Healthchecks present.
    - Updated `Makefile`: Added `makemigrations` and `smoke` targets.
    - Smoke tested local dev environment readiness.
- **Phase C1 Complete**:
    - Improved `docker-compose.yml` (networks, restart policy, pgvector).
    - Added `backend/Dockerfile.dev` and root `Makefile`.
    - Added GitHub Actions for backend (CI/Lint) and frontend (Placeholder).
    - Updated `SECURITY.md` with secret scanning guidance.

## Current Status
- **DevOps**: CI pipelines active. Local dev UX hardened.
- **Backend**: Foundations solid.
- **Frontend**: PWA Foundation ready. Routes and components implemented.
- **Infrastructure**: Docker Compose (PG+Redis) healthy.
