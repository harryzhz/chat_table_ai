# LLM 接口使用指南

## 概述

本项目已重构为支持多种 LLM 提供商的可替换接口设计，支持 OpenAI、Claude、本地模型等多种选择。

## 配置方式

### 环境变量配置

```bash
# LLM 提供商选择（默认: openai）
export LLM_PROVIDER=openai  # 支持: openai, claude, local, mock

# LLM 模型（可选，不设置则使用提供商默认模型）
export LLM_MODEL=gpt-4

# LLM 温度参数（默认: 0.0）
export LLM_TEMPERATURE=0.1

# 是否允许降级到模拟提供商（默认: true）
export LLM_FALLBACK_TO_MOCK=true

# OpenAI 配置
export OPENAI_API_KEY=your_openai_api_key

# Claude 配置
export ANTHROPIC_API_KEY=your_anthropic_api_key

# 本地 LLM 配置
export LOCAL_LLM_ENDPOINT=http://localhost:8000
```

### 支持的提供商

1. **OpenAI** (`openai`)
   - 需要配置 `OPENAI_API_KEY`
   - 默认模型: `gpt-4`
   - 支持所有 OpenAI 模型

2. **Claude** (`claude`) - 预留接口
   - 需要配置 `ANTHROPIC_API_KEY`
   - 默认模型: `claude-3-sonnet`
   - 当前版本暂未实现，将在后续版本中支持

3. **本地模型** (`local`) - 预留接口
   - 需要配置 `LOCAL_LLM_ENDPOINT`
   - 支持兼容 OpenAI API 格式的本地模型服务
   - 当前版本暂未实现

4. **模拟提供商** (`mock`)
   - 无需配置，始终可用
   - 用于测试或无 API Key 时的降级方案

## 使用示例

### 基本使用

```python
from app.agents.llm_factory import LLMFactory
from app.agents.llm_interface import LLMMessage, MessageRole

# 创建 LLM 实例
llm = LLMFactory.create_llm(
    provider="openai",
    model="gpt-4",
    temperature=0.1
)

# 构建消息
messages = [
    LLMMessage(role=MessageRole.SYSTEM, content="你是一个数据分析助手"),
    LLMMessage(role=MessageRole.USER, content="请分析这个数据")
]

# 调用 LLM
response = llm.invoke(messages)
print(response.content)
```

### 从配置创建

```python
from app.agents.config import AgentConfig
from app.agents.llm_factory import LLMFactory

# 从配置文件创建 LLM 实例
llm = LLMFactory.create_from_config(AgentConfig)
```

### 检查可用性

```python
from app.agents.llm_factory import LLMFactory

# 获取所有提供商的可用性
providers = LLMFactory.get_available_providers()
print(providers)  # {'openai': True, 'claude': False, 'local': False, 'mock': True}
```

## 向后兼容性

- 保持了原有的 `OPENAI_API_KEY` 和 `OPENAI_MODEL` 环境变量支持
- 现有代码无需修改即可继续工作
- 新的配置选项是可选的，有合理的默认值

## 错误处理

- 当主要提供商不可用时，系统会自动降级到模拟提供商（如果启用）
- 所有错误都有详细的日志记录
- 提供了清晰的错误信息和解决建议

## 扩展新提供商

要添加新的 LLM 提供商，需要：

1. 在 `app/agents/llm_providers.py` 中实现 `LLMProvider` 接口
2. 在 `LLMFactory.PROVIDERS` 中注册新提供商
3. 在配置文件中添加相应的配置选项

示例：

```python
class NewProvider(LLMProvider):
    def __init__(self, model: str = "default", temperature: float = 0.0, **kwargs):
        super().__init__(model, temperature, **kwargs)
        # 初始化代码
    
    def invoke(self, messages: List[LLMMessage]) -> LLMResponse:
        # 实现调用逻辑
        pass
    
    def is_available(self) -> bool:
        # 检查可用性
        return True
```

## 注意事项

1. 确保在生产环境中正确配置 API Key
2. 根据使用场景选择合适的模型和温度参数
3. 监控 API 调用的成本和频率
4. 定期检查日志以确保系统正常运行