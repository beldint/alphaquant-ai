# AlphaQuant AI - Release Guide
# 股票分析平台 打包发布指南

## Overview / 概述

AlphaQuant AI is a professional stock analysis platform supporting:
- Real-time A-share market data
- Technical analysis (MACD, RSI, KDJ, BOLL, MA, etc.)
- Fundamental analysis (financial statements, valuation)
- AI-powered analysis reports
- Portfolio management
- Watchlist management

## Distribution Methods / 分发方式

Choose the method that best fits your environment:

---

### Method 1: One-Click Launcher (Python)
**Requires**: Python 3.11+
**Platforms**: Windows / macOS / Linux

```bash
# Windows
launch.bat

# macOS / Linux
chmod +x launch.sh && ./launch.sh
```

What it does:
1. Creates a Python virtual environment
2. Installs all Python dependencies
3. Builds the frontend (if Node.js is available)
4. Starts the server on http://localhost:8888
5. Opens the browser automatically

---

### Method 2: Docker Standalone
**Requires**: Docker
**Platforms**: Windows / macOS / Linux

```bash
# Single container with SQLite (no external DB needed)
docker compose -f docker-compose.standalone.yml up -d

# Open http://localhost:8888
```

---

### Method 3: Docker Full Stack (PostgreSQL + Redis)
**Requires**: Docker, more RAM
**Platforms**: Windows / macOS / Linux

```bash
# Multi-service setup with PostgreSQL + Redis + Nginx
cd docker
docker compose up -d

# Frontend: http://localhost:80
# Backend API: http://localhost:8000
```

---

### Method 4: Standalone Executable (PyInstaller)
**Requires**: Python 3.11+, PyInstaller
**Platforms**: Windows / macOS / Linux

```bash
pip install pyinstaller
python build_executable.py

# Output: dist/AlphaQuant-AI/
# Run the executable directly (no Python needed!)
```

---

## Configuration / 配置

### Environment Variables

Key settings in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| PORT | 8888 | Server port |
| DATABASE_ENGINE | sqlite | Database type (sqlite/postgresql/mysql) |
| DATABASE_URL | sqlite+aiosqlite:///./alphaquant.db | Database connection URL |
| DEEPSEEK_API_KEY | (empty) | AI analysis API key |
| JWT_SECRET_KEY | (change me) | Security key for JWT tokens |

### For production deployment:
```bash
# Use the production config file
cp .env.production .env
# Edit JWT_SECRET_KEY with a strong random value
# Optionally set DEEPSEEK_API_KEY for AI features
```

---

## Quick Start / 快速开始

### Windows
```bash
launch.bat
# The browser will open automatically at http://localhost:8888
```

### macOS / Linux
```bash
chmod +x launch.sh
./launch.sh
# The browser will open automatically at http://localhost:8888
```

### Docker (Any OS)
```bash
docker compose -f docker-compose.standalone.yml up -d
# Then open http://localhost:8888
```

---

## Project Structure / 项目结构

```
alphaquant-ai/
├── backend/               # FastAPI Python backend
│   ├── main.py           # Application entry point
│   ├── api/              # REST API endpoints
│   ├── core/             # Core config & exceptions
│   ├── database/         # SQLAlchemy models & session
│   ├── services/         # Business logic
│   ├── models/           # ORM models
│   ├── schemas/          # Pydantic schemas
│   ├── datasource/       # Stock data providers
│   ├── indicators/       # Technical indicators
│   └── ai/               # AI analysis module
├── frontend/             # Vue3 + TypeScript frontend
│   └── dist/            # Built static files
├── launch.py             # Cross-platform launcher
├── launch.bat            # Windows launcher
├── launch.sh             # Unix/macOS launcher
├── Dockerfile.standalone # Standalone Docker image
├── docker-compose.standalone.yml
├── .env.production       # Production config template
└── build_executable.py   # PyInstaller build script
```

---

## Note on Data Sources / 数据源说明

A-share stock data is sourced from public Chinese market data providers:
- Tencent Finance (primary)
- Sina Finance (backup)
- East Money (financial data)
- CNInfo (company filings)

No API key is needed for basic market data.
Set `DEEPSEEK_API_KEY` in `.env` to enable AI-powered analysis.

---

## License

AlphaQuant AI - For research and educational purposes only.
