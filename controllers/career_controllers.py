from fastapi import APIRouter
from models.career_models import CareerPlanRequest
from services.gemini_service import generate_career_plan

router = APIRouter()
@router.post("/generate")
async def generate_plan(request: CareerPlanRequest):
    plan = await generate_career_plan(request)
    return {"status": "success", "data": plan}
