import google.generativeai as genai
from utils.config import GEMINI_API_KEY
import json

genai.configure(api_key=GEMINI_API_KEY)

def get_feedback(source_code: str, problem_description: str, expected_output: str, judge_output: str):
    prompt = f"""
    Bạn là một giáo viên lập trình chuyên nghiệp. Hãy đánh giá code của học sinh.

    📝 **Đề bài:**
    {problem_description}

    💻 **Code của học sinh:**
    ```
    {source_code}
    ```

    ✅ **Kết quả mong đợi:**
    {expected_output}

    📊 **Kết quả thực tế từ Judge0:**
    {judge_output}

    Hãy trả về feedback dưới dạng JSON với cấu trúc sau (chỉ trả JSON, không thêm text khác):
    {{
        "score": 0-100,
        "summary": "Tóm tắt ngắn gọn về bài làm",
        "strengths": ["Điểm mạnh 1", "Điểm mạnh 2"],
        "weaknesses": ["Điểm yếu 1", "Điểm yếu 2"],
        "suggestions": ["Gợi ý cải thiện 1", "Gợi ý cải thiện 2"],
        "code_quality": {{
            "readability": 0-100 %,
            "efficiency": 0-100 %,
            "best_practices": 0-100 %
        }}
    }}

    **Yêu cầu:**
    - is_correct: true nếu output khớp hoàn toàn với expected_output
    - score: điểm tổng thể từ 0-100
    - summary: 1-2 câu tóm tắt
    - strengths: liệt kê các điểm tốt (tối thiểu 1-2 điểm)
    - weaknesses: liệt kê các vấn đề (nếu có, có thể để mảng rỗng nếu code hoàn hảo)
    - suggestions: đề xuất cải thiện (nếu có)
    - code_quality: đánh giá 3 tiêu chí từ 0-10

    Chỉ trả về JSON thuần, không thêm markdown hay text khác.
    """

    model = genai.GenerativeModel("gemini-2.0-flash-exp")
    response = model.generate_content(prompt)
    
    # Parse response text thành JSON
    try:
        # Loại bỏ markdown code block nếu có
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        feedback_json = json.loads(text)
        return feedback_json
    except json.JSONDecodeError:
        # Nếu Gemini không trả về JSON đúng format, wrap lại
        return {
            "is_correct": None,
            "score": 0,
            "summary": response.text,
            "strengths": [],
            "weaknesses": ["Không thể phân tích được feedback"],
            "suggestions": [],
            "code_quality": {
                "readability": 0,
                "efficiency": 0,
                "best_practices": 0
            }
        }
