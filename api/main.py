import uvicorn
from database import get_db
from fastapi import FastAPI, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import Response
from routers import submissions, nominations
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/health")
def health_status():
    return {"status": "ok"}


@app.get("/stats")
def get_stats(conn=Depends(get_db)):
    cur = conn.cursor()
    cur.execute(
        """
        SELECT c.name, COUNT(s.id)
        FROM challenges c LEFT JOIN submissions s ON c.id = s.challenge_id
        GROUP BY c.name
        """
    )
    rows = cur.fetchall()
    stats = {r[0]: r[1] for r in rows}
    return stats


@app.get("/partials/stats")
def get_partial_stats(request: Request, conn=Depends(get_db)):
    cur = conn.cursor()
    cur.execute(
        """
        SELECT c.name, COUNT(s.id)
        FROM challenges c LEFT JOIN submissions s ON c.id = s.challenge_id
        GROUP BY c.name
        """
    )
    rows = cur.fetchall()
    stats = {r[0]: r[1] for r in rows}
    return templates.TemplateResponse(
        request, "partials/stats.html", {"request": request, "stats": stats}
    )


@app.get("/partials/feed")
def get_partial_feed(request: Request, conn=Depends(get_db)):
    cur = conn.cursor()
    cur.execute(
        """
        SELECT s.name, c.name, s.created_at
        FROM submissions s LEFT JOIN challenges c ON s.challenge_id = c.id
        ORDER BY s.created_at DESC
        LIMIT 10
        """
    )
    rows = cur.fetchall()
    submissions = [{"name": r[0], "challenge": r[1], "created_at": r[2]} for r in rows]
    return templates.TemplateResponse(
        request, "partials/feed.html", {"submissions": submissions}
    )


@app.get("/metrics")
def get_metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/")
def home_page(request: Request):
    return templates.TemplateResponse(request, "index.html")


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
