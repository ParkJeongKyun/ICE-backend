import os
import sys
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# 위치 지정
sys.path.append("./ice")

# router
from routers import api

# 로그 디렉토리 생성
if not os.path.exists("log"):
    os.mkdir('log')

# 로깅
logging.basicConfig(filename="log/log.log", level=logging.ERROR)

# FastAPI 앱
app = FastAPI()

# CORS 허용
origins = [
    #"http://localhost:3000",
    "http://ice-forensic.com",
    "http://iceforensic.netlify.app",
    "https://ice-forensic.com",
    "https://iceforensic.netlify.app"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# router 연결
app.include_router(api.router)

# uvicorn 실행
def main():
    uvicorn.run("ice.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()