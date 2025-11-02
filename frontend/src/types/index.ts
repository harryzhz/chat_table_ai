// 会话相关类型
export interface Session {
  id: string;
  created_at: string;
  updated_at: string;
  status: 'active' | 'inactive';
  file_info?: FileInfo;
  messages: Message[];
}

// 文件信息类型
export interface FileInfo {
  filename: string;
  filepath: string;
  rows: number;
  columns: number;
  size: string;
  uploaded_at: string;
}

// 消息类型
export interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  thinking?: string;
  timestamp: string;
}

// 文件上传响应类型
export interface UploadResponse {
  success: boolean;
  session_id: string;
  file_info: FileInfo;
  preview_data: Record<string, any>[];
}

// 聊天流式响应类型
export interface ChatStreamEvent {
  type: 'thinking' | 'response' | 'error' | 'done';
  content?: string;
}

// 应用状态类型
export interface AppState {
  session: Session | null;
  isUploading: boolean;
  isChatting: boolean;
  error: string | null;
}

// 文件预览数据类型
export type PreviewData = Record<string, any>[];