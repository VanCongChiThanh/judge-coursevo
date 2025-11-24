from fastapi import APIRouter, HTTPException, Header, Depends
from services.gemini_service import process_courses

router = APIRouter()
@router.post("/run")
async def run_full_embedding():
    """
    Gọi service process_courses() để tạo embedding cho TẤT CẢ khóa học
    (insert hoặc update nếu đã có)
    """
    await process_courses()
    return {"message": "Embedding process started and completed."}