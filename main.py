from fastapi import FastAPI
from controllers.judge_controller import router as judge_router

app = FastAPI(title="Judge Couservo API", version="1.0.0")

app.include_router(judge_router, prefix="/api/judge", tags=["Judge"])

@app.get("/")
def root():
    return {"message": "FastAPI server is running!"}
