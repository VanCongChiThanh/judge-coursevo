from fastapi import FastAPI
from controllers.judge_controller import router as judge_router
from fastapi.middleware.cors import CORSMiddleware  
app = FastAPI(title="Judge Couservo API", version="1.0.0")

# Danh sách các địa chỉ frontend được phép truy cập
# Thêm địa chỉ của ứng dụng React của bạn vào đây
origins = [
    "http://localhost",
    "http://localhost:3000", # Cổng mặc định của Create React App
    "http://localhost:5173",
    "*", # Cổng mặc định của Vite
    # Thêm bất kỳ cổng nào khác mà frontend của bạn có thể đang chạy
    "https://coursevo.vercel.app",
    
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả các địa chỉ
    allow_methods=["*"],    # Cho phép tất cả các phương thức (GET, POST, etc.)
    allow_headers=["*"],    # Cho phép tất cả các header
)


app.include_router(judge_router, prefix="/api/judge", tags=["Judge"])

@app.get("/")
def root():
    return {"message": "FastAPI server is running!"}
