# ChatTable AI 🤖📊

> 智能表格数据分析对话应用 - 让数据分析像聊天一样简单

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![React](https://img.shields.io/badge/React-19.1.1-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9+-blue.svg)](https://www.typescriptlang.org/)

## 📖 项目简介

ChatTable AI 是一个创新的智能表格数据分析对话应用，让用户能够通过自然语言与 Excel 和 CSV 文件进行交互。无需复杂的数据分析技能，只需上传文件并用日常语言提问，AI 就能帮您分析数据、生成图表、提供洞察。

### ✨ 核心价值

- 🚀 **零门槛数据分析** - 无需学习复杂的数据分析工具
- 💬 **自然语言交互** - 像聊天一样简单的数据查询体验
- 📊 **智能数据洞察** - AI 驱动的深度数据分析
- 🔄 **实时响应** - 流式对话，思考过程可视化

## 🎯 功能特性

### 📁 文件处理
- ✅ 支持 Excel (.xlsx, .xls) 和 CSV 文件上传
- ✅ 拖拽上传，支持文件格式验证
- ✅ 实时文件预览，显示前 200 行数据
- ✅ 文件基本信息统计（行数、列数、大小等）

### 💬 智能对话
- ✅ 自然语言数据查询
- ✅ AI 思考过程可视化
- ✅ 支持 Markdown 格式回答
- ✅ 代码块语法高亮
- ✅ 表格和图表展示

### 🔄 会话管理
- ✅ 多轮对话支持
- ✅ 会话历史保存
- ✅ 上下文理解
- ✅ 会话状态管理

### 🎨 用户体验
- ✅ 响应式设计，支持桌面和移动端
- ✅ 现代化 UI 设计
- ✅ 实时加载状态
- ✅ 错误处理和用户反馈

## 🛠 技术栈

### 前端技术
```
React 19.1.1        # 现代化前端框架
TypeScript 5.9+     # 类型安全的 JavaScript
Vite 7.1.7          # 快速构建工具
TailwindCSS 3.4     # 实用优先的 CSS 框架
Zustand 5.0         # 轻量级状态管理
Lucide React        # 现代图标库
React Markdown      # Markdown 渲染
```

### 后端技术
```
Python 3.8+         # 后端开发语言
FastAPI             # 现代化 Web 框架
Pandas              # 数据处理和分析
OpenAI API          # AI 对话能力
Uvicorn             # ASGI 服务器
Pydantic            # 数据验证
```

### 开发工具
```
ESLint              # 代码质量检查
TypeScript ESLint   # TypeScript 代码规范
Autoprefixer        # CSS 自动前缀
PostCSS             # CSS 处理工具
```

## 📁 项目结构

```
chat_table/
├── 📁 frontend/                 # React 前端应用
│   ├── 📁 src/
│   │   ├── 📁 components/       # React 组件
│   │   │   ├── ChatInput.tsx    # 聊天输入组件
│   │   │   ├── ChatInterface.tsx # 聊天界面组件
│   │   │   ├── FileUpload.tsx   # 文件上传组件
│   │   │   ├── FilePreview.tsx  # 文件预览组件
│   │   │   └── ...
│   │   ├── 📁 pages/           # 页面组件
│   │   ├── 📁 stores/          # 状态管理
│   │   ├── 📁 types/           # TypeScript 类型定义
│   │   ├── 📁 utils/           # 工具函数
│   │   └── 📁 hooks/           # 自定义 Hooks
│   ├── package.json
│   └── vite.config.ts
├── 📁 backend/                  # Python 后端应用
│   ├── 📁 app/
│   │   ├── 📁 api/             # API 路由
│   │   │   └── 📁 routes/      # 路由定义
│   │   ├── 📁 core/            # 核心配置
│   │   ├── 📁 models/          # 数据模型
│   │   └── 📁 services/        # 业务逻辑
│   │       ├── chat_service.py  # 聊天服务
│   │       ├── file_service.py  # 文件处理服务
│   │       └── session_service.py # 会话管理服务
│   ├── main.py                 # 应用入口
│   └── requirements.txt        # Python 依赖
├── 📁 tests/                   # 测试文件
└── README.md                   # 项目文档
```

## 🚀 快速开始

### 环境要求

- **Node.js** 18.0+ 
- **Python** 3.8+
- **npm** 或 **yarn**

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/your-username/chat_table.git
cd chat_table
```

2. **安装前端依赖**
```bash
cd frontend
npm install
```

3. **安装后端依赖**
```bash
cd ../backend
pip install -r requirements.txt
```

4. **环境配置**
```bash
# 在 backend 目录下创建 .env 文件
cp .env.example .env

# 编辑 .env 文件，添加必要的配置
OPENAI_API_KEY=your_openai_api_key_here
```

5. **启动应用**

启动后端服务：
```bash
cd backend
python main.py
```

启动前端服务：
```bash
cd frontend
npm run dev
```

6. **访问应用**
- 前端地址: http://localhost:5173
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

## 📖 使用说明

### 基本使用流程

1. **上传文件** 📁
   - 点击上传区域或拖拽 Excel/CSV 文件
   - 支持的格式：`.xlsx`, `.xls`, `.csv`
   - 文件大小限制：50MB

2. **预览数据** 👀
   - 文件上传成功后，左侧显示数据预览
   - 查看文件基本信息（行数、列数、大小）
   - 浏览前 200 行数据

3. **开始对话** 💬
   - 在右侧聊天框输入您的问题
   - 使用自然语言描述您想了解的内容
   - AI 会分析数据并提供答案

### 示例对话

```
👤 用户: 这个表格有多少行数据？

🤖 AI: 根据您上传的文件，这个表格共有 1,250 行数据，包含 8 个列。

👤 用户: 帮我分析一下销售额的分布情况

🤖 AI: 我来为您分析销售额的分布情况：

📊 **销售额统计摘要**
- 平均值：¥15,680
- 中位数：¥12,450  
- 最大值：¥89,500
- 最小值：¥1,200

| 区间 | 数量 | 占比 |
|------|------|------|
| 0-10K | 456 | 36.5% |
| 10K-30K | 623 | 49.8% |
| 30K+ | 171 | 13.7% |
```

## 🔌 API 文档概览

### 核心接口

#### 文件上传
```http
POST /api/upload
Content-Type: multipart/form-data

Parameters:
- file: File (required) - Excel 或 CSV 文件
- session_id: string (optional) - 会话 ID

Response:
{
  "success": true,
  "session_id": "sess_123456",
  "file_info": {
    "filename": "data.xlsx",
    "rows": 1000,
    "columns": 5,
    "size": "2.5MB"
  },
  "preview_data": [...]
}
```

#### 发送消息
```http
POST /api/chat/stream
Content-Type: application/json

Body:
{
  "message": "分析销售数据",
  "session_id": "sess_123456"
}

Response: Server-Sent Events
data: {"type": "thinking", "content": "正在分析数据..."}
data: {"type": "response", "content": "分析结果..."}
data: {"type": "done"}
```

#### 获取会话历史
```http
GET /api/chat/history/{session_id}

Response:
{
  "messages": [
    {
      "type": "user",
      "content": "用户消息",
      "timestamp": "2024-01-01T00:00:00Z"
    },
    {
      "type": "assistant", 
      "content": "AI 回复",
      "timestamp": "2024-01-01T00:00:01Z"
    }
  ]
}
```

## 🔧 开发指南

### 本地开发

1. **前端开发**
```bash
cd frontend
npm run dev          # 启动开发服务器
npm run build        # 构建生产版本
npm run lint         # 代码检查
```

2. **后端开发**
```bash
cd backend
python main.py       # 启动开发服务器
# 或使用 uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 代码规范

- **前端**: 使用 ESLint + TypeScript ESLint
- **后端**: 遵循 PEP 8 Python 代码规范
- **提交**: 使用语义化提交信息

### 测试

```bash
# 前端测试
cd frontend
npm run test

# 后端测试
cd backend
pytest
```

### 环境变量

创建 `backend/.env` 文件：
```env
# OpenAI API 配置
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# 应用配置
APP_NAME=ChatTable AI
DEBUG=true
HOST=0.0.0.0
PORT=8000

# 文件上传配置
MAX_FILE_SIZE=52428800  # 50MB
UPLOAD_DIR=./uploads
```

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 贡献方式

1. **报告问题** 🐛
   - 使用 GitHub Issues 报告 bug
   - 提供详细的重现步骤
   - 包含错误截图或日志

2. **功能建议** 💡
   - 在 Issues 中提出新功能建议
   - 描述功能的使用场景和价值

3. **代码贡献** 👨‍💻
   - Fork 项目到您的 GitHub
   - 创建功能分支：`git checkout -b feature/amazing-feature`
   - 提交更改：`git commit -m 'Add amazing feature'`
   - 推送分支：`git push origin feature/amazing-feature`
   - 创建 Pull Request

### 开发流程

1. 确保代码通过所有测试
2. 遵循项目的代码规范
3. 更新相关文档
4. 添加必要的测试用例

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [React](https://reactjs.org/) - 前端框架
- [FastAPI](https://fastapi.tiangolo.com/) - 后端框架
- [OpenAI](https://openai.com/) - AI 能力支持
- [TailwindCSS](https://tailwindcss.com/) - CSS 框架
- [Pandas](https://pandas.pydata.org/) - 数据处理

## 📞 联系我们

- 项目主页: [GitHub Repository](https://github.com/your-username/chat_table)
- 问题反馈: [GitHub Issues](https://github.com/your-username/chat_table/issues)
- 邮箱: your-email@example.com

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给我们一个 Star！**

Made with ❤️ by ChatTable Team

</div>