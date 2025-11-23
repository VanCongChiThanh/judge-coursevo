from fastapi import APIRouter, HTTPException, Header, Depends
from models.judge_models import TestCodeRequest, SubmitCodeRequest
from models.db_models import CodeSubmission, OAuthAccessToken
from services import judge0_serivce, gemini_service
from utils.jwt_utils import decode_jwt  # type: ignore
from controllers.database import get_db
from sqlalchemy.orm import Session

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
        expected_output=request.expected_output,
    )

    return {"judge_result": result}


@router.post("/multi-test")  # API chạy nhiều test case
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
    return {"judge_results": result}


@router.post("/submit")
def submit_code(
    request: SubmitCodeRequest,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    """
    API nộp bài — gọi Judge0 chạy code và Gemini để chấm
    """
    user = None
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Authorization header missing or invalid"
        )
    try:
        token = authorization.replace("Bearer ", "")
        user = decode_jwt(token)
        print("Decoded user from JWT:", user)

        if user is None:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    # 1️⃣ Gọi Judge0 để chạy code
    judge_result = judge0_serivce.run_code(
        language_id=request.language_id,
        source_code=request.source_code,
        stdin=request.stdin,
        expected_output=request.expected_output,
    )

    # 2️⃣ Gọi Gemini để phân tích & feedback (bỏ qua nếu thất bại)
    feedback = None
    try:
        feedback = gemini_service.get_feedback(
            source_code=request.source_code,
            problem_description=request.problem_description,
            expected_output=request.expected_output,
            judge_output=judge_result.get("stdout", ""),
        )
    except Exception as e:
        # Log lỗi nhưng không làm gián đoạn API
        print(f"⚠️ Gemini feedback failed: {str(e)}")
        feedback = {
            "error": "Gemini service unavailable",
            "message": "Code was judged successfully but AI feedback is temporarily unavailable",
        }

    # 3️⃣ Lưu kết quả vào database
    points = 0
    # Giả sử nếu status là "Accepted" thì được điểm của test case
    # Bạn cần logic phức tạp hơn để lấy điểm từ bảng code_test_cases
    if judge_result.get("status", {}).get("description") == "Accepted":
        points = 10  # Điểm ví dụ

    new_submission = CodeSubmission(
        # user_id=user["sub"],
        exercise_id=request.exercise_id,  # Cần thêm exercise_id vào SubmitCodeRequest
        source_code=request.source_code,
        language_id=request.language_id,
        status=judge_result.get("status", {}).get("description", "Error"),
        execution_time=judge_result.get("time"),
        memory_usage=judge_result.get("memory"),
        stdout=judge_result.get("stdout"),
        stderr=judge_result.get("stderr"),
        gemini_feedback=feedback,
        points_achieved=points,
    )

    # Lấy user_id từ oauth_access_tokens
    access_token_id = user.get("sub")
    access_token_entry = (
        db.query(OAuthAccessToken)
        .filter(OAuthAccessToken.id == access_token_id)
        .first()
    )

    if not access_token_entry or not access_token_entry.user_id:
        raise HTTPException(
            status_code=401, detail="Could not identify user from token"
        )

    new_submission.user_id = access_token_entry.user_id

    db.add(new_submission)
    db.commit()

    return {"judge_result": judge_result, "feedback": feedback}
