"""Agent 配置文件"""
import os
from typing import Optional

class AgentConfig:
    """Agent 配置类"""
    
    # OpenAI API 配置
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    
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
        if not cls.OPENAI_API_KEY:
            print("警告：OPENAI_API_KEY 环境变量未设置，AI 功能将受限")
            return False
        return True