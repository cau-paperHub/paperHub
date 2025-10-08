from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import papers
app = FastAPI()

# CORS 설정
origins = ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(papers.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Hello from PaperHub Backend!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}