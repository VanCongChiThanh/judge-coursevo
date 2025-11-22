from fastapi import APIRouter, HTTPException, Header
from models.judge_models import TestCodeRequest, SubmitCodeRequest
from services import judge0_serivce, gemini_service
from utils.jwt_utils import decode_jwt

router = APIRouter()

@router.post("/test")
def test_code(request: TestCodeRequest, authorization: str = Header(None)):
    """
    API chạy test code (chỉ dùng Judge0)
    """
    # user = None
    # if authorization:
    #     try:
    #         print(authorization.replace("Bearer ", ""))
    #         user = decode_jwt(authorization.replace("Bearer ", ""))
    #     except Exception:
    #         raise HTTPException(status_code=401, detail="Invalid token")

    result = judge0_serivce.run_code(
        language_id=request.language_id,
        source_code=request.source_code,
        stdin=request.stdin,
        expected_output=request.expected_output
    )

    return {
        "judge_result": result
    }
    
@router.post("/multi-test") # API chạy nhiều test case
def multi_test_code(requests: list[dict], authorization: str = Header(None)):
    """
    API chạy nhiều test case (chỉ dùng Judge0)
    """
    # user = None
    # if authorization:
    #     try:
    #         user = decode_jwt(authorization.replace("Bearer ", ""))
    #     except Exception:
    #         raise HTTPException(status_code=401, detail="Invalid token")

    result = judge0_serivce.run_batch_code(requests)
    return {
        "judge_results": result
    }


@router.post("/submit")
def submit_code(request: SubmitCodeRequest, authorization: str = Header(None)):
    """
    API nộp bài — gọi Judge0 chạy code và Gemini để chấm
    """
    # user = None
    # if authorization:
    #     try:
    #         user = decode_jwt(authorization.replace("Bearer ", ""))
    #     except Exception:
    #         raise HTTPException(status_code=401, detail="Invalid token")

    # 1️⃣ Gọi Judge0 để chạy code
    judge_result = judge0_serivce.run_code(
        language_id=request.language_id,
        source_code=request.source_code,
        stdin=request.stdin,
        expected_output=request.expected_output
    )

    # 2️⃣ Gọi Gemini để phân tích & feedback (bỏ qua nếu thất bại)
    feedback = None
    try:
        feedback = gemini_service.get_feedback(
            source_code=request.source_code,
            problem_description=request.problem_description,
            expected_output=request.expected_output,
            judge_output=judge_result.get("stdout", "")
        )
    #Todo :call api luu ket qua submit
    
    except Exception as e:
        # Log lỗi nhưng không làm gián đoạn API
        print(f"⚠️ Gemini feedback failed: {str(e)}")
        feedback = {
            "error": "Gemini service unavailable",
            "message": "Code was judged successfully but AI feedback is temporarily unavailable"
        }

    # 3️⃣ Trả kết quả tổng hợp
    return {
        "judge_result": judge_result,
        "feedback": feedback
    }
