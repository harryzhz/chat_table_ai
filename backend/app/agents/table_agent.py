"""表格分析 Agent"""
import asyncio
from typing import AsyncGenerator, Dict, Any
from langgraph.graph import StateGraph, END
from app.agents.nodes import (
    AgentState, 
    IntentClassificationNode,
    DataContextNode,
    TableAnalysisNode,
    CodeExecutionNode,
    ResponseGenerationNode,
    DirectResponseNode
)
from app.agents.config import AgentConfig
from app.models.schemas import ChatStreamEvent, Session
from app.core.logging_config import get_agent_logger

logger = get_agent_logger('table_agent')


class TableAnalysisAgent:
    """表格分析 Agent"""
    
    def __init__(self):
        """初始化 Agent"""
        logger.info("开始初始化 TableAnalysisAgent")
        
        # 验证配置
        try:
            AgentConfig.validate_config()
            logger.info("Agent 配置验证成功")
        except ValueError as e:
            logger.error(f"配置验证失败: {e}", exc_info=True)
            # 在实际部署时，这里应该抛出异常或使用默认配置
        
        # 创建节点实例
        logger.debug("创建节点实例")
        self.intent_node = IntentClassificationNode()
        self.data_context_node = DataContextNode()
        self.table_analysis_node = TableAnalysisNode()
        self.code_execution_node = CodeExecutionNode()
        self.response_generation_node = ResponseGenerationNode()
        self.direct_response_node = DirectResponseNode()
        
        # 构建工作流图
        logger.debug("构建工作流图")
        self.workflow = self._build_workflow()
        logger.info("TableAnalysisAgent 初始化完成")
    
    def _build_workflow(self) -> StateGraph:
        """构建 langgraph 工作流"""
        workflow = StateGraph(AgentState)
        
        # 添加节点
        workflow.add_node("intent_classification", self.intent_node)
        workflow.add_node("data_context", self.data_context_node)
        workflow.add_node("table_analysis", self.table_analysis_node)
        workflow.add_node("code_execution", self.code_execution_node)
        workflow.add_node("response_generation", self.response_generation_node)
        workflow.add_node("direct_response", self.direct_response_node)
        
        # 设置入口点
        workflow.set_entry_point("intent_classification")
        
        # 添加条件边
        workflow.add_conditional_edges(
            "intent_classification",
            self._should_analyze_table,
            {
                "analyze_table": "data_context",
                "direct_response": "direct_response"
            }
        )
        
        # 表格分析流程
        workflow.add_edge("data_context", "table_analysis")
        
        workflow.add_conditional_edges(
            "table_analysis",
            self._should_execute_code,
            {
                "execute_code": "code_execution",
                "generate_response": "response_generation"
            }
        )
        
        workflow.add_edge("code_execution", "response_generation")
        
        # 结束节点
        workflow.add_edge("response_generation", END)
        workflow.add_edge("direct_response", END)
        
        return workflow.compile()
    
    def _should_analyze_table(self, state: AgentState) -> str:
        """判断是否需要分析表格"""
        return "analyze_table" if state.get("is_table_related", False) else "direct_response"
    
    def _should_execute_code(self, state: AgentState) -> str:
        """判断是否需要执行代码"""
        return "execute_code" if state.get("needs_code_execution", False) else "generate_response"
    
    async def process_message(
        self, 
        message: str, 
        session: Session
    ) -> AsyncGenerator[ChatStreamEvent, None]:
        """处理消息并返回流式响应"""
        
        try:
            logger.info(f"开始处理用户消息: {message[:100]}...")
            # 初始化状态
            initial_state = AgentState({
                "user_message": message,
                "file_info": session.file_info,
                "session_id": session.id
            })
            
            yield ChatStreamEvent(type="thinking", content="正在分析您的问题...\n")
            await asyncio.sleep(0.3)
            
            # 使用 langgraph 工作流的流式执行
            final_state = {}
            
            # 使用 workflow.astream() 进行流式执行
            logger.info("开始工作流执行")
            async for chunk in self.workflow.astream(initial_state):
                # 获取当前节点名称
                node_name = list(chunk.keys())[0] if chunk else None
                
                if node_name:
                    logger.debug(f"执行节点: {node_name}")
                    # 发送节点执行状态
                    thinking_message = self._get_thinking_message(node_name)
                    if thinking_message:
                        yield ChatStreamEvent(
                            type="thinking",
                            content=thinking_message
                        )
                
                # 检查是否有错误
                current_state = chunk.get(node_name, {}) if node_name else {}
                # 确保 current_state 不为 None
                if current_state is None:
                    current_state = {}
                
                if current_state and current_state.get("error"):
                    logger.error(f"节点 {node_name} 执行出错: {current_state['error']}")
                    yield ChatStreamEvent(
                        type="error",
                        content=current_state["error"]
                    )
                    return
                
                # 保存最终状态，确保不为 None
                if current_state:
                    final_state = current_state
            
            # 检查最终状态
            if not final_state:
                logger.error("工作流执行失败，未获得最终状态")
                yield ChatStreamEvent(type="error", content="工作流执行失败")
                return
            
            # 确保 final_state 是字典类型
            if not isinstance(final_state, dict):
                logger.error(f"最终状态类型错误: {type(final_state)}")
                yield ChatStreamEvent(type="error", content="工作流状态错误")
                return
            
            if final_state.get("error"):
                logger.error(f"工作流执行出错: {final_state['error']}")
                yield ChatStreamEvent(type="error", content=final_state["error"])
                return
            
            # 流式输出最终响应
            final_response = final_state.get("final_response", "抱歉，无法生成回答。")
            logger.info("工作流执行完成，生成最终响应")
            
            # 将响应分段输出，模拟打字效果
            response_parts = self._split_response(final_response)
            
            for part in response_parts:
                yield ChatStreamEvent(type="response", content=part)
                await asyncio.sleep(0.1)
            
            # 完成信号
            yield ChatStreamEvent(type="done")
            
        except Exception as e:
            logger.error(f"处理消息时出错: {str(e)}", exc_info=True)
            yield ChatStreamEvent(type="error", content=f"处理消息时出错：{str(e)}")
    
    def _get_thinking_message(self, node_name: str) -> str:
        """根据节点名称生成思考消息"""
        thinking_messages = {
            "intent_classification": "正在判断问题类型...\n",
            "data_context": "检测到表格分析问题，正在加载数据...\n",
            "table_analysis": "正在分析数据并生成回答...\n",
            "code_execution": "正在执行数据分析代码...\n",
            "response_generation": "正在整理分析结果...\n",
            "direct_response": "正在生成回答...\n"
        }
        
        return thinking_messages.get(node_name, "")
    
    def _split_response(self, response: str, chunk_size: int = 50) -> list:
        """将响应分割成小块，用于流式输出"""
        if len(response) <= chunk_size:
            return [response]
        
        parts = []
        words = response.split()
        current_part = ""
        
        for word in words:
            if len(current_part + " " + word) <= chunk_size:
                current_part += (" " + word) if current_part else word
            else:
                if current_part:
                    parts.append(current_part)
                current_part = word
        
        if current_part:
            parts.append(current_part)
        
        return parts
    
    async def get_data_summary(self, session: Session) -> Dict[str, Any]:
        """获取数据摘要信息"""
        if not session.file_info:
            return {"error": "没有找到文件信息"}
        
        try:
            state = AgentState({
                "file_info": session.file_info
            })
            
            state = self.data_context_node(state)
            
            if state.get("error"):
                return {"error": state["error"]}
            
            return state.get("data_context", {})
            
        except Exception as e:
            return {"error": f"获取数据摘要失败：{str(e)}"}


# 创建全局 Agent 实例
table_agent = TableAnalysisAgent()