import asyncio
import json
from typing import AsyncGenerator
from app.models.schemas import ChatStreamEvent, Session
from app.services.file_service import FileService

class ChatService:
    """聊天服务"""
    
    @staticmethod
    async def process_message(
        message: str, 
        session: Session
    ) -> AsyncGenerator[ChatStreamEvent, None]:
        """处理聊天消息并返回流式响应"""
        
        try:
            # 获取文件数据
            if not session.file_info:
                yield ChatStreamEvent(type="error", content="没有找到文件信息")
                return
            
            df = FileService.get_dataframe(session.file_info.filepath)
            
            # 模拟思考过程
            thinking_steps = [
                "正在分析您的问题...",
                f"已加载数据文件：{session.file_info.filename}",
                f"数据包含 {session.file_info.rows} 行，{session.file_info.columns} 列",
                "正在处理数据查询...",
                "生成分析结果..."
            ]
            
            for step in thinking_steps:
                yield ChatStreamEvent(type="thinking", content=step + "\n")
                await asyncio.sleep(0.5)  # 模拟处理时间
            
            # 模拟响应生成
            response_parts = [
                "根据您上传的数据文件分析，",
                f"该文件包含 **{session.file_info.rows}** 行数据和 **{session.file_info.columns}** 列字段。\n\n",
                "## 数据概览\n\n",
                f"- 文件名：`{session.file_info.filename}`\n",
                f"- 数据行数：{session.file_info.rows}\n",
                f"- 字段数量：{session.file_info.columns}\n",
                f"- 文件大小：{session.file_info.size}\n\n",
                "## 字段信息\n\n"
            ]
            
            # 添加列信息
            for i, col in enumerate(df.columns[:10]):  # 只显示前10列
                response_parts.append(f"{i+1}. **{col}** - {df[col].dtype}\n")
            
            if len(df.columns) > 10:
                response_parts.append(f"\n... 还有 {len(df.columns) - 10} 个字段\n")
            
            response_parts.extend([
                "\n## 数据示例\n\n",
                "以下是前几行数据的示例：\n\n",
                "| " + " | ".join(str(col) for col in df.columns[:5]) + " |\n",
                "| " + " | ".join(["---"] * min(5, len(df.columns))) + " |\n"
            ])
            
            # 添加示例数据行
            for i in range(min(3, len(df))):
                row_data = []
                for col in df.columns[:5]:
                    value = str(df.iloc[i][col])
                    if len(value) > 20:
                        value = value[:17] + "..."
                    row_data.append(value)
                response_parts.append("| " + " | ".join(row_data) + " |\n")
            
            response_parts.extend([
                "\n---\n\n",
                "💡 **提示**：您可以询问关于这些数据的任何问题，比如：\n",
                "- 数据统计和分析\n",
                "- 特定字段的信息\n", 
                "- 数据筛选和查询\n",
                "- 趋势分析等\n\n",
                "请告诉我您想了解什么！"
            ])
            
            # 逐步输出响应
            for part in response_parts:
                yield ChatStreamEvent(type="response", content=part)
                await asyncio.sleep(0.1)  # 模拟打字效果
            
            # 完成信号
            yield ChatStreamEvent(type="done")
            
        except Exception as e:
            yield ChatStreamEvent(type="error", content=f"处理消息时出错：{str(e)}")
    
    @staticmethod
    def _analyze_user_question(message: str, df) -> str:
        """分析用户问题并生成相应回答（简化版本）"""
        message_lower = message.lower()
        
        # 简单的关键词匹配
        if any(word in message_lower for word in ['多少行', '行数', 'rows']):
            return f"数据共有 {len(df)} 行。"
        
        if any(word in message_lower for word in ['多少列', '列数', '字段', 'columns']):
            return f"数据共有 {len(df.columns)} 列，字段名称为：{', '.join(df.columns.tolist())}"
        
        if any(word in message_lower for word in ['统计', '描述', 'describe', 'summary']):
            desc = df.describe()
            return f"数据统计信息：\n{desc.to_string()}"
        
        # 默认回答
        return "这是一个关于数据的问题。由于这是演示版本，我提供了基础的数据概览。在完整版本中，我将能够进行更深入的数据分析。"