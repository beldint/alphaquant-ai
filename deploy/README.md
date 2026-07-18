# AlphaQuant AI 部署指南

## 系统要求
- Docker 24+ 与 Docker Compose v2
- Python 3.11.9+
- Node.js 20+
- PostgreSQL 16
- Redis 7

## Docker 快速部署

```bash
cp .env.example .env
docker compose -f docker/docker-compose.yml up -d --build
docker compose -f docker/docker-compose.yml ps
```

服务地址：
- 前端：http://localhost
- 后端健康检查：http://localhost:8000/api/v1/health
- API 文档：http://localhost:8000/docs

## 数据初始化

```bash
python scripts/init_db.py
python scripts/init_data.py
```

## 本地开发启动

后端：

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

前端：

```bash
cd frontend
npm install
npm run dev
```

## Railway/Heroku 类平台

`Procfile` 已配置后端启动命令：

```bash
web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

部署前需要在平台变量中配置：
- `DATABASE_URL`
- `REDIS_URL`
- `JWT_SECRET_KEY`
- `DEEPSEEK_API_KEY` 或其他 AI 服务 Key
- `TUSHARE_TOKEN` 与股票数据源 Key（可选）

## Cloudflare Pages 前端

构建配置：
- Build command: `npm run build`
- Build output directory: `dist`
- Root directory: `frontend`

`frontend/functions/api/[[path]].ts` 会为 Pages Functions 提供行情、K线、财务和评分兜底 API，并在不可用时回退到后端服务。

## 发布检查

```bash
cd frontend
npm run build

cd ..
python -m pytest
```

最后确认：
- `.env` 已按目标环境修改
- 数据库和 Redis 可连接
- 前端构建产物存在于 `frontend/dist`
- 健康检查返回 `code=0`
