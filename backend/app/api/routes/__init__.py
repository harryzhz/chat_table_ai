# API 路由模块
from fastapi import APIRouter
from app.core.logging_config import get_api_logger
from . import upload, chat

logger = get_api_logger("routes")

# 创建主路由
router = APIRouter()

# 包含子路由
router.include_router(upload.router, tags=["upload"])
router.include_router(chat.router, tags=["chat"])

logger.info("API 路由模块初始化完成")
