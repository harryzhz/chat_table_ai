import React, { useState } from 'react';
import { User, Bot, ChevronDown, ChevronUp, Brain } from 'lucide-react';
// 消息类型
interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  thinking?: string;
  timestamp: string;
}
import { MarkdownRenderer } from './MarkdownRenderer';
import { formatTime } from '../utils/helpers';

interface ChatMessageProps {
  message: Message;
  isStreaming?: boolean;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ 
  message, 
  isStreaming = false 
}) => {
  const [isThinkingExpanded, setIsThinkingExpanded] = useState(true);
  const isUser = message.type === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-6`}>
      <div className={`flex max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        {/* 头像 */}
        <div className={`flex-shrink-0 ${isUser ? 'ml-3' : 'mr-3'}`}>
          <div className={`
            w-8 h-8 rounded-full flex items-center justify-center
            ${isUser ? 'bg-blue-500' : 'bg-gray-500'}
          `}>
            {isUser ? (
              <User className="w-4 h-4 text-white" />
            ) : (
              <Bot className="w-4 h-4 text-white" />
            )}
          </div>
        </div>

        {/* 消息内容 */}
        <div className="flex-1 min-w-0">
          {/* 用户消息 */}
          {isUser && (
            <div className="bg-blue-500 text-white rounded-lg px-4 py-2">
              <p className="whitespace-pre-wrap break-words">{message.content}</p>
            </div>
          )}

          {/* AI 消息 */}
          {!isUser && (
            <div className="space-y-3">
              {/* 思考过程 */}
              {message.thinking && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg overflow-hidden">
                  <button
                    onClick={() => setIsThinkingExpanded(!isThinkingExpanded)}
                    className="w-full px-4 py-2 flex items-center justify-between text-left hover:bg-yellow-100 transition-colors"
                  >
                    <div className="flex items-center space-x-2">
                      <Brain className="w-4 h-4 text-yellow-600" />
                      <span className="text-sm font-medium text-yellow-800">
                        思考过程
                      </span>
                    </div>
                    {isThinkingExpanded ? (
                      <ChevronUp className="w-4 h-4 text-yellow-600" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-yellow-600" />
                    )}
                  </button>
                  
                  {isThinkingExpanded && (
                    <div className="px-4 pb-4 border-t border-yellow-200">
                      <MarkdownRenderer 
                        content={message.thinking} 
                        className="text-sm text-yellow-800"
                      />
                    </div>
                  )}
                </div>
              )}

              {/* 回答内容 */}
              <div className="bg-white border border-gray-200 rounded-lg px-4 py-3">
                {message.content ? (
                  <MarkdownRenderer content={message.content} />
                ) : isStreaming ? (
                  <div className="flex items-center space-x-2 text-gray-500">
                    <div className="animate-pulse flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                    </div>
                    <span className="text-sm">AI 正在思考...</span>
                  </div>
                ) : (
                  <div className="text-gray-500 text-sm">暂无回答</div>
                )}
              </div>
            </div>
          )}

          {/* 时间戳 */}
          <div className={`mt-1 text-xs text-gray-500 ${isUser ? 'text-right' : 'text-left'}`}>
            {formatTime(message.timestamp)}
          </div>
        </div>
      </div>
    </div>
  );
};