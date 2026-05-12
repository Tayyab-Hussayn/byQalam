# Qalam Backup Strategy

## Goals

- Keep a restorable copy of the PostgreSQL database.
- Make backups easy to run locally, in containers, and in scheduled jobs.
- Keep the procedure simple enough to automate before launch.

## Current Approach

- Use `pg_dump` against the configured `DATABASE_URL`.
- Write backups as custom-format dump files.
- Store the output in a timestamped backup directory.
- Keep runtime secrets out of the dump process.

## Backup Command

```bash
python -m app.scripts.backup_database
```

Optional output directory:

```bash
BACKUP_OUTPUT_DIR=/path/to/backups python -m app.scripts.backup_database
```

## Operational Notes

- Run backups on a schedule from a cron job, task runner, or orchestration layer.
- Keep multiple historical backups instead of a single overwrite-only file.
- Store copies off-box in object storage or another durable location.
- Test restores on a separate database before trusting the backups.

## Restore Note

Custom-format dumps can be restored with `pg_restore` into a fresh PostgreSQL
database.
