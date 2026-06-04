import uvicorn
from database import get_db
from fastapi import FastAPI, Depends
from fastapi.responses import Response
from routers import submissions, nominations
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

app = FastAPI()


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


@app.get("/metrics")
def get_metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


app.include_router(submissions.router)
app.include_router(nominations.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
