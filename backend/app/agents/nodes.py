"""Agent 节点模块"""
import pandas as pd
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from app.agents.config import AgentConfig
from app.services.file_service import FileService
from app.core.logging_config import get_agent_logger

# 获取日志记录器
logger = get_agent_logger('nodes')


class AgentState(Dict[str, Any]):
    """Agent 状态类"""
    pass


class IntentClassificationNode:
    """意图分类节点"""
    
    def __init__(self):
        if AgentConfig.OPENAI_API_KEY:
            self.llm = ChatOpenAI(
                model=AgentConfig.OPENAI_MODEL,
                api_key=AgentConfig.OPENAI_API_KEY,
                temperature=0
            )
        else:
            self.llm = None
    
    def __call__(self, state: AgentState) -> AgentState:
        """判断用户意图"""
        logger.info("开始执行意图分类节点")
        user_message = state.get("user_message", "")
        logger.debug(f"用户消息: {user_message[:100]}...")  # 只记录前100个字符
        
        # 简单的关键词匹配作为快速判断
        is_table_related = any(
            keyword in user_message.lower() 
            for keyword in AgentConfig.TABLE_RELATED_KEYWORDS
        )
        logger.debug(f"关键词匹配结果: {is_table_related}")
        
        # 如果关键词匹配不明确，使用 LLM 进行判断
        if not is_table_related and self.llm:
            logger.info("使用 LLM 进行意图分类")
            try:
                system_prompt = """
                你是一个意图分类专家。请判断用户的问题是否与数据表格分析相关。
                
                表格相关的问题包括但不限于：
                - 数据统计和分析
                - 数据查询和筛选
                - 数据可视化
                - 字段信息查询
                - 数据计算和汇总
                - 趋势分析
                
                请只回答 "是" 或 "否"。
                """
                
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=f"用户问题：{user_message}")
                ]
                
                response = self.llm.invoke(messages)
                is_table_related = "是" in response.content
                logger.debug(f"LLM 分类结果: {response.content} -> {is_table_related}")
            except Exception as e:
                logger.error(f"LLM 意图分类失败: {str(e)}", exc_info=True)
                # 如果 LLM 调用失败，默认认为是表格相关问题
                is_table_related = True
                logger.warning("LLM 分类失败，默认设置为表格相关问题")
        
        state["is_table_related"] = is_table_related
        state["intent_classification_done"] = True
        
        logger.info(f"意图分类完成 - 是否表格相关: {is_table_related}")
        return state


class DataContextNode:
    """数据上下文节点"""
    
    def __call__(self, state: AgentState) -> AgentState:
        """构建数据上下文"""
        logger.info("开始执行数据上下文节点")
        file_info = state.get("file_info")
        if not file_info:
            logger.error("没有找到文件信息")
            state["error"] = "没有找到文件信息"
            return state
        
        logger.debug(f"处理文件: {file_info.filename}")
        
        try:
            # 读取数据文件
            logger.debug("开始读取数据文件")
            df = FileService.get_dataframe(file_info.filepath)
            logger.info(f"成功读取数据文件 - 行数: {len(df)}, 列数: {len(df.columns)}")
            
            # 获取前21行数据（包含表头）
            preview_df = df.head(AgentConfig.MAX_PREVIEW_ROWS - 1)  # -1 因为 head 不包含表头计数
            
            # 构建数据上下文
            context_info = {
                "filename": file_info.filename,
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "columns": df.columns.tolist(),
                "dtypes": df.dtypes.to_dict(),
                "preview_data": preview_df.to_dict('records'),
                "preview_string": preview_df.to_string()
            }
            
            state["data_context"] = context_info
            state["dataframe"] = df
            state["data_context_ready"] = True
            
            logger.info("数据上下文构建完成")
            
        except Exception as e:
            logger.error(f"读取数据文件失败: {str(e)}", exc_info=True)
            state["error"] = f"读取数据文件失败：{str(e)}"
        
        return state


class TableAnalysisNode:
    """表格分析节点"""
    
    def __init__(self):
        if AgentConfig.OPENAI_API_KEY:
            self.llm = ChatOpenAI(
                model=AgentConfig.OPENAI_MODEL,
                api_key=AgentConfig.OPENAI_API_KEY,
                temperature=0.1
            )
        else:
            self.llm = None
    
    def __call__(self, state: AgentState) -> AgentState:
        """分析表格数据并生成回答"""
        logger.info("开始执行表格分析节点")
        user_message = state.get("user_message", "")
        data_context = state.get("data_context", {})
        
        if not data_context:
            logger.error("数据上下文未准备就绪")
            state["error"] = "数据上下文未准备就绪"
            return state
        
        logger.debug(f"分析数据文件: {data_context.get('filename', 'unknown')}")
        
        # 构建系统提示
        system_prompt = f"""
        你是一个专业的数据分析师。用户上传了一个数据文件，你需要根据用户的问题进行分析。

        数据文件信息：
        - 文件名：{data_context.get('filename', 'unknown')}
        - 总行数：{data_context.get('total_rows', 0)}
        - 总列数：{data_context.get('total_columns', 0)}
        - 列名：{', '.join(data_context.get('columns', []))}
        
        数据预览（前20行）：
        {data_context.get('preview_string', '')}
        
        请根据用户的问题，分析数据并提供准确的回答。如果需要进行复杂的计算或数据处理，
        你可以生成 Python 代码来处理数据。数据已经加载到变量 'df' 中。
        
        如果你需要执行代码来回答问题，请在回答中包含代码块，格式如下：
        ```python
        # 你的代码
        ```
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        try:
            if self.llm:
                logger.info("使用 LLM 进行表格分析")
                logger.debug(f"发送消息到 LLM: {len(messages)} 条消息，数据行数: {data_context.get('total_rows', 0)}")
                response = self.llm.invoke(messages)
                logger.info(f"LLM 表格分析响应成功，响应长度: {len(response.content)} 字符")
                state["analysis_response"] = response.content
                state["analysis_done"] = True
                
                # 检查是否包含代码块
                if "```python" in response.content:
                    state["needs_code_execution"] = True
                    # 提取代码
                    code_blocks = self._extract_code_blocks(response.content)
                    state["code_to_execute"] = code_blocks
                    logger.info(f"检测到 {len(code_blocks)} 个代码块需要执行")
                else:
                    state["needs_code_execution"] = False
                    logger.debug("未检测到需要执行的代码块")
            else:
                # 没有 LLM 时的简单回答
                logger.warning("未配置 OpenAI API Key，使用简单分析模式")
                state["analysis_response"] = f"""
                根据您上传的数据文件分析：
                
                ## 数据概览
                - 文件名：{data_context.get('filename', 'unknown')}
                - 总行数：{data_context.get('total_rows', 0)}
                - 总列数：{data_context.get('total_columns', 0)}
                - 列名：{', '.join(data_context.get('columns', []))}
                
                ## 数据预览
                {data_context.get('preview_string', '')}
                
                注意：当前未配置 OpenAI API Key，无法进行深度分析。请配置 OPENAI_API_KEY 环境变量以获得完整的 AI 分析功能。
                """
                state["analysis_done"] = True
                state["needs_code_execution"] = False
                
        except Exception as e:
            logger.error(f"表格分析过程中出错: {str(e)}", exc_info=True)
            state["error"] = f"分析过程中出错：{str(e)}"
        
        logger.info("表格分析节点执行完成")
        
        return state
    
    def _extract_code_blocks(self, text: str) -> List[str]:
        """提取代码块"""
        code_blocks = []
        lines = text.split('\n')
        in_code_block = False
        current_code = []
        
        for line in lines:
            if line.strip().startswith('```python'):
                in_code_block = True
                current_code = []
            elif line.strip() == '```' and in_code_block:
                in_code_block = False
                if current_code:
                    code_blocks.append('\n'.join(current_code))
            elif in_code_block:
                current_code.append(line)
        
        return code_blocks


class CodeExecutionNode:
    """代码执行节点"""
    
    def __call__(self, state: AgentState) -> AgentState:
        """执行代码"""
        logger.info("开始执行代码执行节点")
        code_blocks = state.get("code_to_execute", [])
        df = state.get("dataframe")
        
        if not code_blocks:
            logger.debug("没有代码需要执行")
            state["code_execution_done"] = True
            return state
        
        logger.info(f"准备执行 {len(code_blocks)} 个代码块")
        
        execution_results = []
        
        for i, code in enumerate(code_blocks):
            logger.debug(f"执行代码块 {i+1}/{len(code_blocks)}")
            try:
                # 创建执行环境
                exec_globals = {
                    'df': df,
                    'pd': pd,
                    'pandas': pd,
                }
                
                # 捕获输出
                import io
                import contextlib
                
                output_buffer = io.StringIO()
                
                with contextlib.redirect_stdout(output_buffer):
                    exec(code, exec_globals)
                
                output = output_buffer.getvalue()
                execution_results.append({
                    "code": code,
                    "output": output,
                    "success": True
                })
                logger.info(f"代码块 {i+1} 执行成功")
                
            except Exception as e:
                logger.error(f"代码块 {i+1} 执行失败: {str(e)}", exc_info=True)
                logger.debug(f"失败的代码内容: {code[:200]}...")  # 只记录前200个字符
                execution_results.append({
                    "code": code,
                    "output": f"执行错误：{str(e)}",
                    "success": False
                })
        
        state["code_execution_results"] = execution_results
        state["code_execution_done"] = True
        
        successful_executions = sum(1 for result in execution_results if result["success"])
        logger.info(f"代码执行完成 - 成功: {successful_executions}/{len(code_blocks)}")
        
        return state


class ResponseGenerationNode:
    """响应生成节点"""
    
    def __init__(self):
        if AgentConfig.OPENAI_API_KEY:
            self.llm = ChatOpenAI(
                model=AgentConfig.OPENAI_MODEL,
                api_key=AgentConfig.OPENAI_API_KEY,
                temperature=0.1
            )
        else:
            self.llm = None
    
    def __call__(self, state: AgentState) -> AgentState:
        """生成最终响应"""
        logger.info("开始执行响应生成节点")
        user_message = state.get("user_message", "")
        analysis_response = state.get("analysis_response", "")
        code_execution_results = state.get("code_execution_results", [])
        
        if not state.get("is_table_related", False):
            # 非表格相关问题，直接回答
            logger.debug("处理非表格相关问题")
            if self.llm:
                logger.info("使用 LLM 生成非表格相关回答")
                system_prompt = "你是一个友好的助手，请直接回答用户的问题。"
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_message)
                ]
                
                try:
                    logger.debug(f"发送消息到 LLM: {len(messages)} 条消息")
                    response = self.llm.invoke(messages)
                    logger.info(f"LLM 响应成功，响应长度: {len(response.content)} 字符")
                    state["final_response"] = response.content
                except Exception as e:
                    logger.error(f"LLM 调用失败: {str(e)}", exc_info=True)
                    state["final_response"] = f"抱歉，生成回答时出现错误: {str(e)}"
            else:
                logger.warning("未配置 OpenAI API Key，无法回答非表格相关问题")
                state["final_response"] = "抱歉，当前未配置 OpenAI API Key，无法回答非表格相关的问题。请配置 OPENAI_API_KEY 环境变量。"
        else:
            # 表格相关问题，整合分析结果和代码执行结果
            logger.debug("整合表格分析结果和代码执行结果")
            final_response = analysis_response
            
            if code_execution_results:
                logger.info(f"整合 {len(code_execution_results)} 个代码执行结果")
                final_response += "\n\n## 代码执行结果\n\n"
                for i, result in enumerate(code_execution_results, 1):
                    final_response += f"### 代码块 {i}\n"
                    final_response += f"```python\n{result['code']}\n```\n\n"
                    if result['success']:
                        final_response += f"**执行结果：**\n```\n{result['output']}\n```\n\n"
                    else:
                        final_response += f"**执行错误：**\n```\n{result['output']}\n```\n\n"
            
            state["final_response"] = final_response
        
        state["response_generation_done"] = True
        logger.info("响应生成完成")
        return state


class DirectResponseNode:
    """直接响应节点（非表格相关问题）"""
    
    def __init__(self):
        if AgentConfig.OPENAI_API_KEY:
            self.llm = ChatOpenAI(
                model=AgentConfig.OPENAI_MODEL,
                api_key=AgentConfig.OPENAI_API_KEY,
                temperature=0.7
            )
        else:
            self.llm = None
    
    def __call__(self, state: AgentState) -> AgentState:
        """直接回答非表格相关问题"""
        logger.info("开始执行直接响应节点")
        user_message = state.get("user_message", "")
        
        system_prompt = """
        你是一个友好、专业的助手。用户的问题与数据表格分析无关，
        请直接回答用户的问题，保持友好和专业的语调。
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        try:
            if self.llm:
                logger.info("使用 LLM 生成直接回答")
                response = self.llm.invoke(messages)
                state["final_response"] = response.content
            else:
                logger.warning("未配置 OpenAI API Key，无法生成直接回答")
                state["final_response"] = "抱歉，当前未配置 OpenAI API Key，无法回答您的问题。请配置 OPENAI_API_KEY 环境变量以获得完整的 AI 功能。"
            state["direct_response_done"] = True
            logger.info("直接响应生成完成")
        except Exception as e:
            logger.error(f"生成直接回答时出错: {str(e)}")
            state["error"] = f"生成回答时出错：{str(e)}"
        
        return state