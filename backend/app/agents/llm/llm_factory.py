"""LLM 工厂类"""

from typing import Optional, Dict, Any
from .llm_interface import LLMProvider, LLMUnavailableError
from .llm_providers import (
    OpenAIProvider,
    MockLLMProvider,
    ClaudeProvider,
    LocalLLMProvider,
)
from app.core.logging_config import get_agent_logger

logger = get_agent_logger("llm_factory")


class LLMFactory:
    """LLM 工厂类，根据配置创建相应的 LLM 提供商实例"""

    # 支持的提供商映射
    PROVIDERS = {
        "openai": OpenAIProvider,
        "claude": ClaudeProvider,
        "local": LocalLLMProvider,
        "mock": MockLLMProvider,
    }

    @classmethod
    def create_llm(
        cls,
        provider: str = "openai",
        model: Optional[str] = None,
        temperature: float = 0.0,
        fallback_to_mock: bool = True,
        **kwargs,
    ) -> LLMProvider:
        """
        创建 LLM 提供商实例

        Args:
            provider: 提供商名称 (openai, claude, local, mock)
            model: 模型名称，如果为 None 则使用默认模型
            temperature: 温度参数
            fallback_to_mock: 当主要提供商不可用时是否降级到模拟提供商
            **kwargs: 其他参数

        Returns:
            LLM 提供商实例

        Raises:
            LLMUnavailableError: 当提供商不可用且不允许降级时
        """
        provider = provider.lower()

        if provider not in cls.PROVIDERS:
            logger.error(f"不支持的 LLM 提供商: {provider}")
            if fallback_to_mock:
                logger.warning("降级到模拟提供商")
                return cls._create_mock_provider(temperature, **kwargs)
            else:
                raise LLMUnavailableError(f"不支持的 LLM 提供商: {provider}")

        try:
            # 获取提供商类
            provider_class = cls.PROVIDERS[provider]

            # 设置默认模型
            if model is None:
                model = cls._get_default_model(provider)

            logger.info(f"创建 LLM 提供商: {provider}, 模型: {model}")

            # 创建实例
            llm_instance = provider_class(
                model=model, temperature=temperature, **kwargs
            )

            # 检查是否可用
            if not llm_instance.is_available():
                logger.warning(f"{provider} 提供商不可用")
                if fallback_to_mock:
                    logger.warning("降级到模拟提供商")
                    return cls._create_mock_provider(temperature, **kwargs)
                else:
                    raise LLMUnavailableError(f"{provider} 提供商不可用")

            logger.info(f"成功创建 {provider} 提供商实例")
            return llm_instance

        except Exception as e:
            logger.error(f"创建 {provider} 提供商失败: {str(e)}")
            if fallback_to_mock:
                logger.warning("降级到模拟提供商")
                return cls._create_mock_provider(temperature, **kwargs)
            else:
                raise LLMUnavailableError(f"创建 {provider} 提供商失败: {str(e)}")

    @classmethod
    def _get_default_model(cls, provider: str) -> str:
        """获取提供商的默认模型"""
        defaults = {
            "openai": "gpt-4",
            "claude": "claude-3-sonnet",
            "local": "local",
            "mock": "mock",
        }
        return defaults.get(provider, "gpt-4")

    @classmethod
    def _create_mock_provider(
        cls, temperature: float = 0.0, **kwargs
    ) -> MockLLMProvider:
        """创建模拟提供商实例"""
        return MockLLMProvider(temperature=temperature, **kwargs)

    @classmethod
    def get_available_providers(cls) -> Dict[str, bool]:
        """
        获取所有提供商的可用性状态

        Returns:
            提供商名称到可用性的映射
        """
        availability = {}

        for provider_name, provider_class in cls.PROVIDERS.items():
            try:
                # 创建临时实例检查可用性
                if provider_name == "mock":
                    # 模拟提供商始终可用
                    availability[provider_name] = True
                else:
                    temp_instance = provider_class()
                    availability[provider_name] = temp_instance.is_available()
            except Exception:
                availability[provider_name] = False

        return availability

    @classmethod
    def create_from_config(cls, config) -> LLMProvider:
        """
        从配置对象创建 LLM 实例

        Args:
            config: 配置对象，需要包含 LLM 相关配置

        Returns:
            LLM 提供商实例
        """
        provider = getattr(config, "LLM_PROVIDER", "openai")
        model = getattr(config, "LLM_MODEL", None)
        temperature = getattr(config, "LLM_TEMPERATURE", 0.0)
        fallback_to_mock = getattr(config, "LLM_FALLBACK_TO_MOCK", True)

        # 获取提供商特定的配置
        provider_config = {}
        if provider == "openai":
            api_key = getattr(config, "OPENAI_API_KEY", None)
            if api_key:
                provider_config["api_key"] = api_key
        elif provider == "claude":
            api_key = getattr(config, "ANTHROPIC_API_KEY", None)
            if api_key:
                provider_config["api_key"] = api_key
        elif provider == "local":
            endpoint = getattr(config, "LOCAL_LLM_ENDPOINT", None)
            if endpoint:
                provider_config["endpoint"] = endpoint

        return cls.create_llm(
            provider=provider,
            model=model,
            temperature=temperature,
            fallback_to_mock=fallback_to_mock,
            **provider_config,
        )
