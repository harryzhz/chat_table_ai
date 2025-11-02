import uuid
from typing import Dict, Optional
from datetime import datetime
from app.models.schemas import Session, Message, FileInfo

class SessionService:
    """会话管理服务"""
    
    # 内存存储（生产环境应使用数据库）
    _sessions: Dict[str, Session] = {}
    
    @classmethod
    def create_session(cls, file_info: FileInfo) -> Session:
        """创建新会话"""
        session_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        session = Session(
            id=session_id,
            created_at=now,
            updated_at=now,
            status="active",
            file_info=file_info,
            messages=[]
        )
        
        cls._sessions[session_id] = session
        return session
    
    @classmethod
    def get_session(cls, session_id: str) -> Optional[Session]:
        """获取会话"""
        return cls._sessions.get(session_id)
    
    @classmethod
    def add_message(cls, session_id: str, message: Message) -> bool:
        """添加消息到会话"""
        session = cls._sessions.get(session_id)
        if not session:
            return False
        
        session.messages.append(message)
        session.updated_at = datetime.now().isoformat()
        return True
    
    @classmethod
    def update_last_message(
        cls, 
        session_id: str, 
        content: Optional[str] = None,
        thinking: Optional[str] = None
    ) -> bool:
        """更新最后一条消息"""
        session = cls._sessions.get(session_id)
        if not session or not session.messages:
            return False
        
        last_message = session.messages[-1]
        if content is not None:
            last_message.content = content
        if thinking is not None:
            last_message.thinking = thinking
        
        session.updated_at = datetime.now().isoformat()
        return True
    
    @classmethod
    def delete_session(cls, session_id: str) -> bool:
        """删除会话"""
        if session_id in cls._sessions:
            del cls._sessions[session_id]
            return True
        return False
    
    @classmethod
    def get_all_sessions(cls) -> Dict[str, Session]:
        """获取所有会话"""
        return cls._sessions.copy()
    
    @classmethod
    def cleanup_inactive_sessions(cls, max_age_hours: int = 24) -> int:
        """清理非活跃会话"""
        now = datetime.now()
        to_delete = []
        
        for session_id, session in cls._sessions.items():
            session_time = datetime.fromisoformat(session.updated_at)
            age_hours = (now - session_time).total_seconds() / 3600
            
            if age_hours > max_age_hours:
                to_delete.append(session_id)
        
        for session_id in to_delete:
            del cls._sessions[session_id]
        
        return len(to_delete)