// 文件上传响应类型
interface UploadResponse {
  success: boolean;
  session_id: string;
  file_info: {
    filename: string;
    filepath: string;
    rows: number;
    columns: number;
    size: string;
    uploaded_at: string;
  };
  preview_data: Record<string, any>[];
}

// 聊天流式响应类型
interface ChatStreamEvent {
  type: 'thinking' | 'response' | 'error' | 'done';
  content?: string;
}

const API_BASE_URL = 'http://localhost:8000/api';

// 文件上传 API
export const uploadFile = async (file: File, sessionId?: string): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  if (sessionId) {
    formData.append('session_id', sessionId);
  }

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Upload failed: ${response.statusText}`);
  }

  return response.json();
};

// 流式聊天 API
export const sendMessage = async (
  message: string,
  sessionId: string,
  onEvent: (event: ChatStreamEvent) => void
): Promise<void> => {
  const response = await fetch(`${API_BASE_URL}/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      session_id: sessionId,
    }),
  });

  if (!response.ok) {
    throw new Error(`Chat failed: ${response.statusText}`);
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error('No response body');
  }

  const decoder = new TextDecoder();
  let buffer = '';

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') {
            onEvent({ type: 'done' });
            return;
          }
          
          try {
            const event: ChatStreamEvent = JSON.parse(data);
            onEvent(event);
          } catch (e) {
            console.warn('Failed to parse SSE data:', data);
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
};

// 获取会话历史 API
export const getChatHistory = async (sessionId: string) => {
  const response = await fetch(`${API_BASE_URL}/chat/history/${sessionId}`);
  
  if (!response.ok) {
    throw new Error(`Failed to get chat history: ${response.statusText}`);
  }

  return response.json();
};