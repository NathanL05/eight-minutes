from datetime import datetime, timezone

import uvicorn
from database import get_db
from fastapi import FastAPI, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response
from routers import submissions, nominations
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def _time_ago(dt):
    """Render a TIMESTAMPTZ as a friendly relative label (e.g. '5m ago')."""
    if dt is None:
        return ""
    seconds = (datetime.now(timezone.utc) - dt).total_seconds()
    if seconds < 60:
        return "just now"
    if seconds < 3600:
        return f"{int(seconds // 60)}m ago"
    if seconds < 86400:
        return f"{int(seconds // 3600)}h ago"
    return f"{int(seconds // 86400)}d ago"


@app.get("/health")
def health_status():
    return {"status": "ok"}


@app.get("/stats")
def get_stats(conn=Depends(get_db)):
    cur = conn.cursor()
    cur.execute("""
        SELECT c.name, COUNT(s.id)
        FROM challenges c LEFT JOIN submissions s ON c.id = s.challenge_id
        GROUP BY c.name
        """)
    rows = cur.fetchall()
    stats = {r[0]: r[1] for r in rows}
    return stats


@app.get("/stats/timeseries")
def get_stats_timeseries(conn=Depends(get_db)):
    """Cumulative participant count bucketed by day, for the homepage growth chart.

    Bucketing by day (rather than one point per submission) means an accelerating
    sign-up rate actually shows up as an upward curve, not a straight line.
    """
    cur = conn.cursor()
    cur.execute(
        """
        SELECT created_at::date AS day, COUNT(*)
        FROM submissions
        GROUP BY day
        ORDER BY day ASC
        """
    )
    rows = cur.fetchall()
    labels = []
    data = []
    running = 0
    for day, count in rows:
        running += count
        labels.append(day.strftime("%b %d") if day else "")
        data.append(running)
    return {"labels": labels, "data": data}


@app.get("/partials/stats")
def get_partial_stats(request: Request, conn=Depends(get_db)):
    cur = conn.cursor()
    cur.execute("""
        SELECT c.name, COUNT(s.id)
        FROM challenges c LEFT JOIN submissions s ON c.id = s.challenge_id
        GROUP BY c.name
        """)
    rows = cur.fetchall()
    stats = {r[0]: r[1] for r in rows}
    return templates.TemplateResponse(
        request, "partials/stats.html", {"request": request, "stats": stats}
    )


PAGE_SIZE = 5


@app.get("/partials/feed")
def get_partial_feed(
    request: Request,
    offset: int = 0,
    limit: int = PAGE_SIZE,
    more: int = 0,
    conn=Depends(get_db),
):
    limit = max(1, min(limit, 50))
    offset = max(0, offset)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM submissions")
    total = cur.fetchone()[0]
    cur.execute(
        """
        SELECT s.id, s.name, c.name, s.created_at, s.likes
        FROM submissions s LEFT JOIN challenges c ON s.challenge_id = c.id
        ORDER BY s.created_at DESC
        OFFSET %s LIMIT %s
        """,
        (offset, limit),
    )
    rows = cur.fetchall()
    submissions = [
        {
            "id": r[0],
            "name": r[1],
            "challenge": r[2],
            "created_at": r[3],
            "created_label": _time_ago(r[3]),
            "likes": r[4],
            "comments": [],
        }
        for r in rows
    ]

    # Attach comments for the visible submissions in a single query.
    by_id = {s["id"]: s for s in submissions}
    if by_id:
        cur.execute(
            """
            SELECT submission_id, author, body, created_at
            FROM comments
            WHERE submission_id = ANY(%s)
            ORDER BY created_at ASC
            """,
            (list(by_id.keys()),),
        )
        for sub_id, author, body, created_at in cur.fetchall():
            by_id[sub_id]["comments"].append(
                {"author": author, "body": body, "created_label": _time_ago(created_at)}
            )

    next_offset = offset + len(rows)
    template = "partials/feed_more.html" if more else "partials/feed.html"
    return templates.TemplateResponse(
        request,
        template,
        {
            "submissions": submissions,
            "has_more": next_offset < total,
            "next_offset": next_offset,
            "limit": limit,
        },
    )


@app.post("/partials/submissions/{submission_id}/like")
def like_submission(submission_id: int, request: Request, conn=Depends(get_db)):
    cur = conn.cursor()
    cur.execute(
        "UPDATE submissions SET likes = likes + 1 WHERE id = %s RETURNING likes",
        (submission_id,),
    )
    row = cur.fetchone()
    if row is None:
        conn.rollback()
        return Response(status_code=404)
    conn.commit()
    return templates.TemplateResponse(
        request,
        "partials/like_button.html",
        {"submission_id": submission_id, "likes": row[0]},
    )


@app.post("/partials/submissions/{submission_id}/comment")
async def comment_submission(
    submission_id: int, request: Request, conn=Depends(get_db)
):
    form = await request.form()
    body = (form.get("body") or "").strip()[:280]
    author = (form.get("author") or "").strip()[:40] or "Anonymous"
    if not body:
        return Response(status_code=204)

    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO comments (submission_id, author, body)
        VALUES (%s, %s, %s)
        RETURNING author, body, created_at
        """,
        (submission_id, author, body),
    )
    row = cur.fetchone()
    conn.commit()
    comment = {"author": row[0], "body": row[1], "created_label": _time_ago(row[2])}
    return templates.TemplateResponse(
        request, "partials/comment.html", {"comment": comment}
    )


@app.get("/metrics")
def get_metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/")
def home_page(request: Request, conn=Depends(get_db)):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM submissions")
    total = cur.fetchone()[0]
    return templates.TemplateResponse(
        request,
        "index.html",
        {"page_size": PAGE_SIZE, "show_load_more": total > PAGE_SIZE},
    )


@app.get("/challenge")
def challenge_page(request: Request):
    return templates.TemplateResponse(request, "challenge.html")


@app.post("/submit/form")
async def submit_form(request: Request, conn=Depends(get_db)):
    cur = conn.cursor()
    form_data = await request.form()

    challenge = form_data["challenge"]
    answers = form_data.getlist("answers")
    name = form_data["name"]
    nominee_name = form_data["nominee_name"]
    email = form_data["nominee_email"]

    cur.execute(
        """
        SELECT id
        FROM challenges
        WHERE name = %s
        """,
        (challenge,),
    )
    challenge_id = cur.fetchone()[0]
    cur.execute(
        """
        INSERT INTO submissions (challenge_id, name, answers)
        VALUES (%s, %s, %s)
        RETURNING id
        """,
        (challenge_id, name, answers),
    )
    submission_id = cur.fetchone()[0]
    cur.execute(
        """
        INSERT INTO nominations (submission_id, name, email)
        VALUES (%s, %s, %s)
        """,
        (submission_id, nominee_name, email),
    )
    conn.commit()

    return templates.TemplateResponse(
        request,
        "partials/submit_success.html",
        {
            "submission_id": submission_id,
            "challenge": challenge,
            "nominee_name": nominee_name,
        },
    )


app.include_router(submissions.router)
app.include_router(nominations.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
