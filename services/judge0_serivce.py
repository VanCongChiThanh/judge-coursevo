import requests
from utils.config import JUDGE0_URL, RAPID_API_KEY

HEADERS = {
    "x-rapidapi-host": "judge0-ce.p.rapidapi.com",
    "x-rapidapi-key": RAPID_API_KEY,
    "content-type": "application/json"
}

def run_code(language_id: int, source_code: str, stdin: str = "", expected_output: str = ""):
    payload = {
        "language_id": language_id,
        "source_code": source_code,
        "stdin": stdin,
        "expected_output": expected_output
    }
    url = f"{JUDGE0_URL}?base64_encoded=false&wait=true"
    res = requests.post(url, json=payload, headers=HEADERS)
    
    # Judge0 trả về 200 hoặc 201 đều OK
    if res.status_code not in [200, 201]:
        return {"error": f"Judge0 returned {res.status_code}", "detail": res.text}
    
    # Trả về JSON object thay vì string
    return res.json()

# batched submissions
def run_batch_code(submissions: list[dict]):
    payload = {
        "submissions": submissions
    }
    url = f"{JUDGE0_URL}/batch?base64_encoded=false&wait=true"
    res = requests.post(url, json=payload, headers=HEADERS)
    
    # Judge0 trả về 200 hoặc 201 đều OK
    if res.status_code not in [200, 201]:
        return {"error": f"Judge0 returned {res.status_code}", "detail": res.text}
    
    # lấy danh sách token từ kết quả
    data = res.json()
    tokens = [r["token"] for r in (data if isinstance(data, list) else data.get("judge_results", []))]
    
    # get batched submission results
    result_url = f"{JUDGE0_URL}/batch?tokens={','.join(tokens)}&base64_encoded=false"
    res = requests.get(result_url, headers=HEADERS)
    
    # Trả về JSON object thay vì string
    return res.json()
