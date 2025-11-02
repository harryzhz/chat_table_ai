import { create } from 'zustand';

// 类型定义
interface FileInfo {
  filename: string;
  filepath: string;
  rows: number;
  columns: number;
  size: string;
  uploaded_at: string;
}

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  thinking?: string;
  timestamp: string;
}

interface Session {
  id: string;
  created_at: string;
  updated_at: string;
  status: 'active' | 'inactive';
  file_info?: FileInfo;
  messages: Message[];
}

type PreviewData = Record<string, any>[];

interface AppStore {
  // 状态
  session: Session | null;
  previewData: PreviewData;
  isUploading: boolean;
  isChatting: boolean;
  error: string | null;
  
  // 操作
  setSession: (session: Session) => void;
  setPreviewData: (data: PreviewData) => void;
  setUploading: (uploading: boolean) => void;
  setChatting: (chatting: boolean) => void;
  setError: (error: string | null) => void;
  addMessage: (message: Message) => void;
  updateLastMessage: (content: string, thinking?: string) => void;
  clearSession: () => void;
}

export const useAppStore = create<AppStore>((set, get) => ({
  // 初始状态
  session: null,
  previewData: [],
  isUploading: false,
  isChatting: false,
  error: null,

  // 操作方法
  setSession: (session) => set({ session }),
  
  setPreviewData: (data) => set({ previewData: data }),
  
  setUploading: (uploading) => set({ isUploading: uploading }),
  
  setChatting: (chatting) => set({ isChatting: chatting }),
  
  setError: (error) => set({ error }),
  
  addMessage: (message) => {
    const { session } = get();
    if (session) {
      const updatedSession = {
        ...session,
        messages: [...session.messages, message],
        updated_at: new Date().toISOString(),
      };
      set({ session: updatedSession });
    }
  },
  
  updateLastMessage: (content, thinking) => {
    const { session } = get();
    if (session && session.messages.length > 0) {
      const messages = [...session.messages];
      const lastMessage = messages[messages.length - 1];
      
      if (lastMessage.type === 'assistant') {
        messages[messages.length - 1] = {
          ...lastMessage,
          content: content || lastMessage.content,
          thinking: thinking !== undefined ? thinking : lastMessage.thinking,
        };
        
        const updatedSession = {
          ...session,
          messages,
          updated_at: new Date().toISOString(),
        };
        set({ session: updatedSession });
      }
    }
  },
  
  clearSession: () => set({ 
    session: null, 
    previewData: [], 
    error: null 
  }),
}));