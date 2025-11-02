"""
LLM 模块 - 提供可替换的 LLM 接口

这个模块包含了所有 LLM 相关的类和函数，支持多种 LLM 提供商。

主要组件：
- LLMProvider: 抽象基类，定义 LLM 提供商接口
- LLMFactory: 工厂类，用于创建 LLM 实例
- LLMMessage, LLMResponse: 消息和响应的数据类
- MessageRole: 消息角色枚举
- 各种具体的 LLM 提供商实现
"""

# 导入核心接口
from .llm_interface import (
    LLMProvider,
    LLMMessage,
    LLMResponse,
    MessageRole
)

# 导入具体实现
from .llm_providers import (
    OpenAIProvider,
    MockLLMProvider,
    ClaudeProvider,
    LocalLLMProvider
)

# 导入工厂类
from .llm_factory import LLMFactory

# 定义公开的 API
__all__ = [
    # 核心接口
    'LLMProvider',
    'LLMMessage',
    'LLMResponse',
    'MessageRole',
    
    # 具体实现
    'OpenAIProvider',
    'MockLLMProvider',
    'ClaudeProvider',
    'LocalLLMProvider',
    
    # 工厂类
    'LLMFactory'
]

# 版本信息
__version__ = '1.0.0'