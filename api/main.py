import uvicorn
from fastapi import FastAPI
from fastapi.responses import Response
from routers import submissions, nominations
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

app = FastAPI()


@app.get("/health")
def health_status():
    return {"status": "ok"}


@app.get("/stats")
def get_stats():
    stats = {"ice bucket": 0, "treadmill": 0, "hot wings": 0}

    submissions_list = submissions.submissions_db

    for submission in submissions_list:
        stats[submission.challenge] += 1

    return stats


@app.get("/metrics")
def get_metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


app.include_router(submissions.router)
app.include_router(nominations.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
