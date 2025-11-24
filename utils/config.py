import os
from dotenv import load_dotenv

load_dotenv()

JUDGE0_URL = os.getenv("JUDGE0_URL", "https://judge0-ce.p.rapidapi.com/submissions")
RAPID_API_KEY = os.getenv("RAPID_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
JWT_SECRET = os.getenv("JWT_SECRET", "your-java-secret-key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS512")
DATABASE_URL = os.getenv("DATABASE_URL")
MAIN_SERVICE_URL = os.getenv("MAIN_SERVICE_URL", "http://localhost:8105/api")
