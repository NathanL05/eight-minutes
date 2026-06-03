from fastapi import APIRouter, Depends
from models import SubmissionRequest, SubmissionResponse
from database import get_db

router = APIRouter()

@router.post("/submit", response_model=SubmissionResponse)
def create_submission(submission: SubmissionRequest, conn = Depends(get_db)):
    cur = conn.cursor()
    cur.execute("SELECT id from challenges WHERE name = (%s)", (submission.challenge,))
    challenge_id = cur.fetchone()[0]
    cur.execute("INSERT INTO submissions (challenge_id, name, answers) VALUES (%s, %s, %s) RETURNING id, challenge_id, name, answers, created_at", (challenge_id, submission.name, submission.answers))
    conn.commit()

    row = cur.fetchone()
    new_submission = SubmissionResponse(id=row[0], challenge=submission.challenge, name=row[2], answers=row[3])

    return new_submission

@router.get("/submissions", response_model=list[SubmissionResponse])
def get_submission(conn = Depends(get_db)):
    cur = conn.cursor()
    cur.execute("SELECT s.id, c.name as challenge, s.name, s.answers FROM submissions s JOIN challenges c ON s.challenge_id = c.id")
    
    rows = cur.fetchall()
    submissions = [SubmissionResponse(id=row[0], challenge=row[1], name=row[2], answers=row[3]) for row in rows]

    return submissions
 