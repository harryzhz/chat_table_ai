import asyncio
import json
from typing import AsyncGenerator
from app.models.schemas import ChatStreamEvent, Session
from app.services.file_service import FileService
from app.agents.table_agent import table_agent
from app.core.logging_config import get_app_logger

logger = get_app_logger('chat_service')

class ChatService:
    """聊天服务"""
    
    @staticmethod
    async def process_message(
        message: str, 
        session: Session
    ) -> AsyncGenerator[ChatStreamEvent, None]:
        """处理聊天消息并返回流式响应"""
        logger.info(f"开始处理聊天消息，session_id: {getattr(session, 'id', None)}")
        
        try:
            # 使用 table_agent 处理消息
            logger.debug("调用 table_agent 处理消息")
            async for event in table_agent.process_message(message, session):
                logger.debug(f"收到事件: {event.type}")
                yield event
            
            logger.info("聊天消息处理完成")
                
        except Exception as e:
            logger.error(f"处理聊天消息时出错: {str(e)}")
            yield ChatStreamEvent(type="error", content=f"处理消息时出错：{str(e)}")