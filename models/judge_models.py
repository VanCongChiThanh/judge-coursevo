from uuid import UUID
from pydantic import BaseModel


class TestCodeRequest(BaseModel):
    language_id: int
    source_code: str
    stdin: str | None = ""
    expected_output: str | None = ""


class SubmitCodeRequest(BaseModel):
    language_id: int
    source_code: str
    problem_description: str
    expected_output: str
    stdin: str | None = ""
    user_id: UUID | None = None
    exercise_id: UUID
