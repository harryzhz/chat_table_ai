import React from 'react';
import { Sparkles } from 'lucide-react';
import { FileUpload, FilePreview, ChatInterface, ResizablePanels } from '../components';
import { useAppStore } from '../stores/appStore';

export const HomePage: React.FC = () => {
  const { session } = useAppStore();

  // 如果没有会话，显示文件上传界面
  if (!session) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="container mx-auto px-4 py-8">
          {/* 头部 */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-4 flex items-center justify-center gap-3">
              <Sparkles className="w-10 h-10 text-blue-500 animate-pulse" />
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent font-extrabold tracking-tight">
                ChatTable AI
              </span>
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              上传您的 Excel 或 CSV 文件，与数据进行智能对话
            </p>
          </div>

          {/* 文件上传区域 */}
          <div className="max-w-2xl mx-auto">
            <FileUpload />
          </div>

          {/* 功能介绍 */}
          <div className="mt-16 max-w-4xl mx-auto">
            <h2 className="text-2xl font-semibold text-gray-900 text-center mb-8">
              功能特色
            </h2>
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  简单上传
                </h3>
                <p className="text-gray-600">
                  支持拖拽上传 Excel 和 CSV 文件，自动解析数据结构
                </p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  智能对话
                </h3>
                <p className="text-gray-600">
                  使用自然语言询问数据问题，获得准确的分析结果
                </p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  数据洞察
                </h3>
                <p className="text-gray-600">
                  深度分析数据趋势，生成可视化图表和统计报告
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // 如果有会话，显示分栏布局
  return (
    <div className="h-screen flex bg-gray-50 p-4">
      {/* 主容器 - 添加圆角和阴影 */}
      <div className="flex-1 flex bg-white rounded-xl shadow-lg overflow-hidden">
        {/* 使用可拖拽的分割面板 */}
        <ResizablePanels
          leftPanel={
            <div className="flex flex-col h-full border-r border-l border-b border-gray-200">
              {/* 左侧标题栏 */}
              <header className="flex-shrink-0 bg-white border-b border-gray-200">
                <div className="px-6 py-4">
                  <div className="flex items-center justify-between">
                    <h1 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
                      <Sparkles className="w-5 h-5 text-blue-500" />
                      <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent font-bold tracking-tight">
                        ChatTable AI
                      </span>
                    </h1>
                    <button
                      onClick={() => window.location.reload()}
                      className="px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                      重新开始
                    </button>
                  </div>
                </div>
              </header>
              {/* 文件预览内容 */}
              <div className="flex-1 overflow-hidden">
                <FilePreview />
              </div>
            </div>
          }
          rightPanel={<ChatInterface />}
          defaultLeftWidth={35}
          minLeftWidth={25}
          maxLeftWidth={70}
        />
      </div>
    </div>
  );
};