# AlphaQuant AI API 文档

## 基础 URL
`http://localhost:8000/api/v1`

## 统一响应格式
```json
{"code": 0, "message": "success", "data": {}}
```

## 健康检查
- `GET /health` - 检查 API/数据库/Redis 状态

## 认证
- `POST /auth/register` - 用户注册 (username, email, password, full_name?)
- `POST /auth/login` - 用户登录 (username_or_email, password) -> access_token, refresh_token

## 股票数据
- `GET /stocks/search?keyword=&market=` - 搜索股票
- `GET /stocks/{symbol}/quote?market=` - 实时行情
- `GET /stocks/{symbol}/kline?market=&start_date=&end_date=&adjust=` - K线数据

## AI 分析
- `POST /analysis/stock` - AI 股票分析 (symbol, market, lookback_days)
  - 返回 Markdown 格式分析报告

## WebSocket
- `WS /ws/{channel}` - 实时数据订阅
