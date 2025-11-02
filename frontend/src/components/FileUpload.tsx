import React, { useCallback, useState } from 'react';
import { Upload, FileText, AlertCircle, CheckCircle } from 'lucide-react';
import { validateFileType, formatFileSize } from '../utils/helpers';
import { uploadFile } from '../utils/api';
import { useAppStore } from '../stores/appStore';

interface FileUploadProps {
  onUploadSuccess?: () => void;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onUploadSuccess }) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const { setSession, setPreviewData, setUploading, setError, isUploading } = useAppStore();

  const handleFileUpload = useCallback(async (file: File) => {
    if (!validateFileType(file)) {
      setError('请上传 Excel (.xlsx, .xls) 或 CSV (.csv) 格式的文件');
      return;
    }

    setUploading(true);
    setError(null);
    setUploadProgress(0);

    try {
      // 模拟上传进度
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + 10;
        });
      }, 100);

      const response = await uploadFile(file);
      
      clearInterval(progressInterval);
      setUploadProgress(100);

      // 创建新会话
      const newSession = {
        id: response.session_id,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        status: 'active' as const,
        file_info: response.file_info,
        messages: [],
      };

      setSession(newSession);
      setPreviewData(response.preview_data);
      
      setTimeout(() => {
        setUploadProgress(0);
        onUploadSuccess?.();
      }, 500);

    } catch (error) {
      setError(error instanceof Error ? error.message : '文件上传失败');
      setUploadProgress(0);
    } finally {
      setUploading(false);
    }
  }, [setSession, setPreviewData, setUploading, setError, onUploadSuccess]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  }, [handleFileUpload]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileUpload(files[0]);
    }
  }, [handleFileUpload]);

  return (
    <div className="w-full max-w-md mx-auto">
      <div
        className={`
          relative border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200
          ${isDragOver 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-gray-300 hover:border-gray-400'
          }
          ${isUploading ? 'pointer-events-none opacity-75' : 'cursor-pointer'}
        `}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => !isUploading && document.getElementById('file-input')?.click()}
      >
        <input
          id="file-input"
          type="file"
          accept=".xlsx,.xls,.csv"
          onChange={handleFileSelect}
          className="hidden"
          disabled={isUploading}
        />

        {isUploading ? (
          <div className="space-y-4">
            <div className="animate-spin mx-auto w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full" />
            <div className="space-y-2">
              <p className="text-sm text-gray-600">上传中...</p>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
              <p className="text-xs text-gray-500">{uploadProgress}%</p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <Upload className="mx-auto w-12 h-12 text-gray-400" />
            <div className="space-y-2">
              <p className="text-lg font-medium text-gray-700">
                拖拽文件到这里或点击上传
              </p>
              <p className="text-sm text-gray-500">
                支持 Excel (.xlsx, .xls) 和 CSV (.csv) 格式
              </p>
            </div>
          </div>
        )}
      </div>

      {/* 文件格式说明 */}
      <div className="mt-4 p-3 bg-gray-50 rounded-lg">
        <div className="flex items-start space-x-2">
          <FileText className="w-4 h-4 text-gray-500 mt-0.5" />
          <div className="text-xs text-gray-600">
            <p className="font-medium mb-1">支持的文件格式：</p>
            <ul className="space-y-1">
              <li>• Excel 文件 (.xlsx, .xls)</li>
              <li>• CSV 文件 (.csv)</li>
              <li>• 最大文件大小：10MB</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};