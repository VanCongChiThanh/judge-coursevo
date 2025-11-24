import os
from jose import jwt, JWTError
import base64
from utils.config import JWT_SECRET, JWT_ALGORITHM

def decode_jwt(token: str):
    try:
        secret_string = JWT_SECRET
        algorithm = JWT_ALGORITHM
        secret_bytes = base64.b64decode(secret_string)
        payload = jwt.decode(token, secret_bytes, algorithms=[algorithm])
        return payload

    except JWTError as e:
        print(f"Lỗi xác thực: {e}")
        return None
