import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
  value?: string;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  disabled = false,
  placeholder = "输入您的问题...",
  value
}) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // 当外部传入 value 时，更新 message
  useEffect(() => {
    if (value !== undefined) {
      setMessage(value);
    }
  }, [value]);

  // 自动调整文本框高度
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
    }
  }, [message]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmedMessage = message.trim();
    if (trimmedMessage && !disabled) {
      onSendMessage(trimmedMessage);
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="border border-purple-300 bg-white p-2 shadow-lg rounded-lg">
      <form onSubmit={handleSubmit} className="flex items-end space-x-3">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            className={`
              w-full resize-none rounded-lg border-0 px-3 py-2 pr-10
              focus:outline-none focus:ring-0
              disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed
              min-h-[40px] max-h-[120px] bg-transparent
            `}
            rows={1}
          />
          
          {/* 字符计数 */}
          <div className="absolute bottom-1 right-1 text-xs text-gray-400">
            {message.length}/1000
          </div>
        </div>

        <button
          type="submit"
          disabled={disabled || !message.trim() || message.length > 1000}
          className={`
            flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center
            transition-all duration-200
            ${disabled || !message.trim() || message.length > 1000
              ? 'bg-gray-300 cursor-not-allowed'
              : 'bg-blue-500 hover:bg-blue-600 hover:shadow-md'
            }
          `}
        >
          {disabled ? (
            <Loader2 className="w-4 h-4 text-white animate-spin" />
          ) : (
            <Send className="w-4 h-4 text-white" />
          )}
        </button>
      </form>

      {/* 提示信息 */}
      <div className="mt-1 flex items-center justify-between text-xs text-gray-500">
        <span>按 Enter 发送，Shift + Enter 换行</span>
        {message.length > 900 && (
          <span className={message.length > 1000 ? 'text-red-500' : 'text-yellow-600'}>
            {message.length > 1000 ? '字符数超出限制' : '接近字符限制'}
          </span>
        )}
      </div>
    </div>
  );
};