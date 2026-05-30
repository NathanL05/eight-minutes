from fastapi import APIRouter
from models import SubmissionRequest, SubmissionResponse

router = APIRouter()

submissions_db: list[SubmissionResponse] = []


@router.post("/submit", response_model=SubmissionResponse)
def create_submission(submission: SubmissionRequest):
    new_submission = SubmissionResponse(
        id=len(submissions_db) + 1, **submission.model_dump()
    )
    submissions_db.append(new_submission)
    return new_submission


@router.get("/submissions", response_model=list[SubmissionResponse])
def get_submission():
    return submissions_db
