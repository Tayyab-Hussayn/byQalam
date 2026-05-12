# Qalam Backend

FastAPI backend for Qalam.

## Local Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

## Validation

```bash
python -m pytest -q
python -m ruff check .
```

## Docker

Build the backend image:

```bash
docker build -t qalam-backend .
```

Run the API, worker, beat, Postgres, and Redis locally:

```bash
docker compose up --build
```

## Backups

Backup and restore guidance lives in [BACKUP_STRATEGY.md](./BACKUP_STRATEGY.md).

## Plan Limits

Plan defaults live in `.env` for bootstrapping. Runtime quota checks use database rows.

After changing plan defaults, sync them into the database:

```bash
python -m app.scripts.sync_plan_limits
```

## Workers

Scheduled LinkedIn publishing runs through Celery. Start Redis first, then run:

```bash
celery -A app.workers.celery_app.celery_app worker --loglevel=INFO
```

Trigger one scanner pass manually:

```bash
celery -A app.workers.celery_app.celery_app call qalam.publish_due_scheduled_posts
```
