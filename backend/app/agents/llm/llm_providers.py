"""LLM 提供商具体实现"""

import os
from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from .llm_interface import (
    LLMProvider,
    LLMMessage,
    LLMResponse,
    MessageRole,
    LLMError,
    LLMUnavailableError,
    LLMAPIError,
)
from app.core.logging_config import get_agent_logger

logger = get_agent_logger("llm_providers")


class OpenAIProvider(LLMProvider):
    """OpenAI LLM 提供商实现"""

    def __init__(
        self,
        model: str = "gpt-4",
        temperature: float = 0.0,
        api_key: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(model, temperature, **kwargs)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self._client = None

    def _get_client(self) -> ChatOpenAI:
        """获取 OpenAI 客户端"""
        if self._client is None:
            if not self.api_key:
                raise LLMUnavailableError("OpenAI API Key 未配置")

            try:
                self._client = ChatOpenAI(
                    model=self.model,
                    api_key=self.api_key,
                    temperature=self.temperature,
                    **self.kwargs,
                )
            except Exception as e:
                logger.error(f"创建 OpenAI 客户端失败: {str(e)}")
                raise LLMUnavailableError(f"创建 OpenAI 客户端失败: {str(e)}")

        return self._client

    def invoke(self, messages: List[LLMMessage]) -> LLMResponse:
        """调用 OpenAI API"""
        try:
            client = self._get_client()

            # 转换消息格式
            langchain_messages = []
            for msg in messages:
                if msg.role == MessageRole.SYSTEM:
                    langchain_messages.append(SystemMessage(content=msg.content))
                elif msg.role == MessageRole.USER:
                    langchain_messages.append(HumanMessage(content=msg.content))
                elif msg.role == MessageRole.ASSISTANT:
                    langchain_messages.append(AIMessage(content=msg.content))

            logger.debug(
                f"调用 OpenAI API - 模型: {self.model}, 消息数: {len(langchain_messages)}"
            )

            # 调用 API
            response = client.invoke(langchain_messages)

            logger.debug(
                f"OpenAI API 响应成功 - 响应长度: {len(response.content)} 字符"
            )

            return LLMResponse(
                content=response.content,
                model=self.model,
                usage=getattr(response, "usage_metadata", None),
            )

        except Exception as e:
            logger.error(f"OpenAI API 调用失败: {str(e)}")
            raise LLMAPIError(f"OpenAI API 调用失败: {str(e)}")

    def is_available(self) -> bool:
        """检查 OpenAI 是否可用"""
        try:
            return bool(self.api_key)
        except Exception:
            return False


class MockLLMProvider(LLMProvider):
    """模拟 LLM 提供商（用于测试或无 API Key 时的降级）"""

    def __init__(self, model: str = "mock", temperature: float = 0.0, **kwargs):
        super().__init__(model, temperature, **kwargs)

    def invoke(self, messages: List[LLMMessage]) -> LLMResponse:
        """返回模拟响应"""
        logger.warning("使用模拟 LLM 提供商，返回默认响应")

        # 根据最后一条用户消息生成简单响应
        user_message = ""
        for msg in reversed(messages):
            if msg.role == MessageRole.USER:
                user_message = msg.content
                break

        mock_response = f"""
        抱歉，当前未配置有效的 LLM API Key，无法提供 AI 分析功能。
        
        您的问题：{user_message[:100]}...
        
        请配置以下环境变量之一以启用 AI 功能：
        - OPENAI_API_KEY: 用于 OpenAI GPT 模型
        
        配置完成后重启应用即可使用完整的 AI 分析功能。
        """

        return LLMResponse(content=mock_response.strip(), model=self.model)

    def is_available(self) -> bool:
        """模拟提供商始终可用"""
        return True


# 未来可以添加更多提供商实现
class ClaudeProvider(LLMProvider):
    """Claude LLM 提供商实现（预留接口）"""

    def __init__(
        self,
        model: str = "claude-3-sonnet",
        temperature: float = 0.0,
        api_key: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(model, temperature, **kwargs)
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

    def invoke(self, messages: List[LLMMessage]) -> LLMResponse:
        """调用 Claude API（待实现）"""
        raise NotImplementedError(
            "Claude 提供商暂未实现，请使用 OpenAI 或配置相应的依赖"
        )

    def is_available(self) -> bool:
        """检查 Claude 是否可用"""
        return bool(self.api_key)


class LocalLLMProvider(LLMProvider):
    """本地 LLM 提供商实现（预留接口）"""

    def __init__(
        self,
        model: str = "local",
        temperature: float = 0.0,
        endpoint: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(model, temperature, **kwargs)
        self.endpoint = endpoint or os.getenv(
            "LOCAL_LLM_ENDPOINT", "http://localhost:8000"
        )

    def invoke(self, messages: List[LLMMessage]) -> LLMResponse:
        """调用本地 LLM API（待实现）"""
        raise NotImplementedError("本地 LLM 提供商暂未实现")

    def is_available(self) -> bool:
        """检查本地 LLM 是否可用"""
        # 这里可以添加健康检查逻辑
        return False
