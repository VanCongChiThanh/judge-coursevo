# Hướng dẫn Test API với Postman

## Server URL

```
http://127.0.0.1:5000
```

---

## 1. API Test Code (Không có Gemini)

### Endpoint

```
POST http://127.0.0.1:5000/api/judge/test
```

### Headers

```
Content-Type: application/json
Authorization: Bearer YOUR_JWT_TOKEN (optional)
```

### Body (raw JSON) - Python

```json
{
  "language_id": 71,
  "source_code": "print('Hello World')",
  "stdin": "",
  "expected_output": "Hello World"
}
```

### Body (raw JSON) - Python với input

```json
{
  "language_id": 71,
  "source_code": "name = input('Enter your name: ')\nprint(f'Hello, {name}!')",
  "stdin": "John",
  "expected_output": "Hello, John!"
}
```

### Body (raw JSON) - C++

```json
{
  "language_id": 54,
  "source_code": "#include <iostream>\nusing namespace std;\n\nint main() {\n    cout << \"Hello from C++\" << endl;\n    return 0;\n}",
  "stdin": "",
  "expected_output": "Hello from C++"
}
```

### Body (raw JSON) - Java

```json
{
  "language_id": 62,
  "source_code": "public class Main {\n    public static void main(String[] args) {\n        System.out.println(\"Hello from Java\");\n    }\n}",
  "stdin": "",
  "expected_output": "Hello from Java"
}
```

### Body (raw JSON) - JavaScript (Node.js)

```json
{
  "language_id": 63,
  "source_code": "console.log('Hello from JavaScript');",
  "stdin": "",
  "expected_output": "Hello from JavaScript"
}
```

---

## 2. API Submit Code (Có Judge0 + Gemini)

### Endpoint

```
POST http://127.0.0.1:5000/api/judge/submit
```

### Headers

```
Content-Type: application/json
Authorization: Bearer YOUR_JWT_TOKEN (optional)
```

### Body (raw JSON) - Bài toán tính tổng 2 số

```json
{
  "language_id": 71,
  "source_code": "a = int(input())\nb = int(input())\nprint(a + b)",
  "problem_description": "Viết chương trình nhập 2 số nguyên và in ra tổng của chúng",
  "expected_output": "15",
  "stdin": "5\n10"
}
```

### Body (raw JSON) - Bài toán kiểm tra số chẵn lẻ

```json
{
  "language_id": 71,
  "source_code": "n = int(input())\nif n % 2 == 0:\n    print('Even')\nelse:\n    print('Odd')",
  "problem_description": "Viết chương trình kiểm tra một số có phải là số chẵn hay không. In 'Even' nếu chẵn, 'Odd' nếu lẻ.",
  "expected_output": "Even",
  "stdin": "10"
}
```

### Body (raw JSON) - Bài toán tính giai thừa

```json
{
  "language_id": 71,
  "source_code": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)\n\nn = int(input())\nprint(factorial(n))",
  "problem_description": "Viết hàm tính giai thừa của một số nguyên n",
  "expected_output": "120",
  "stdin": "5"
}
```

### Body (raw JSON) - Code sai để test feedback

```json
{
  "language_id": 71,
  "source_code": "a = int(input())\nb = int(input())\nprint(a - b)",
  "problem_description": "Viết chương trình nhập 2 số nguyên và in ra tổng của chúng",
  "expected_output": "15",
  "stdin": "5\n10"
}
```

---

## 3. API Root (Health Check)

### Endpoint

```
GET http://127.0.0.1:5000/
```

### Response

```json
{
  "message": "FastAPI server is running!"
}
```

---

## Language IDs (Judge0)

Các `language_id` phổ biến:

| Language                     | ID  |
| ---------------------------- | --- |
| Python (3.8.1)               | 71  |
| JavaScript (Node.js 12.14.0) | 63  |
| Java (OpenJDK 13.0.1)        | 62  |
| C++ (GCC 9.2.0)              | 54  |
| C (GCC 9.2.0)                | 50  |
| C# (Mono 6.6.0.161)          | 51  |
| Go (1.13.5)                  | 60  |
| Ruby (2.7.0)                 | 72  |
| PHP (7.4.1)                  | 68  |
| TypeScript (3.7.4)           | 74  |

---

## Expected Response Format

### Response từ `/test` endpoint:

```json
{
  "user": null,
  "judge_result": {
    "stdout": "Hello World\n",
    "time": "0.023",
    "memory": 2048,
    "stderr": null,
    "token": "abc123...",
    "compile_output": null,
    "message": null,
    "status": {
      "id": 3,
      "description": "Accepted"
    }
  }
}
```

### Response từ `/submit` endpoint:

```json
{
  "user": null,
  "judge_result": {
    "stdout": "15\n",
    "time": "0.023",
    "memory": 2048,
    "stderr": null,
    "status": {
      "id": 3,
      "description": "Accepted"
    }
  },
  "feedback": {
    "score": 10,
    "comment": "Code chạy đúng và output khớp với expected output. Cách giải hợp lý.",
    "suggestions": [
      "Có thể thêm xử lý lỗi cho trường hợp input không hợp lệ",
      "Nên thêm comment để code dễ hiểu hơn"
    ]
  }
}
```

---

## Lưu ý

1. **Authorization header** là optional. Nếu không có, `user` sẽ là `null`.
2. **Tạo JWT token** (nếu cần test với authentication):
   ```python
   import jwt
   token = jwt.encode({"user_id": 123, "username": "test"}, "your-secret-key", algorithm="HS256")
   ```
3. **Judge0 Service** cần được cấu hình đúng trong `services/judge0_serivce.py`
4. **Gemini API** cần có API key hợp lệ trong `services/gemini_service.py`

---

## Test với cURL (Alternative)

### Test endpoint

```bash
curl -X POST "http://127.0.0.1:5000/api/judge/test" \
  -H "Content-Type: application/json" \
  -d '{"language_id": 71, "source_code": "print(\"Hello World\")", "stdin": "", "expected_output": "Hello World"}'
```

### Submit endpoint

```bash
curl -X POST "http://127.0.0.1:5000/api/judge/submit" \
  -H "Content-Type: application/json" \
  -d '{"language_id": 71, "source_code": "a = int(input())\nb = int(input())\nprint(a + b)", "problem_description": "Tính tổng 2 số", "expected_output": "15", "stdin": "5\n10"}'
```
