from fastapi import APIRouter
from models import Nomination

router = APIRouter()

nominations_db: list[Nomination] = []


@router.post("/nominate", response_model=Nomination)
def create_nomination(nomination: Nomination):
    nominations_db.append(nomination)
    return nomination


@router.get("/nominations", response_model=list[Nomination])
def get_nominations():
    return nominations_db
