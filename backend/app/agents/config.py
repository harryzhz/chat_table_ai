"""Agent 配置文件"""
import os
from typing import Optional

class AgentConfig:
    """Agent 配置类"""
    
    # LLM 提供商配置
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")  # 支持: openai, claude, local, mock
    LLM_MODEL: Optional[str] = os.getenv("LLM_MODEL")  # 如果为空则使用提供商默认模型
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.0"))
    LLM_FALLBACK_TO_MOCK: bool = os.getenv("LLM_FALLBACK_TO_MOCK", "true").lower() == "true"
    
    # OpenAI API 配置
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")  # 保持向后兼容
    
    # Claude API 配置
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    
    # 本地 LLM 配置
    LOCAL_LLM_ENDPOINT: str = os.getenv("LOCAL_LLM_ENDPOINT", "http://localhost:8000")
    
    # 表格分析相关配置
    MAX_PREVIEW_ROWS: int = 21  # 包含表头的前21行
    MAX_CODE_EXECUTION_TIME: int = 30  # 代码执行超时时间（秒）
    
    # 意图判断相关配置
    TABLE_RELATED_KEYWORDS = [
        "数据", "表格", "统计", "分析", "查询", "筛选", "排序", "汇总",
        "平均", "最大", "最小", "总和", "计数", "图表", "可视化",
        "data", "table", "statistics", "analysis", "query", "filter", 
        "sort", "summary", "average", "max", "min", "sum", "count",
        "chart", "visualization", "行", "列", "字段", "row", "column", "field"
    ]
    
    @classmethod
    def validate_config(cls) -> bool:
        """验证配置是否完整"""
        provider = cls.LLM_PROVIDER.lower()
        
        if provider == "openai":
            if not cls.OPENAI_API_KEY:
                print("警告：OPENAI_API_KEY 环境变量未设置，AI 功能将受限")
                return False
        elif provider == "claude":
            if not cls.ANTHROPIC_API_KEY:
                print("警告：ANTHROPIC_API_KEY 环境变量未设置，AI 功能将受限")
                return False
        elif provider == "local":
            # 本地模型可能不需要 API Key，但可以检查端点
            print(f"使用本地 LLM 端点: {cls.LOCAL_LLM_ENDPOINT}")
        elif provider == "mock":
            print("使用模拟 LLM 提供商，AI 功能将受限")
            return False
        else:
            print(f"警告：不支持的 LLM 提供商 '{provider}'，将降级到模拟提供商")
            return False
        
        return True
    
    @classmethod
    def get_llm_config(cls) -> dict:
        """获取 LLM 配置字典"""
        return {
            "provider": cls.LLM_PROVIDER,
            "model": cls.LLM_MODEL,
            "temperature": cls.LLM_TEMPERATURE,
            "fallback_to_mock": cls.LLM_FALLBACK_TO_MOCK,
            "openai_api_key": cls.OPENAI_API_KEY,
            "anthropic_api_key": cls.ANTHROPIC_API_KEY,
            "local_llm_endpoint": cls.LOCAL_LLM_ENDPOINT,
        }