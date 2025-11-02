import json
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models.schemas import ChatRequest, Message, ErrorResponse
from app.services.session_service import SessionService
from app.services.chat_service import ChatService

router = APIRouter()

@router.post("/chat/stream")
async def stream_chat(request: ChatRequest):
    """
    流式聊天接口
    
    接收用户消息，返回 Server-Sent Events (SSE) 格式的流式响应
    """
    # 验证会话
    session = SessionService.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    # 添加用户消息
    user_message = Message(
        id=str(uuid.uuid4()),
        type="user",
        content=request.message,
        timestamp=datetime.now().isoformat()
    )
    SessionService.add_message(request.session_id, user_message)
    
    # 创建 AI 消息占位符
    ai_message = Message(
        id=str(uuid.uuid4()),
        type="assistant",
        content="",
        thinking="",
        timestamp=datetime.now().isoformat()
    )
    SessionService.add_message(request.session_id, ai_message)
    
    async def generate_response():
        """生成流式响应"""
        try:
            current_thinking = ""
            current_response = ""
            
            async for event in ChatService.process_message(request.message, session):
                # 更新消息内容
                if event.type == "thinking" and event.content:
                    current_thinking += event.content
                    SessionService.update_last_message(
                        request.session_id, 
                        content=current_response,
                        thinking=current_thinking
                    )
                elif event.type == "response" and event.content:
                    current_response += event.content
                    SessionService.update_last_message(
                        request.session_id,
                        content=current_response,
                        thinking=current_thinking
                    )
                
                # 发送 SSE 事件
                yield f"data: {json.dumps(event.dict())}\n\n"
            
            # 发送完成信号
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            error_event = {
                "type": "error",
                "content": f"处理消息时出错：{str(e)}"
            }
            yield f"data: {json.dumps(error_event)}\n\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )

@router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """获取聊天历史"""
    session = SessionService.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    return {
        "session_id": session.id,
        "messages": session.messages,
        "file_info": session.file_info
    }

@router.delete("/chat/session/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    success = SessionService.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    return {"message": "会话已删除"}

@router.get("/chat/sessions")
async def list_sessions():
    """获取所有会话列表"""
    sessions = SessionService.get_all_sessions()
    return {
        "sessions": [
            {
                "id": session.id,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
                "status": session.status,
                "file_info": session.file_info,
                "message_count": len(session.messages)
            }
            for session in sessions.values()
        ]
    }