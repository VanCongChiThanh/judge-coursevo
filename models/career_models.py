from pydantic import BaseModel
from typing import Dict, Any

class CareerPlanRequest(BaseModel):
    role: str
    goal: str
    answers: Dict[str, Any]
