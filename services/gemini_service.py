
from google import genai

import httpx
from services.db_service import upsert_course_vector
from utils.config import GEMINI_API_KEY, MAIN_SERVICE_URL
import json
import math

client = genai.Client(api_key=GEMINI_API_KEY)

BATCH_SIZE = 50

def get_feedback(
    source_code: str, problem_description: str, expected_output: str, judge_output: str
):
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

    # 📌 Gọi Gemini theo SDK mới
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    text = response.text.strip()

    # 🧹 Làm sạch JSON nếu LLM tự bao block markdown
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    # 🧾 Parse JSON
    try:
        return json.loads(text)
    except Exception:
        # Nếu JSON không đúng format, vẫn trả feedback dạng fallback
        return {
            "is_correct": None,
            "score": 0,
            "summary": text,
            "strengths": [],
            "weaknesses": ["Không phân tích được feedback"],
            "suggestions": [],
            "code_quality": {"readability": 0, "efficiency": 0, "best_practices": 0},
        }

async def process_courses():
    async with httpx.AsyncClient() as http:
        body = (await http.get(f"{MAIN_SERVICE_URL}/v1/courses")).json()
        courses = body.get("data", [])

    if not courses:
        print("⚠ Không có khóa học nào.")
        return

    total = len(courses)
    batches = math.ceil(total / BATCH_SIZE)
    success = 0

    for b in range(batches):
        chunk = courses[b * BATCH_SIZE : (b + 1) * BATCH_SIZE]

        contents = [
            f"{c['title']}\n{c['description']}\n{c.get('learningObjectives', '')}"
            for c in chunk
        ]

        try:
            result = client.models.embed_content(
                model="gemini-embedding-001",
                contents=contents  # ✔ API chuẩn SDK mới
            )

            vectors = [emb.values for emb in result.embeddings]  # list[list[float]]

            for idx, c in enumerate(chunk):
                upsert_course_vector(c["courseId"], vectors[idx])
                success += 1

            print(f"🔹 Batch {b+1}/{batches} completed ({len(chunk)} courses)")

        except Exception as e:
            print(f"❌ Lỗi batch {b+1}/{batches}: {e}")

    print(f"✨ Done — Embedded {success}/{total} courses bằng batch")
