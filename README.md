# EightMinute — Viral Challenge Platform

> Inspired by Fidelity Investments' Elephant in the Room mental-health awareness initiative.

A web platform for the **8-Minute Challenge** — a mental-health awareness concept with viral, ice-bucket-style nomination mechanics. Users pick one of three 8-minute challenges (ice bath, treadmill, or hot wings), answer short reflective questions, nominate someone else, and submit. Submissions and per-challenge counts are tracked on a live dashboard.

---

## What's built today

A containerised FastAPI application backed by PostgreSQL, with a server-rendered HTMX/Jinja2 frontend and a CI/CD pipeline that builds and publishes the image to GHCR.

```
Browser
  │  (HTMX requests)
  ▼
FastAPI (Jinja2 + HTMX)  :8000  ────►  PostgreSQL
  │                                     (challenges, submissions, nominations)
  └── /metrics  (prometheus_client)

CI/CD: GitHub Actions ── flake8 + pytest ──► build image ──► push to GHCR (on merge to main)
```

## Stack

| Layer        | Tool                          |
|--------------|-------------------------------|
| Backend API  | Python + FastAPI              |
| Frontend     | HTMX + Jinja2 (server-rendered)|
| Database     | PostgreSQL 17 (psycopg2 pool) |
| Metrics      | `prometheus_client` `/metrics` endpoint |
| CI/CD        | GitHub Actions + GHCR         |
| Runtime      | Docker Compose                |

## Data model

- **challenges** — the three fixed challenge types (`CHECK` constraint).
- **submissions** — a participant's entry, foreign-keyed to a challenge, with their reflective answers.
- **nominations** — who a submission nominated (name + email), foreign-keyed to the submission.

## API surface

| Method | Path               | Purpose                                    |
|--------|--------------------|--------------------------------------------|
| GET    | `/`                | Home page                                  |
| GET    | `/challenge`       | Challenge page                             |
| POST   | `/submit/form`     | Submit a challenge entry + nomination      |
| GET    | `/stats`           | Per-challenge submission counts (JSON)     |
| GET    | `/partials/stats`  | Live stats partial (HTMX)                  |
| GET    | `/partials/feed`   | Latest submissions feed partial (HTMX)     |
| GET    | `/health`          | Health check                               |
| GET    | `/metrics`         | Prometheus metrics endpoint                |

## Run locally

Requires Docker and a `.env` file with `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`.

```bash
docker compose up --build      # start API + PostgreSQL
# visit http://localhost:8000
docker compose down            # stop
```

Run the tests:

```bash
cd api && pytest
```

---

## Roadmap (planned, not yet implemented)

This project is a work in progress. The following are designed but **not yet built** — they are the next phases, not current features:

- Observability stack: Prometheus scraping + Grafana dashboards + Loki/Promtail log aggregation
- Nginx reverse proxy with TLS and rate limiting
- k6 load test simulating a viral traffic burst
- Chaos experiments (DB/API failure injection) + a written post-mortem
- Terraform deployment to AWS EC2

The `/metrics` endpoint is already exposed in preparation for the observability work.
