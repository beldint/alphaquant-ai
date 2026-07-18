# AlphaQuant AI

专业级 AI 股票分析平台，提供实时行情、技术分析、基本面分析和 AI 智能分析报告。

## 功能特性

### 行情中心
- 股票搜索（A 股、港股、美股）
- 实时行情数据
- K线图（日K，支持 MA5/10/20）
- 多周期切换（1月/3月/6月）

### 技术分析
- MA, EMA, MACD, BOLL
- RSI, KDJ, CCI, WR, ROC
- ATR, DMI, SAR
- OBV, VOL, VR
- PSY, MFI, BIAS, TRIX

### AI 分析
- 自动生成技术分析报告
- 技术指标共振分析
- 风险提示
- 趋势判断

### 持仓管理
- 投资组合追踪
- 盈亏统计
- 自选股管理

## 快速开始

### Docker 部署（推荐）
```bash
cp .env.example .env
# 编辑 .env 配置 DEEPSEEK_API_KEY
docker compose -f docker/docker-compose.yml up -d
```

### 手动启动
```bash
# 后端
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000

# 前端
cd frontend
npm install
npm run dev
```

## 技术栈
- **后端**: Python 3.11, FastAPI, SQLAlchemy (async), PostgreSQL, Redis
- **前端**: Vue 3, TypeScript, Vite, Pinia, ECharts, naive-ui
- **数据源**: AKShare
- **AI**: DeepSeek / OpenAI / Claude 等

## 项目结构
```
stock-analysis/
├── backend/          # FastAPI 后端
├── frontend/         # Vue 3 前端
├── docker/           # Docker 配置
├── deploy/           # 部署文档
├── docs/             # 项目文档
├── scripts/          # 数据库脚本
├── .env.example      # 环境变量模板
└── pyproject.toml    # Python 项目配置
```


> Deployed on Railway + Cloudflare Pages
# Last build: 2026-07-18 12:49:56.448050
