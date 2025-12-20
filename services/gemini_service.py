
from google import genai

import httpx
from services.db_service import upsert_course_vector
from utils.config import GEMINI_API_KEY, MAIN_SERVICE_URL
import json
import math
from services.db_service import get_all_course_vectors
import numpy as np


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
            f"""
            {c['title']}
            {c['description']}
            Level: {c['level']}
            Category: {c['category']}
            """
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

async def generate_career_plan(req):
    # 1️⃣ tạo context mô tả toàn bộ yêu cầu career
    context = f"""
    Role: {req.role}
    Goal: {req.goal}
    Answers: {req.answers}
    """

    # 2️⃣ yêu cầu Gemini chia lộ trình thành các section
    prompt = f"""
    Bạn là cố vấn nghề nghiệp trong lĩnh vực lập trình.
    Hãy tạo một lộ trình học (career roadmap) dựa trên các thông tin sau:

    {context}

    Yêu cầu bắt buộc:
    - TRẢ VỀ JSON THUẦN, không thêm giải thích, không markdown.
    - Không viết bất kỳ nội dung nào ngoài JSON.
    - Từ ngữ ngắn gọn, chính xác, chuyên nghiệp.

    Cấu trúc JSON bắt buộc:
    {{
    "sections": [
        {{
        "section_title": "Tên section",
        "description": "Mô tả nội dung section và kỹ năng sẽ đạt được",
        "keywords": ["keyword1", "keyword2", "keyword3"]
        }}
    ]
    }}

    Quy tắc sinh dữ liệu:
    - Tạo từ 3 đến 6 section.
    - Một section phải tập trung vào một chủ đề kỹ năng rõ ràng (ví dụ: Java cơ bản, Spring Boot backend, Hệ thống phân tán, DevOps,...)
    - Mỗi section phải có tối thiểu 2 và tối đa 4 keywords.
    - KHÔNG thêm text ngoài JSON.
    """


    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    text = response.text.strip()
    if text.startswith("```json"): text = text[7:]
    if text.startswith("```"): text = text[3:]
    if text.endswith("```"): text = text[:-3]
    sections = json.loads(text)["sections"]

    # 3️⃣ Chuyển keywords thành courseIds — dùng embedding search
    enriched_sections = []
    for section in sections:
        course_ids = await search_similar_courses(section["keywords"])
        enriched_sections.append({
            "section_title": section["section_title"],
            "description": section["description"],
            "course_ids": course_ids
        })

    return {
        "role": req.role,
        "goal": req.goal,
        "sections": enriched_sections
    }
async def search_similar_courses(keywords: list[str], top_k: int = 3):
    # Tạo embedding query bằng Gemini
    query = " ".join(keywords)
    emb = client.models.embed_content(model="gemini-embedding-001", contents=[query]).embeddings[0].values

    courses = get_all_course_vectors()  # [{ course_id, embedding }]
    if not courses:
        return []
    
    scores = []

    for c in courses:
        score = np.dot(emb, c["embedding"]) / (
            np.linalg.norm(emb) * np.linalg.norm(c["embedding"])
        )
        scores.append((c["course_id"], score))

    scores.sort(key=lambda x: x[1], reverse=True)
    return [cid for cid, _ in scores[:top_k]]