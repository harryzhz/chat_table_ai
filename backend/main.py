import os
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from app.api.routes import router
from app.core.config import settings
from app.core.logging_config import LoggingConfig, get_app_logger

# 初始化日志系统
LoggingConfig.setup_logging()
logger = get_app_logger('main')

app = FastAPI(
    title="ChatTable AI API",
    description="API for ChatTable AI - 与数据对话的智能应用",
    version="1.0.0"
)

logger.info("FastAPI 应用初始化完成")

# CORS 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("CORS 中间件配置完成")

# 注册路由
app.include_router(router, prefix="/api")
logger.info("API 路由注册完成")

@app.get("/")
async def root():
    logger.info("健康检查请求")
    return {"message": "ChatTable AI API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    logger.info("启动 Chat Table API 服务器")
    logger.info(f"服务器地址: http://0.0.0.0:8000")
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )