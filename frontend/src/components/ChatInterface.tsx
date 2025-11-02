import React, { useEffect, useRef, useState } from 'react';
import { MessageSquare, AlertCircle } from 'lucide-react';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { useAppStore } from '../stores/appStore';
import { sendMessage } from '../utils/api';
import { generateId } from '../utils/helpers';
// 消息类型
interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  thinking?: string;
  timestamp: string;
}

// 聊天流式响应类型
interface ChatStreamEvent {
  type: 'thinking' | 'response' | 'error' | 'done';
  content?: string;
}

export const ChatInterface: React.FC = () => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [streamingMessage, setStreamingMessage] = useState<Message | null>(null);
  const [inputValue, setInputValue] = useState<string>('');
  
  const { 
    session, 
    isChatting, 
    setChatting, 
    addMessage, 
    updateLastMessage, 
    error, 
    setError 
  } = useAppStore();

  // 自动滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [session?.messages, streamingMessage]);

  const handleSendMessage = async (content: string) => {
    if (!session) {
      setError('请先上传文件');
      return;
    }

    setChatting(true);
    setError(null);
    setInputValue(''); // 清空输入框

    // 添加用户消息
    const userMessage: Message = {
      id: generateId(),
      type: 'user',
      content,
      timestamp: new Date().toISOString(),
    };
    addMessage(userMessage);

    // 创建 AI 消息占位符
    const aiMessage: Message = {
      id: generateId(),
      type: 'assistant',
      content: '',
      thinking: '',
      timestamp: new Date().toISOString(),
    };
    addMessage(aiMessage);
    setStreamingMessage(aiMessage);

    try {
      let currentThinking = '';
      let currentResponse = '';

      await sendMessage(content, session.id, (event: ChatStreamEvent) => {
        switch (event.type) {
          case 'thinking':
            if (event.content) {
              currentThinking += event.content;
              updateLastMessage(currentResponse, currentThinking);
              setStreamingMessage(prev => prev ? {
                ...prev,
                thinking: currentThinking,
                content: currentResponse
              } : null);
            }
            break;

          case 'response':
            if (event.content) {
              currentResponse += event.content;
              updateLastMessage(currentResponse, currentThinking);
              setStreamingMessage(prev => prev ? {
                ...prev,
                content: currentResponse,
                thinking: currentThinking
              } : null);
            }
            break;

          case 'error':
            setError(event.content || '发生未知错误');
            break;

          case 'done':
            setStreamingMessage(null);
            break;
        }
      });

    } catch (error) {
      setError(error instanceof Error ? error.message : '发送消息失败');
      setStreamingMessage(null);
    } finally {
      setChatting(false);
    }
  };

  // 处理示例问题点击
  const handleExampleClick = (example: string) => {
    setInputValue(example);
  };

  if (!session) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-50">
        <div className="text-center text-gray-500">
          <MessageSquare className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p className="text-lg font-medium mb-1">开始对话</p>
          <p className="text-sm">上传文件后即可开始与数据对话</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-gradient-to-b from-gray-50 to-white">
      {/* 错误提示 */}
      {error && (
        <div className="flex-shrink-0 mx-4 mt-4 p-3 bg-red-50 border-l-4 border-red-400 rounded-r-lg shadow-sm">
          <div className="flex items-center space-x-3">
            <AlertCircle className="w-4 h-4 text-red-500" />
            <span className="text-sm text-red-700 font-medium">{error}</span>
          </div>
        </div>
      )}

      {/* 消息列表 */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        {session.messages.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center text-gray-500 max-w-md">
              <div className="p-4 bg-blue-50 rounded-full w-20 h-20 mx-auto mb-6 flex items-center justify-center">
                <MessageSquare className="w-10 h-10 text-blue-400" />
              </div>
              <h3 className="text-xl font-semibold mb-3 text-gray-700">开始提问吧！</h3>
              <p className="text-sm leading-relaxed text-gray-600 mb-6">
                您可以询问关于数据的任何问题，比如：
              </p>
              <div className="space-y-3">
                {[
                  "这个表格有多少行数据？",
                  "帮我分析一下销售数据的趋势",
                  "计算各个类别的平均值"
                ].map((example, index) => (
                  <div 
                    key={index} 
                    className="p-3 bg-white rounded-lg shadow-sm border border-gray-100 cursor-pointer hover:bg-blue-50 hover:border-blue-200 transition-all duration-200"
                    onClick={() => handleExampleClick(example)}
                  >
                    <p className="text-sm text-gray-600">• {example}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {session.messages.map((message) => (
              <ChatMessage 
                key={message.id} 
                message={message}
                isStreaming={streamingMessage?.id === message.id}
              />
            ))}
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* 输入区域 */}
      <div className="flex-shrink-0 bg-white border-t border-gray-100 p-4">
        <ChatInput
          onSendMessage={handleSendMessage}
          disabled={isChatting}
          placeholder={
            isChatting 
              ? "AI 正在思考中..." 
              : "询问关于数据的问题..."
          }
          value={inputValue}
        />
      </div>
    </div>
  );
};