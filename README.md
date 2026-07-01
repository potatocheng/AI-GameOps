# AI智能游戏运营系统

基于LangChain构建的AI智能游戏运营Agent系统，具备自主规划、工具调用、多步推理能力。

## 技术栈

- **后端**: Python 3.10+ / FastAPI / LangChain / PostgreSQL
- **前端**: Vue.js 3 / TypeScript / Vite
- **AI**: OpenAI API / ChromaDB (向量数据库)
- **部署**: Docker / Docker Compose

## 功能特性

- 🤖 AI Agent自主规划与工具调用
- 📝 玩家反馈收集与管理
- 🔍 RAG知识库智能问答
- 😊 情感分析（正面/中性/负面）
- 📊 数据统计与可视化
- 📢 AI自动生成公告
- 💬 对话记忆管理

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd AIOperator
```

### 2. 配置环境变量

创建 `.env` 文件：

```env
OPENAI_API_KEY=your-openai-api-key

POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123
POSTGRES_DB=game_operator
```

### 3. 启动PostgreSQL

```bash
docker-compose up -d postgres
```

### 4. 安装依赖

**后端:**
```bash
pip install -r requirements.txt
```

**前端:**
```bash
cd frontend
npm install
```

### 5. 启动服务

**后端:**
```bash
python -m uvicorn app:app --reload --port 3000
```

**前端:**
```bash
cd frontend
npm run dev
```

## API文档

启动后端服务后访问: `http://localhost:3000/docs`

### 主要API端点

| 端点 | 方法 | 功能 |
|-----|------|------|
| `/api/feedback/` | POST | 提交反馈 |
| `/api/feedback/` | GET | 查询反馈列表 |
| `/api/agent/chat` | POST | AI对话 |
| `/api/agent/feedback/analyze` | POST | 情感分析 |
| `/api/stats/overview` | GET | 统计概览 |

## 项目结构

```
AIOperator/
├── agent/                # AI Agent核心
│   ├── agent.py         # Agent执行器
│   ├── tools.py         # 工具集
│   ├── memory.py        # 记忆管理
│   └── knowledge.py     # RAG知识库
├── routes/              # API路由
├── knowledge_base/      # 知识库文档
├── frontend/            # Vue前端
├── app.py              # FastAPI入口
└── docker-compose.yml  # Docker配置
```

## 许可证

MIT License