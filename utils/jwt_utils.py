import os
from jose import jwt, JWTError
import base64


def decode_jwt(token: str):
    try:
        secret_string = os.getenv("JWT_SECRET")
        algorithm = os.getenv("JWT_ALGORITHM", "HS512")
        secret_bytes = base64.b64decode(secret_string)
        payload = jwt.decode(token, secret_bytes, algorithms=[algorithm])
        return payload

    except JWTError as e:
        print(f"Lỗi xác thực: {e}")
        return None
