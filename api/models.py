from pydantic import BaseModel, Field
from typing import Literal, Optional


class SubmissionRequest(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    challenge: Literal["ice bath", "hot wings", "treadmill"]
    answers: list[str] = Field(..., min_length=8, max_length=8)

class SubmissionResponse(SubmissionRequest):
    id: int
class Nomination(BaseModel):
    nominee_name: str
    nominee_email: str
    submission_id: int
