from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # 应用配置
    app_name: str = "ChatTable AI"
    debug: bool = True
    
    # 文件上传配置
    upload_dir: str = "uploads"
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_extensions: List[str] = [".xlsx", ".xls", ".csv"]
    
    # API 配置
    api_prefix: str = "/api"
    
    # CORS 配置
    allowed_origins: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ]
    
    class Config:
        env_file = ".env"

# 创建设置实例
settings = Settings()

# 确保上传目录存在
os.makedirs(settings.upload_dir, exist_ok=True)