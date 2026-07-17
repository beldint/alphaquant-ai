# AlphaQuant AI 部署指南

## 系统要求
- Docker & Docker Compose
- Python 3.11.9+
- Node.js 20+

## 快速启动（Docker）

```bash
# 1. 复制环境变量
cp .env.example .env
# 编辑 .env 填入 DEEPSEEK_API_KEY 等配置

# 2. 启动所有服务
docker compose -f docker/docker-compose.yml up -d

# 3. 访问 http://localhost
```

## 手动启动

### 后端
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

### 前端
```bash
cd frontend
npm install
npm run dev
```

## 初始化数据库
```bash
python scripts/init_db.py
python scripts/init_data.py
```

## 环境变量
参见 `.env.example` 获取完整配置说明。
