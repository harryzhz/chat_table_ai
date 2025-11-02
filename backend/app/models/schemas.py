from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime


# 文件信息模型
class FileInfo(BaseModel):
    filename: str
    filepath: str
    rows: int
    columns: int
    size: str
    uploaded_at: str


# 消息模型
class Message(BaseModel):
    id: str
    type: str  # 'user' | 'assistant'
    content: str
    thinking: Optional[str] = None
    timestamp: str


# 会话模型
class Session(BaseModel):
    id: str
    created_at: str
    updated_at: str
    status: str  # 'active' | 'inactive'
    file_info: Optional[FileInfo] = None
    messages: List[Message] = []


# 文件上传响应
class UploadResponse(BaseModel):
    success: bool
    session_id: str
    file_info: FileInfo
    preview_data: List[Dict[str, Any]]


# 聊天请求
class ChatRequest(BaseModel):
    message: str
    session_id: str


# 聊天流式响应事件
class ChatStreamEvent(BaseModel):
    type: str  # 'thinking' | 'response' | 'error' | 'done'
    content: Optional[str] = None


# 错误响应
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
