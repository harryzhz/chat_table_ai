import json
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models.schemas import ChatRequest, Message, ErrorResponse
from app.services.session_service import SessionService
from app.services.chat_service import ChatService
from app.core.logging_config import get_api_logger

logger = get_api_logger("chat")

router = APIRouter()


@router.post("/chat/stream")
async def stream_chat(request: ChatRequest):
    """
    流式聊天接口

    接收用户消息，返回 Server-Sent Events (SSE) 格式的流式响应
    """
    logger.info(f"收到聊天请求，会话ID: {request.session_id}")
    # 验证会话
    session = SessionService.get_session(request.session_id)
    if not session:
        logger.warning(f"会话不存在: {request.session_id}")
        raise HTTPException(status_code=404, detail="会话不存在")

    # 添加用户消息
    logger.debug(f"添加用户消息: {request.message[:100]}...")
    user_message = Message(
        id=str(uuid.uuid4()),
        type="user",
        content=request.message,
        timestamp=datetime.now().isoformat(),
    )
    SessionService.add_message(request.session_id, user_message)

    # 创建 AI 消息占位符
    ai_message = Message(
        id=str(uuid.uuid4()),
        type="assistant",
        content="",
        thinking="",
        timestamp=datetime.now().isoformat(),
    )
    SessionService.add_message(request.session_id, ai_message)

    async def generate_response():
        """生成流式响应"""
        try:
            logger.debug("开始生成流式响应")
            current_thinking = ""
            current_response = ""

            async for event in ChatService.process_message(request.message, session):
                # 更新消息内容
                if event.type == "thinking" and event.content:
                    current_thinking += event.content
                    SessionService.update_last_message(
                        request.session_id,
                        content=current_response,
                        thinking=current_thinking,
                    )
                elif event.type == "response" and event.content:
                    current_response += event.content
                    SessionService.update_last_message(
                        request.session_id,
                        content=current_response,
                        thinking=current_thinking,
                    )

                # 发送 SSE 事件
                yield f"data: {json.dumps(event.dict())}\n\n"

            # 发送完成信号
            logger.info("聊天响应生成完成")
            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"生成聊天响应时出错: {str(e)}")
            error_event = {"type": "error", "content": f"处理消息时出错：{str(e)}"}
            yield f"data: {json.dumps(error_event)}\n\n"

    return StreamingResponse(
        generate_response(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        },
    )


@router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """获取聊天历史"""
    logger.info(f"获取聊天历史，会话ID: {session_id}")
    session = SessionService.get_session(session_id)
    if not session:
        logger.warning(f"获取聊天历史失败，会话不存在: {session_id}")
        raise HTTPException(status_code=404, detail="会话不存在")

    return {
        "session_id": session.id,
        "messages": session.messages,
        "file_info": session.file_info,
    }


@router.delete("/chat/session/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    logger.info(f"删除会话，会话ID: {session_id}")
    success = SessionService.delete_session(session_id)
    if not success:
        logger.warning(f"删除会话失败，会话不存在: {session_id}")
        raise HTTPException(status_code=404, detail="会话不存在")

    return {"message": "会话已删除"}


@router.get("/chat/sessions")
async def list_sessions():
    """获取所有会话列表"""
    logger.info("获取所有会话列表")
    sessions = SessionService.list_sessions()
    return {
        "sessions": [
            {
                "id": session.id,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
                "status": session.status,
                "file_info": session.file_info,
                "message_count": len(session.messages),
            }
            for session in sessions.values()
        ]
    }
