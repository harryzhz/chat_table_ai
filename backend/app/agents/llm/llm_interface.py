"""LLM 接口抽象层"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class MessageRole(Enum):
    """消息角色枚举"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class LLMMessage:
    """统一的消息格式"""

    role: MessageRole
    content: str

    def to_dict(self) -> Dict[str, str]:
        """转换为字典格式"""
        return {"role": self.role.value, "content": self.content}


@dataclass
class LLMResponse:
    """LLM 响应格式"""

    content: str
    model: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None

    @property
    def text(self) -> str:
        """获取响应文本内容"""
        return self.content


class LLMProvider(ABC):
    """LLM 提供商抽象基类"""

    def __init__(self, model: str, temperature: float = 0.0, **kwargs):
        self.model = model
        self.temperature = temperature
        self.kwargs = kwargs

    @abstractmethod
    def invoke(self, messages: List[LLMMessage]) -> LLMResponse:
        """
        调用 LLM 生成响应

        Args:
            messages: 消息列表

        Returns:
            LLM 响应

        Raises:
            Exception: 调用失败时抛出异常
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        检查 LLM 提供商是否可用

        Returns:
            是否可用
        """
        pass

    def get_model_name(self) -> str:
        """获取模型名称"""
        return self.model


class LLMError(Exception):
    """LLM 相关错误"""

    pass


class LLMUnavailableError(LLMError):
    """LLM 不可用错误"""

    pass


class LLMAPIError(LLMError):
    """LLM API 调用错误"""

    pass
