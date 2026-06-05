from pydantic import BaseModel, Field
from typing import Literal, Optional


class SubmissionRequest(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    challenge: Literal["ice bath", "hot wings", "treadmill"]
    answers: list[str] = Field(..., min_length=8, max_length=8)


class SubmissionResponse(SubmissionRequest):
    id: int


class NominationRequest(BaseModel):
    name: str
    email: str
    submission_id: int


class NominationResponse(NominationRequest):
    id: int
