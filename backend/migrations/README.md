# Database Migrations

Migrations are SQL files applied in order with `psql`. Files do not drop tables, data, or Docker volumes.

| Migration | File | Creates |
|---|---|---|
| 001 | `001_tool_calls.sql` | `tool_calls` (decision summaries) and its timestamp index |

## Apply a migration

From the repository root, start the database if it isn't running:

    docker compose up -d db

Apply migration 001 with the `psql` inside the database container:

    docker compose exec -T db psql -v ON_ERROR_STOP=1 -U agentguard -d agentguard < backend/migrations/001_tool_calls.sql

With `ON_ERROR_STOP=1`, `psql` stops at the first error and does not continue. The file runs in one transaction, so a failure does not leave anything half-applied and running it again is safe.

## Rules

- Do not run `docker compose down -v` or delete the `pgdata` volume to "reset" the database. That deletes all stored data.
- Migrations do not get applied automatically, for example on app startup or `/health`.
