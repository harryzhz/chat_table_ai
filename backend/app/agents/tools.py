"""Agent 工具模块"""
import ast
import sys
import io
import contextlib
import traceback
import pandas as pd
from typing import Dict, Any, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class CodeExecutionInput(BaseModel):
    """代码执行工具的输入模型"""
    code: str = Field(description="要执行的 Python 代码")
    context: Dict[str, Any] = Field(default_factory=dict, description="执行上下文，包含变量和数据")


class CodeExecutionTool(BaseTool):
    """代码执行工具"""
    name = "code_execution"
    description = """
    执行 Python 代码并返回结果。
    可以用于数据分析、统计计算、数据处理等操作。
    代码中可以使用 pandas、numpy 等常用数据分析库。
    执行上下文中会包含 'df' 变量，代表当前的数据表。
    """
    args_schema = CodeExecutionInput
    
    def _run(self, code: str, context: Dict[str, Any] = None) -> str:
        """执行代码并返回结果"""
        if context is None:
            context = {}
            
        # 创建安全的执行环境
        safe_globals = {
            '__builtins__': {
                'len': len, 'str': str, 'int': int, 'float': float, 'bool': bool,
                'list': list, 'dict': dict, 'tuple': tuple, 'set': set,
                'min': min, 'max': max, 'sum': sum, 'abs': abs, 'round': round,
                'sorted': sorted, 'reversed': reversed, 'enumerate': enumerate,
                'zip': zip, 'range': range, 'print': print, 'type': type,
            },
            'pd': pd,
            'pandas': pd,
        }
        
        # 添加上下文变量
        safe_globals.update(context)
        
        # 捕获输出
        output_buffer = io.StringIO()
        error_buffer = io.StringIO()
        
        try:
            # 检查代码安全性
            self._validate_code_safety(code)
            
            # 执行代码
            with contextlib.redirect_stdout(output_buffer), \
                 contextlib.redirect_stderr(error_buffer):
                
                # 编译并执行代码
                compiled_code = compile(code, '<string>', 'exec')
                exec(compiled_code, safe_globals)
            
            # 获取输出
            stdout_output = output_buffer.getvalue()
            stderr_output = error_buffer.getvalue()
            
            result = []
            if stdout_output:
                result.append(f"输出:\n{stdout_output}")
            if stderr_output:
                result.append(f"警告:\n{stderr_output}")
                
            return "\n".join(result) if result else "代码执行完成，无输出"
            
        except Exception as e:
            error_msg = f"代码执行错误: {str(e)}\n"
            error_msg += f"错误类型: {type(e).__name__}\n"
            error_msg += f"详细信息:\n{traceback.format_exc()}"
            return error_msg
    
    def _validate_code_safety(self, code: str) -> None:
        """验证代码安全性"""
        # 解析 AST
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise ValueError(f"代码语法错误: {e}")
        
        # 检查危险操作
        dangerous_nodes = []
        for node in ast.walk(tree):
            # 检查导入语句
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.ImportFrom):
                    module = node.module
                    if module and any(danger in module for danger in ['os', 'sys', 'subprocess', 'shutil']):
                        dangerous_nodes.append(f"危险的导入: {module}")
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if any(danger in alias.name for danger in ['os', 'sys', 'subprocess', 'shutil']):
                            dangerous_nodes.append(f"危险的导入: {alias.name}")
            
            # 检查函数调用
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['exec', 'eval', 'compile', '__import__']:
                        dangerous_nodes.append(f"危险的函数调用: {node.func.id}")
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['system', 'popen', 'remove', 'rmdir']:
                        dangerous_nodes.append(f"危险的方法调用: {node.func.attr}")
        
        if dangerous_nodes:
            raise ValueError(f"代码包含危险操作: {', '.join(dangerous_nodes)}")


class DataContextTool(BaseTool):
    """数据上下文工具"""
    name = "get_data_context"
    description = "获取当前数据表的上下文信息，包括列名、数据类型、样本数据等"
    
    def _run(self, df: pd.DataFrame) -> str:
        """获取数据上下文信息"""
        if df is None or df.empty:
            return "没有可用的数据"
        
        context_info = []
        
        # 基本信息
        context_info.append(f"数据形状: {df.shape[0]} 行 x {df.shape[1]} 列")
        
        # 列信息
        context_info.append("\n列信息:")
        for i, (col, dtype) in enumerate(zip(df.columns, df.dtypes), 1):
            context_info.append(f"{i}. {col} ({dtype})")
        
        # 数据预览
        context_info.append(f"\n数据预览 (前5行):")
        context_info.append(df.head().to_string())
        
        # 数值列的基本统计
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            context_info.append(f"\n数值列统计:")
            context_info.append(df[numeric_cols].describe().to_string())
        
        return "\n".join(context_info)


def create_agent_tools(df: Optional[pd.DataFrame] = None) -> list:
    """创建 Agent 工具列表"""
    tools = [CodeExecutionTool()]
    
    if df is not None:
        # 为工具提供数据上下文
        code_tool = CodeExecutionTool()
        code_tool.context = {'df': df}
        tools = [code_tool, DataContextTool()]
    
    return tools