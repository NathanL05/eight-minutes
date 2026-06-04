from fastapi import APIRouter, Depends
from models import NominationRequest, NominationResponse
from database import get_db

router = APIRouter()


@router.post("/nominate", response_model=NominationResponse)
def create_nomination(nomination: NominationRequest, conn=Depends(get_db)):
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO nominations (submission_id, name, email) VALUES (%s, %s, %s) RETURNING id",
        (nomination.submission_id, nomination.name, nomination.email),
    )
    conn.commit()

    row = cur.fetchone()
    new_nomination = NominationResponse(
        id=row[0],
        name=nomination.name,
        email=nomination.email,
        submission_id=nomination.submission_id,
    )

    return new_nomination


@router.get("/nominations", response_model=list[NominationResponse])
def get_nominations(conn=Depends(get_db)):
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, submission_id FROM nominations")

    rows = cur.fetchall()
    nominations = [
        NominationResponse(id=row[0], name=row[1], email=row[2], submission_id=row[3])
        for row in rows
    ]
    return nominations
