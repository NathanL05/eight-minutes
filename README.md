# EightMinute — Viral Challenge Platform

> Elephant in the Room | Skills-Based Volunteering Project

A platform for the **8-Minute Challenge** — a viral mental health awareness campaign in partnership with Fidelity Investments and the Elephant in the Room charity.

Users pick one of three 8-minute challenges (ice bath, treadmill, or hot wings), answer 8 short reflective questions tied to mental health awareness, nominate someone else, and submit. All completions and nominations are tracked on a live public dashboard. The mechanic mirrors the ice-bucket challenge. Designed to handle viral traffic spikes.

---

## Architecture

```
GitHub Push
  │
  ▼
GitHub Actions CI (lint → test → build → push image to GHCR)
  │
  ▼ (on main merge)
AWS EC2 t2.micro  ←──── Terraform provisions this
  │
  ▼
Nginx (TLS, rate limiting, static files)
  │
  ├── /          → Frontend (HTMX + Jinja2 + Tailwind CSS)
  └── /api/      → Python API (FastAPI)
                        │
                        ├── PostgreSQL (challenges, submissions, nominations)
                        └── /metrics  → Prometheus → Grafana
                                                        │
                                              Loki ← Promtail ← API logs
```

---

## Stack

| Layer          | Tool                           |
|----------------|--------------------------------|
| Backend API    | Python + FastAPI               |
| Frontend       | HTMX + Jinja2 + Tailwind CSS   |
| Database       | PostgreSQL                     |
| Reverse proxy  | Nginx (TLS, rate limiting)     |
| Observability  | Prometheus + Grafana + Loki    |
| Load testing   | k6                             |
| CI/CD          | GitHub Actions + GHCR          |
| IaC            | Terraform (AWS EC2, free tier) |
| Local runtime  | Docker Compose                 |

---

## How to Run (local)

```bash
make up        # start the full stack
make down      # stop everything
make logs      # tail API logs
make load-test # run k6 viral burst simulation
make chaos-db  # kill postgres, observe recovery
make chaos-api # kill api, observe recovery
```

## How to Deploy (AWS)

```bash
make tf-init   # initialise Terraform
make tf-plan   # preview what will be created
make tf-apply  # provision EC2 + security group + Elastic IP
make tf-destroy # tear down after demo — always run this
```

---