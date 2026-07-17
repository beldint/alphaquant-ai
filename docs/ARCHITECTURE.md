# AlphaQuant AI 架构文档

## 技术栈
- **后端**: Python 3.11, FastAPI, SQLAlchemy (async), PostgreSQL, Redis
- **前端**: Vue 3, TypeScript, Vite, Pinia, ECharts, naive-ui
- **任务队列**: Celery + Redis
- **定时任务**: APScheduler
- **数据源**: AKShare (A股), 预留 Tushare/BaoStock 等
- **AI**: 兼容 OpenAI-compatible 接口 (DeepSeek, OpenAI, Claude 等)
- **部署**: Docker Compose

## 项目结构
```
stock-analysis/
├── backend/            # FastAPI 后端
│   ├── api/           # API 路由 (v1)
│   ├── ai/            # AI 分析 (providers)
│   ├── cache/         # Redis 缓存
│   ├── core/          # 核心配置、异常、安全
│   ├── database/      # SQLAlchemy 异步引擎
│   ├── datasource/    # 数据源 (AKShare)
│   ├── indicators/    # 技术指标 (MA, MACD, RSI, KDJ 等)
│   ├── middleware/     # 中间件
│   ├── models/        # ORM 模型
│   ├── repository/    # 通用 CRUD 仓库
│   ├── scheduler/     # APScheduler 任务
│   ├── schemas/       # Pydantic 请求/响应
│   ├── services/      # 业务服务层
│   ├── tasks/         # Celery 任务
│   ├── utils/         # 工具函数
│   ├── websocket/     # WebSocket 管理器
│   └── main.py        # 应用入口
├── frontend/           # Vue 3 前端
│   └── src/
│       ├── api/       # API 客户端
│       ├── assets/    # 样式/资源
│       ├── components/# 通用组件
│       ├── router/    # 路由配置
│       ├── stores/    # Pinia 状态管理
│       └── views/     # 页面视图
├── docker/             # Docker 配置
├── deploy/             # 部署文档
├── docs/               # 项目文档
├── scripts/            # 数据库脚本
└── .env.example        # 环境变量模板
```

## API 端点
详见 API.md
