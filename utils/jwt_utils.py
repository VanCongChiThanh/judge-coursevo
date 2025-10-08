from jose import jwt, JWTError
import base64

JWT_SECRET = "928d4aef-6452-4ca1-8e4e-7dabad510423"
JWT_ALGORITHM = "HS512"

def decode_jwt(token: str):
    try:
        # Không encode thêm, truyền trực tiếp string
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError as e:
        print("JWT decode error:", e)
        return None