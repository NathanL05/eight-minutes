# EightMinute — Concept & Overview

## How it works (user flow)

1. User picks one of three challenges: **ice bath**, **treadmill**, or **hot wings**.
2. User answers **8 short reflective questions** tied to mental health awareness.
3. User **nominates** someone else (name + email captured) to do the same.
4. The submission, its answers, and the nomination post to a **live public dashboard**, where others can like and comment on it.

## Data model (as built)

- `challenges` — the 3 fixed challenge types.
- `submissions` — submitter name, the 8 answers, like count.
- `comments` — free-text public comments on a submission.
- `nominations` — nominee **name and email**, linked to the submission that named them.

## Architecture & stack (prototype)

| Layer          | Tool                           |
|----------------|--------------------------------|
| Backend API    | Python + FastAPI               |
| Frontend       | HTMX + Jinja2 + Tailwind CSS   |
| Database       | PostgreSQL                     |
| Reverse proxy  | Nginx (TLS, rate limiting) — *designed, not yet deployed* |
| Observability  | Prometheus + Grafana + Loki    |
| CI/CD          | GitHub Actions + GHCR          |
| IaC            | Terraform (AWS EC2, free tier) — *scaffolded, not yet run for real* |
| Local runtime  | Docker Compose + Cloudflare Tunnel (demo only) |

## What's needed before this could go live

The prototype proves the concept but is missing things a real public campaign — especially one collecting health-related reflections and a third party's contact details — would need:

- **No authentication** on any submission, comment, or nomination endpoint.
- **No abuse/spam protection.** The "author" name on submissions and comments is free text with no verification — anyone can post as anyone.
- **No rate limiting in the running app.** Nginx rate limiting exists only in the (unused) AWS/Terraform path, not in the current Docker Compose setup.
- **No content moderation** on public comments, submissions, or the reflective answers shown on the dashboard.
- **Nominations capture a third party's name and email without their consent** — this needs a data-privacy/safeguarding and consent-flow review before any real use, especially given the mental-health subject matter.
- **No persistent hosting.** The only current public access is a Cloudflare *Quick Tunnel*, intended for demos — it's ephemeral (URL changes every restart) and has no uptime guarantee.
- **No legal/brand sign-off** for using the Fidelity Investments or Elephant in the Room names in a live product.

## Recommendation

Use this as the starting concept and architecture for a from-scratch build on your side, rather than taking the current code as-is into production. Happy to walk through the idea or answer questions on what was prototyped.
