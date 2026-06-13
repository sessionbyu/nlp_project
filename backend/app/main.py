import logging
import time

from app.api.v1.predict import router
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="NLP Service")


# =====================
# CORS
# =====================

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


# =====================
# 请求日志
# =====================


@app.middleware("http")
async def request_log(request: Request, call_next):
    start = time.time()

    response = await call_next(request)

    cost = time.time() - start

    logging.info(f"{request.method} {request.url} {cost:.2f}s")

    return response


# =====================
# 全局异常
# =====================


@app.exception_handler(Exception)
async def global_exception(request, exc):
    return {"error": str(exc)}


app.include_router(router, prefix="/api/v1")


@app.get("/")
def index():
    return {"status": "running"}
