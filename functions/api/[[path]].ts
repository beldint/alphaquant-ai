const SEARCH_PATH = /\/api\/v1\/stocks\/search$/;

const STOCKS = [
  { symbol: "000001", name: "\u5e73\u5b89\u94f6\u884c", exchange: "SZSE", industry: "\u94f6\u884c" },
  { symbol: "000002", name: "\u4e07\u79d1A", exchange: "SZSE", industry: "\u623f\u5730\u4ea7" },
  { symbol: "000333", name: "\u7f8e\u7684\u96c6\u56e2", exchange: "SZSE", industry: "\u5bb6\u7528\u7535\u5668" },
  { symbol: "000651", name: "\u683c\u529b\u7535\u5668", exchange: "SZSE", industry: "\u5bb6\u7528\u7535\u5668" },
  { symbol: "000725", name: "\u4eac\u4e1c\u65b9A", exchange: "SZSE", industry: "\u7535\u5b50" },
  { symbol: "000858", name: "\u4e94\u7cae\u6db2", exchange: "SZSE", industry: "\u98df\u54c1\u996e\u6599" },
  { symbol: "002230", name: "\u79d1\u5927\u8baf\u98de", exchange: "SZSE", industry: "\u8ba1\u7b97\u673a" },
  { symbol: "002415", name: "\u6d77\u5eb7\u5a01\u89c6", exchange: "SZSE", industry: "\u8ba1\u7b97\u673a" },
  { symbol: "002475", name: "\u7acb\u8baf\u7cbe\u5bc6", exchange: "SZSE", industry: "\u7535\u5b50" },
  { symbol: "002594", name: "\u6bd4\u4e9a\u8fea", exchange: "SZSE", industry: "\u6c7d\u8f66" },
  { symbol: "300014", name: "\u4ebf\u7eac\u9502\u80fd", exchange: "SZSE", industry: "\u7535\u529b\u8bbe\u5907" },
  { symbol: "300015", name: "\u7231\u5c14\u773c\u79d1", exchange: "SZSE", industry: "\u533b\u836f\u751f\u7269" },
  { symbol: "300059", name: "\u4e1c\u65b9\u8d22\u5bcc", exchange: "SZSE", industry: "\u975e\u94f6\u878d\u91d1" },
  { symbol: "300124", name: "\u6c47\u5ddd\u6280\u672f", exchange: "SZSE", industry: "\u7535\u529b\u8bbe\u5907" },
  { symbol: "300274", name: "\u9633\u5149\u7535\u6e90", exchange: "SZSE", industry: "\u7535\u529b\u8bbe\u5907" },
  { symbol: "300308", name: "\u4e2d\u9645\u65ed\u521b", exchange: "SZSE", industry: "\u901a\u4fe1" },
  { symbol: "300502", name: "\u65b0\u6613\u76db", exchange: "SZSE", industry: "\u901a\u4fe1" },
  { symbol: "300750", name: "\u5b81\u5fb7\u65f6\u4ee3", exchange: "SZSE", industry: "\u7535\u529b\u8bbe\u5907" },
  { symbol: "300760", name: "\u8fc8\u745e\u533b\u7597", exchange: "SZSE", industry: "\u533b\u836f\u751f\u7269" },
  { symbol: "600000", name: "\u6d66\u53d1\u94f6\u884c", exchange: "SSE", industry: "\u94f6\u884c" },
  { symbol: "600009", name: "\u4e0a\u6d77\u673a\u573a", exchange: "SSE", industry: "\u7efc\u5408" },
  { symbol: "600016", name: "\u6c11\u751f\u94f6\u884c", exchange: "SSE", industry: "\u94f6\u884c" },
  { symbol: "600030", name: "\u4e2d\u4fe1\u8bc1\u5238", exchange: "SSE", industry: "\u8bc1\u5238" },
  { symbol: "600036", name: "\u62db\u5546\u94f6\u884c", exchange: "SSE", industry: "\u94f6\u884c" },
  { symbol: "600276", name: "\u6052\u745e\u533b\u836f", exchange: "SSE", industry: "\u533b\u836f\u751f\u7269" },
  { symbol: "600309", name: "\u4e07\u534e\u5316\u5b66", exchange: "SSE", industry: "\u57fa\u7840\u5316\u5de5" },
  { symbol: "600519", name: "\u8d35\u5dde\u8305\u53f0", exchange: "SSE", industry: "\u98df\u54c1\u996e\u6599" },
  { symbol: "600690", name: "\u6d77\u5c14\u667a\u5bb6", exchange: "SSE", industry: "\u5bb6\u7528\u7535\u5668" },
  { symbol: "600745", name: "\u95fb\u6cf0\u79d1\u6280", exchange: "SSE", industry: "\u7535\u5b50" },
  { symbol: "600809", name: "\u5c71\u897f\u6c7e\u9152", exchange: "SSE", industry: "\u98df\u54c1\u996e\u6599" },
  { symbol: "600887", name: "\u4f0a\u5229\u80a1\u4efd", exchange: "SSE", industry: "\u98df\u54c1\u996e\u6599" },
  { symbol: "600900", name: "\u957f\u6c5f\u7535\u529b", exchange: "SSE", industry: "\u516c\u5171\u4e8b\u4e1a" },
  { symbol: "600941", name: "\u4e2d\u56fd\u79fb\u52a8", exchange: "SSE", industry: "\u901a\u4fe1" },
  { symbol: "601088", name: "\u4e2d\u56fd\u795e\u534e", exchange: "SSE", industry: "\u7164\u70ad" },
  { symbol: "601166", name: "\u5174\u4e1a\u94f6\u884c", exchange: "SSE", industry: "\u94f6\u884c" },
  { symbol: "601318", name: "\u4e2d\u56fd\u5e73\u5b89", exchange: "SSE", industry: "\u975e\u94f6\u878d\u91d1" },
  { symbol: "601398", name: "\u5de5\u5546\u94f6\u884c", exchange: "SSE", industry: "\u94f6\u884c" },
  { symbol: "601766", name: "\u4e2d\u56fd\u4e2d\u8f66", exchange: "SSE", industry: "\u673a\u68b0\u8bbe\u5907" },
  { symbol: "601857", name: "\u4e2d\u56fd\u77f3\u6cb9", exchange: "SSE", industry: "\u77f3\u6cb9\u77f3\u5316" },
  { symbol: "601899", name: "\u7d2b\u91d1\u77ff\u4e1a", exchange: "SSE", industry: "\u6709\u8272\u91d1\u5c5e" },
  { symbol: "603259", name: "\u836f\u660e\u5eb7\u5fb7", exchange: "SSE", industry: "\u533b\u836f\u751f\u7269" },
  { symbol: "688981", name: "\u4e2d\u82af\u56fd\u9645", exchange: "SSE", industry: "\u7535\u5b50" },
];

function secid(symbol) {
  return symbol.startsWith("6") || symbol.startsWith("9") ? "1." + symbol : "0." + symbol;
}

function yahooSym(symbol) {
  return symbol.startsWith("6") ? symbol + ".SS" : symbol + ".SZ";
}

function apiResponse(data) {
  return new Response(JSON.stringify(data), {
    headers: { "Content-Type": "application/json; charset=utf-8" },
  });
}

function railFetch(url, method, headers, body) {
  return fetch("https://alphaquant-ai-production.up.railway.app" + url.pathname + url.search, {
    method,
    headers,
    body,
  });
}

function normalizeStock(item) {
  return {
    symbol: item.symbol || item.s || "",
    name: item.name || item.n || "",
    market: item.market || "A",
    exchange: item.exchange || item.e || "SZSE",
    industry: item.industry || INDUSTRY_BY_SYMBOL[item.symbol || item.s || ""] || null,
  };
}

const INDUSTRY_BY_SYMBOL = {
  "000001": "\u94f6\u884c",
  "000002": "\u623f\u5730\u4ea7",
  "000333": "\u5bb6\u7528\u7535\u5668",
  "000651": "\u5bb6\u7528\u7535\u5668",
  "000725": "\u7535\u5b50",
  "000858": "\u98df\u54c1\u996e\u6599",
  "002230": "\u8ba1\u7b97\u673a",
  "002415": "\u8ba1\u7b97\u673a",
  "002475": "\u7535\u5b50",
  "002594": "\u6c7d\u8f66",
  "300014": "\u7535\u529b\u8bbe\u5907",
  "300015": "\u533b\u836f\u751f\u7269",
  "300059": "\u975e\u94f6\u878d\u91d1",
  "300124": "\u7535\u529b\u8bbe\u5907",
  "300274": "\u7535\u529b\u8bbe\u5907",
  "300308": "\u901a\u4fe1",
  "300502": "\u901a\u4fe1",
  "300750": "\u7535\u529b\u8bbe\u5907",
  "300760": "\u533b\u836f\u751f\u7269",
  "600000": "\u94f6\u884c",
  "600009": "\u7efc\u5408",
  "600016": "\u94f6\u884c",
  "600030": "\u8bc1\u5238",
  "600036": "\u94f6\u884c",
  "600276": "\u533b\u836f\u751f\u7269",
  "600309": "\u57fa\u7840\u5316\u5de5",
  "600519": "\u98df\u54c1\u996e\u6599",
  "600690": "\u5bb6\u7528\u7535\u5668",
  "600745": "\u7535\u5b50",
  "600809": "\u98df\u54c1\u996e\u6599",
  "600887": "\u98df\u54c1\u996e\u6599",
  "600900": "\u516c\u5171\u4e8b\u4e1a",
  "600941": "\u901a\u4fe1",
  "601088": "\u7164\u70ad",
  "601166": "\u94f6\u884c",
  "601318": "\u975e\u94f6\u878d\u91d1",
  "601398": "\u94f6\u884c",
  "601766": "\u673a\u68b0\u8bbe\u5907",
  "601857": "\u77f3\u6cb9\u77f3\u5316",
  "601899": "\u6709\u8272\u91d1\u5c5e",
  "603259": "\u533b\u836f\u751f\u7269",
  "688981": "\u7535\u5b50",
};

function searchLocalStocks(keyword) {
  const kw = keyword.trim();
  const upper = kw.toUpperCase();
  if (!kw) return [];
  return STOCKS.filter((stock) => stock.symbol.includes(upper) || stock.name.includes(kw))
    .slice(0, 20)
    .map(normalizeStock);
}

async function searchEastMoney(keyword) {
  const endpoint = "https://searchadapter.eastmoney.com/api/suggest/get_SearchSuggestList";
  const target = endpoint + "?input=" + encodeURIComponent(keyword) + "&type=14&token=D43BF722C8E33BDC906FB84D85E326E8";
  const response = await fetch(target, { headers: { "User-Agent": "Mozilla/5.0" } });
  if (!response.ok) return [];
  const payload = await response.json();
  const rows = Array.isArray(payload?.Data) ? payload.Data : [];
  return rows
    .filter((row) => row?.Code && row?.Name)
    .map((row) => {
      const symbol = String(row.Code).padStart(6, "0");
      return normalizeStock({
        symbol,
        name: String(row.Name),
        exchange: symbol.startsWith("6") || symbol.startsWith("9") ? "SSE" : "SZSE",
      });
    })
    .slice(0, 20);
}

async function handleSearch(keyword) {
  const localResults = searchLocalStocks(keyword);
  if (localResults.length > 0) return localResults;
  try {
    const remoteResults = await searchEastMoney(keyword);
    if (remoteResults.length > 0) return remoteResults;
  } catch (error) {
    console.error("stock search provider failed", error);
  }
  return [];
}

function parseAnalysisPayload(requestText, url) {
  try {
    const payload = requestText ? JSON.parse(requestText) : {};
    return payload && typeof payload === "object" ? payload : {};
  } catch (error) {
    console.error("analysis payload parse failed", error);
  }
  return {
    symbol: url.searchParams.get("symbol") || "000001",
    market: url.searchParams.get("market") || "A",
    lookback_days: Number(url.searchParams.get("lookback_days") || 120),
    model: url.searchParams.get("model") || "",
  };
}

function stockDisplayName(symbol) {
  const item = STOCKS.find((stock) => stock.symbol === symbol);
  return item ? item.name : symbol;
}

function roundNumber(value, digits = 2) {
  if (!Number.isFinite(value)) return null;
  return Number(value.toFixed(digits));
}

async function fetchQuoteFallback(symbol) {
  try {
    const response = await fetch(
      "https://push2.eastmoney.com/api/qt/stock/get?secid=" + secid(symbol) + "&fields=f43,f44,f45,f46,f47,f48,f169,f170,f57,f58",
      { headers: { "User-Agent": "Mozilla/5.0" } },
    );
    const payload = await response.json();
    const data = payload.data || {};
    if (data.f43) {
      return {
        symbol,
        name: data.f58 || stockDisplayName(symbol),
        market: "A",
        price: data.f43 / 100,
        change: data.f169 / 100,
        pct_change: data.f170 / 100,
        volume: data.f47 || 0,
        amount: data.f48 || 0,
        timestamp: new Date().toISOString(),
        source: "eastmoney",
      };
    }
  } catch (error) {
    console.error("analysis quote fallback failed", error);
  }
  return {
    symbol,
    name: stockDisplayName(symbol),
    market: "A",
    price: null,
    change: null,
    pct_change: null,
    volume: null,
    amount: null,
    timestamp: new Date().toISOString(),
    source: "edge-fallback",
  };
}

async function fetchKlineFallback(symbol, lookbackDays) {
  const end = new Date();
  const start = new Date(end.getTime() - Math.max(Number(lookbackDays) || 120, 20) * 86400000);
  const beg = start.toISOString().slice(0, 10).replace(/-/g, "");
  const finish = end.toISOString().slice(0, 10).replace(/-/g, "");
  try {
    const response = await fetch(
      "https://push2.eastmoney.com/api/qt/stock/kline/get?secid=" + secid(symbol) + "&klt=101&fqt=1&beg=" + beg + "&end=" + finish,
      { headers: { "User-Agent": "Mozilla/5.0" } },
    );
    const payload = await response.json();
    const raw = (payload.data || {}).klines || [];
    return raw.map((row) => {
      const parts = row.split(",");
      return {
        trade_date: parts[0],
        open_price: parseFloat(parts[1]),
        close_price: parseFloat(parts[2]),
        high_price: parseFloat(parts[3]),
        low_price: parseFloat(parts[4]),
        volume: parseInt(parts[5], 10),
        amount: parseFloat(parts[6]),
      };
    }).filter((row) => row.trade_date && Number.isFinite(row.close_price));
  } catch (error) {
    console.error("analysis kline fallback failed", error);
  }
  return [];
}

function summarizeKline(rows) {
  const closes = rows.map((row) => row.close_price).filter((value) => Number.isFinite(value));
  const volumes = rows.map((row) => row.volume).filter((value) => Number.isFinite(value));
  if (closes.length === 0) {
    return {
      trend: "数据不足",
      close: null,
      change_pct: null,
      ma5: null,
      ma20: null,
      high: null,
      low: null,
      avg_volume: null,
    };
  }
  const last = closes[closes.length - 1];
  const first = closes[0];
  const sliceAverage = (items, count) => items.slice(-Math.min(count, items.length)).reduce((sum, value) => sum + value, 0) / Math.min(count, items.length);
  const ma5 = sliceAverage(closes, 5);
  const ma20 = sliceAverage(closes, 20);
  let trend = "震荡";
  if (last > ma5 && ma5 > ma20) trend = "短期偏强";
  if (last < ma5 && ma5 < ma20) trend = "短期偏弱";
  return {
    trend,
    close: roundNumber(last),
    change_pct: first ? roundNumber(((last - first) / first) * 100) : null,
    ma5: roundNumber(ma5),
    ma20: roundNumber(ma20),
    high: roundNumber(Math.max(...closes)),
    low: roundNumber(Math.min(...closes)),
    avg_volume: volumes.length ? Math.round(volumes.reduce((sum, value) => sum + value, 0) / volumes.length) : null,
  };
}

async function buildFallbackAnalysis(payload) {
  const symbol = String(payload.symbol || "000001").trim() || "000001";
  const market = String(payload.market || "A");
  const lookbackDays = Number(payload.lookback_days || payload.lookbackDays || 120);
  const model = String(payload.model || "edge-fallback");
  const quote = await fetchQuoteFallback(symbol);
  const klineRows = await fetchKlineFallback(symbol, lookbackDays);
  const technical = summarizeKline(klineRows);
  const dataTimestamp = new Date().toISOString();
  const priceLine = quote.price == null ? "当前行情暂不可用" : `现价 ${roundNumber(quote.price)}，涨跌幅 ${roundNumber(quote.pct_change || 0)}%`;
  const report = [
    `# ${quote.name || stockDisplayName(symbol)}(${symbol}) AI 分析报告`,
    "",
    `生成时间：${dataTimestamp}`,
    `数据来源：Cloudflare Pages 边缘兜底，Railway 后端暂不可用`,
    "",
    "## 行情概览",
    `- ${priceLine}`,
    `- 回看周期：${lookbackDays} 天，样本数量：${klineRows.length}`,
    `- 区间涨跌幅：${technical.change_pct == null ? "数据不足" : technical.change_pct + "%"}`,
    "",
    "## 技术面",
    `- 趋势判断：${technical.trend}`,
    `- MA5：${technical.ma5 ?? "无"}，MA20：${technical.ma20 ?? "无"}`,
    `- 区间高点：${technical.high ?? "无"}，区间低点：${technical.low ?? "无"}`,
    `- 平均成交量：${technical.avg_volume ?? "无"}`,
    "",
    "## 风险提示",
    "- 当前报告由边缘兜底逻辑生成，未调用完整 AI 后端和完整财务数据库。",
    "- Railway 后端恢复后，系统会自动返回完整模型分析报告。",
    "- 若价格、成交量或财务数据缺失，应等待数据源恢复后重新分析。",
    "",
    "## 操作观察",
    technical.trend === "短期偏强"
      ? "- 短线趋势相对积极，可继续观察成交量是否同步放大。"
      : technical.trend === "短期偏弱"
        ? "- 短线趋势偏弱，优先关注均线修复和止跌信号。"
        : "- 当前趋势偏震荡，适合结合支撑压力位和成交量变化继续跟踪。",
  ].join("\n");

  return {
    symbol,
    market,
    provider: "cloudflare-pages-fallback",
    model,
    report_markdown: report,
    objective_data: {
      quote,
      kline_points: klineRows.length,
      fallback: true,
      origin_error: "railway_bad_gateway",
    },
    technical_summary: technical,
    risk_summary: {
      data_quality: klineRows.length > 0 ? "partial" : "limited",
      origin_available: false,
      retry_recommended: true,
    },
    data_timestamp: dataTimestamp,
  };
}

export async function onRequest(context) {
  const url = new URL(context.request.url);
  const path = url.pathname;

  if (!path.startsWith("/api/")) {
    const resp = await context.env.ASSETS.fetch(context.request).catch(() => null);
    if (resp && resp.status !== 404) return resp;
    const idxUrl = new URL(context.request.url);
    idxUrl.pathname = "/index.html";
    return context.env.ASSETS.fetch(new Request(idxUrl)).catch(() => new Response("Not Found", { status: 404 }));
  }

  const method = context.request.method;
  const hdrs = context.request.headers;
  const body = context.request.body;
  const rail = () => railFetch(url, method, hdrs, body);

  if (path === "/api/v1/analysis/stock") {
    const requestText = await context.request.clone().text().catch(() => "{}");
    try {
      const response = await railFetch(url, method, hdrs, method === "GET" || method === "HEAD" ? undefined : requestText);
      if (response.ok) return response;
      console.error("railway analysis failed", response.status);
    } catch (error) {
      console.error("railway analysis unavailable", error);
    }
    const payload = parseAnalysisPayload(requestText, url);
    return apiResponse({ code: 0, message: "success", data: await buildFallbackAnalysis(payload) });
  }

  if (SEARCH_PATH.test(path)) {
    const keyword = url.searchParams.get("keyword") || "";
    const results = await handleSearch(keyword);
    if (results.length > 0) {
      return apiResponse({ code: 0, message: "success", data: results });
    }
    const response = await rail();
    if (response.ok) return response;
    return apiResponse({ code: 0, message: "success", data: [] });
  }

  const quoteMatch = path.match(/\/api\/v1\/stocks\/(\d+)\/quote$/);
  if (quoteMatch) {
    const symbol = quoteMatch[1];
    try {
      const response = await fetch(
        "https://push2.eastmoney.com/api/qt/stock/get?secid=" + secid(symbol) + "&fields=f43,f44,f45,f46,f47,f48,f169,f170,f57,f58",
        { headers: { "User-Agent": "Mozilla/5.0" } },
      );
      const payload = await response.json();
      const data = payload.data || {};
      if (data.f43) {
        return apiResponse({
          code: 0,
          message: "success",
          data: {
            symbol,
            name: data.f58 || symbol,
            market: "A",
            price: data.f43 / 100,
            change: data.f169 / 100,
            pct_change: data.f170 / 100,
            volume: data.f47 || 0,
            amount: data.f48 || 0,
            timestamp: new Date().toISOString(),
            source: "eastmoney",
          },
        });
      }
    } catch (error) {
      console.error("eastmoney quote failed", error);
    }

    try {
      const response = await fetch("https://query1.finance.yahoo.com/v8/finance/chart/" + yahooSym(symbol) + "?interval=1d&range=5d", {
        headers: { "User-Agent": "Mozilla/5.0" },
      });
      const payload = await response.json();
      const meta = payload.chart.result[0].meta;
      const close = meta.regularMarketPrice;
      const prev = meta.chartPreviousClose;
      return apiResponse({
        code: 0,
        message: "success",
        data: {
          symbol,
          name: meta.symbol || symbol,
          market: "A",
          price: close,
          change: close - prev,
          pct_change: ((close - prev) / prev) * 100,
          volume: meta.regularMarketVolume || 0,
          amount: 0,
          timestamp: new Date().toISOString(),
          source: "yahoo",
        },
      });
    } catch (error) {
      return rail();
    }
  }

  const klineMatch = path.match(/\/api\/v1\/stocks\/(\d+)\/kline$/);
  if (klineMatch) {
    const symbol = klineMatch[1];
    const startDate = url.searchParams.get("start_date") || "";
    const endDate = url.searchParams.get("end_date") || "";

    try {
      const response = await fetch(
        "https://push2.eastmoney.com/api/qt/stock/kline/get?secid=" + secid(symbol) + "&klt=101&fqt=1&beg=" + startDate.replace(/-/g, "") + "&end=" + (endDate ? endDate.replace(/-/g, "") : ""),
        { headers: { "User-Agent": "Mozilla/5.0" } },
      );
      const payload = await response.json();
      const raw = (payload.data || {}).klines || [];
      const result = raw.map((row) => {
        const parts = row.split(",");
        return {
          trade_date: parts[0],
          open_price: parseFloat(parts[1]),
          close_price: parseFloat(parts[2]),
          high_price: parseFloat(parts[3]),
          low_price: parseFloat(parts[4]),
          volume: parseInt(parts[5], 10),
          amount: parseFloat(parts[6]),
        };
      }).filter((row) => row.trade_date && Number.isFinite(row.close_price));
      if (result.length > 0) return apiResponse({ code: 0, message: "success", data: result });
    } catch (error) {
      console.error("eastmoney kline failed", error);
    }

    try {
      let range = "3mo";
      if (startDate) {
        const days = (new Date(endDate || new Date()) - new Date(startDate)) / 86400000;
        range = days <= 31 ? "1mo" : days <= 93 ? "3mo" : days <= 183 ? "6mo" : "1y";
      }
      const response = await fetch("https://query1.finance.yahoo.com/v8/finance/chart/" + yahooSym(symbol) + "?interval=1d&range=" + range, {
        headers: { "User-Agent": "Mozilla/5.0" },
      });
      const payload = await response.json();
      const result = payload.chart.result[0];
      const timestamps = result.timestamp || [];
      const quote = result.indicators.quote[0];
      const rows = [];
      for (let i = 0; i < timestamps.length; i += 1) {
        const date = new Date(timestamps[i] * 1000);
        const tradeDate = date.getFullYear() + "-" + String(date.getMonth() + 1).padStart(2, "0") + "-" + String(date.getDate()).padStart(2, "0");
        if (quote.open[i] && quote.close[i]) {
          rows.push({
            trade_date: tradeDate,
            open_price: quote.open[i],
            high_price: quote.high[i],
            low_price: quote.low[i],
            close_price: quote.close[i],
            volume: quote.volume[i] || 0,
            amount: (quote.volume[i] || 0) * quote.open[i],
          });
        }
      }
      if (rows.length > 0) return apiResponse({ code: 0, message: "success", data: rows });
    } catch (error) {
      console.error("yahoo kline failed", error);
    }

    return rail();
  }

  if (path.startsWith("/api/v1/stocks/") && path.endsWith("/financials")) {
    const symbol = path.split("/")[4];
    const tsToken = context.env.TUSHARE_TOKEN || "";

    if (tsToken) {
      try {
        const finResp = await fetch("https://api.tushare.pro", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            token: tsToken,
            api_name: "fina_indicator",
            params: { ts_code: symbol.startsWith("6") ? symbol + ".SH" : symbol + ".SZ", limit: 1 },
            fields: "roe,gross_margin,net_margin,revenue,net_profit,debt_to_assets",
          }),
        });
        const finData = await finResp.json();
        const finRow = ((finData.data || {}).items || [])[0] || [];
        if (finRow.length > 1 && typeof finRow[1] === "number") {
          return apiResponse({
            code: 0,
            message: "success",
            data: {
              market_cap: null,
              pe_ttm: null,
              pb: null,
              peg: null,
              dividend_yield: null,
              roe: finRow[1] != null ? Number((finRow[1] * 100).toFixed(2)) + "%" : null,
              gross_margin: finRow[2] != null ? Number((finRow[2] * 100).toFixed(2)) + "%" : null,
              net_margin: finRow[3] != null ? Number((finRow[3] * 100).toFixed(2)) + "%" : null,
              revenue: finRow[4] != null ? Number(Number(finRow[4]).toFixed(2)) : null,
              net_profit: finRow[5] != null ? Number(Number(finRow[5]).toFixed(2)) : null,
              debt_ratio: finRow[6] != null ? Number((finRow[6] * 100).toFixed(2)) + "%" : null,
              revenue_growth: null,
              deducted_net_profit: null,
              current_ratio: null,
              quick_ratio: null,
              operating_cashflow: null,
              cash_equiv: null,
              total_debt: null,
              inventory_turnover: null,
              ar_turnover: null,
              goodwill: null,
              pledge_ratio: null,
              major_reduction: null,
              auditor_change: null,
              report_date: null,
            },
          });
        }
      } catch (error) {
        console.error("tushare financials failed", error);
      }
    }

    try {
      const ySymbol = symbol.startsWith("6") ? symbol + ".SS" : symbol + ".SZ";
      const response = await fetch("https://query1.finance.yahoo.com/v10/finance/quoteSummary/" + ySymbol + "?modules=price,defaultKeyStatistics,financialData,calendarEvents", {
        headers: { "User-Agent": "Mozilla/5.0" },
      });
      const payload = await response.json();
      const quoteSummary = ((payload.quoteSummary || {}).result || [{}])[0] || {};
      const keyStats = quoteSummary.defaultKeyStatistics || {};
      const financialData = quoteSummary.financialData || {};
      const calendar = quoteSummary.calendarEvents || {};
      const raw = (value) => value && value.raw ? value.raw : null;
      return apiResponse({
        code: 0,
        message: "success",
        data: {
          pe_ttm: raw(keyStats.trailingPE),
          pb: raw(keyStats.priceToBook),
          market_cap: raw(quoteSummary.price?.marketCap),
          peg: raw(keyStats.pegRatio),
          dividend_yield: raw(keyStats.dividendYield) ? (raw(keyStats.dividendYield) * 100).toFixed(2) : null,
          roe: raw(keyStats.returnOnEquity) ? (raw(keyStats.returnOnEquity) * 100).toFixed(2) : null,
          gross_margin: raw(financialData.grossMargins) ? (raw(financialData.grossMargins) * 100).toFixed(2) : null,
          net_margin: raw(financialData.profitMargins) ? (raw(financialData.profitMargins) * 100).toFixed(2) : null,
          revenue: raw(financialData.totalRevenue),
          revenue_growth: raw(financialData.revenueGrowth) ? (raw(financialData.revenueGrowth) * 100).toFixed(2) : null,
          net_profit: raw(financialData.netIncome) || null,
          deducted_net_profit: null,
          current_ratio: raw(financialData.currentRatio),
          quick_ratio: raw(financialData.quickRatio),
          debt_ratio: raw(keyStats.debtToEquity) ? raw(keyStats.debtToEquity).toFixed(2) : null,
          operating_cashflow: raw(financialData.operatingCashflow),
          cash_equiv: null,
          total_debt: null,
          inventory_turnover: null,
          ar_turnover: null,
          goodwill: null,
          pledge_ratio: null,
          major_reduction: null,
          auditor_change: null,
          report_date: (calendar.earnings || {}).earningsDate ? (calendar.earnings.earningsDate[0] || {}).fmt || null : null,
        },
      });
    } catch (error) {
      console.error("yahoo financials failed", error);
    }

    return apiResponse({
      code: 0,
      message: "success",
      data: {
        symbol,
        name: symbol,
        net_profit: null,
        deducted_net_profit: null,
        gross_margin: null,
        net_margin: null,
        roe: null,
        revenue: null,
        revenue_growth: null,
        debt_ratio: null,
        current_ratio: null,
        quick_ratio: null,
        cash: null,
        interest_debt: null,
        operating_cashflow: null,
        pe_ttm: null,
        pb: null,
        peg: null,
        dividend_yield: null,
        inventory_days: null,
        ar_days: null,
        goodwill: null,
        pledge_ratio: null,
        major_reduction: null,
        auditor_change: null,
        market_cap: null,
        total_shares: null,
        report_date: null,
      },
    });
  }

  const scoreMatch = path.startsWith("/api/v1/stocks/") && path.endsWith("/score") ? [null, path.split("/")[4]] : null;
  if (scoreMatch) {
    const symbol = scoreMatch[1] || "";
    const ySymbol = symbol.match(/^[569]/) ? symbol + ".SS" : symbol + ".SZ";
    try {
      const response = await fetch("https://query1.finance.yahoo.com/v8/finance/chart/" + ySymbol + "?range=6mo&interval=1d", {
        headers: { "User-Agent": "Mozilla/5.0" },
      });
      if (response.ok) {
        const payload = await response.json();
        const chart = ((payload.chart || {}).result || [{}])[0] || {};
        const quote = ((chart.indicators || {}).quote || [{}])[0] || {};
        const closes = (quote.close || []).filter((value) => value !== null);
        if (closes.length > 5) {
          let technical = 8;
          const last = closes[closes.length - 1];
          const prev5 = closes[closes.length - 5];
          const prev20 = closes[Math.max(0, closes.length - 20)];
          if (last && prev5) {
            const pct = ((last - prev5) / prev5) * 100;
            if (pct > 3) technical += 5;
            else if (pct > 0) technical += 3;
            else if (pct > -3) technical += 2;
          }
          if (last && prev20) {
            const pct = ((last - prev20) / prev20) * 100;
            if (pct > 5) technical += 4;
            else if (pct > 2) technical += 3;
          }
          if (closes.length > 10) {
            const avg5 = closes.slice(-5).reduce((sum, value) => sum + value, 0) / 5;
            const avg10 = closes.slice(-10).reduce((sum, value) => sum + value, 0) / 10;
            if (avg5 > avg10) technical += 3;
          }
          technical = Math.min(technical, 20);
          const total = null;
          const strengths = [];
          const risks = [];
          if (technical >= 15) strengths.push("\u6280\u672f\u8d8b\u52bf\u8f83\u5f3a");
          else if (technical <= 8) risks.push("\u6280\u672f\u8d8b\u52bf\u504f\u5f31");
          risks.push("\u8d22\u52a1\u548c\u98ce\u9669\u7ef4\u5ea6\u4f7f\u7528\u7ebf\u4e0a\u515c\u5e95\u5206");
          return apiResponse({
            code: 0,
            message: "success",
            data: {
              symbol,
              name: symbol,
              score_date: null,
              fundamental_score: null,
              solvency_score: null,
              technical_score: null,
              valuation_score: null,
              risk_score: null,
              total_score: null,
              rating: "--",
              strengths: [],
              risks: ["技术数据已获取，但财务和风险数据未能获取，无法进行完整评分"],
              suggestion: "当前股票由于财务数据未能获取，仅能根据技术指标进行部分分析，无法进行完整评分。",
              data_insufficient: true,
            },
          })
        }
      }
    } catch (error) {
      console.error("score calculation failed", error);
    }

    return apiResponse({
      code: 0,
      message: "success",
      data: {
        symbol,
        name: symbol,
        fundamental_score: null,
        solvency_score: null,
        technical_score: null,
        valuation_score: null,
        risk_score: null,
        total_score: null,
        data_insufficient: true,
        rating: "D",
        strengths: [],
        risks: ["\u7814\u7a76\u8bc4\u5206\u6570\u636e\u6e90\u6682\u4e0d\u53ef\u7528"],
        suggestion: "\u6570\u636e\u4e0d\u8db3\uff0c\u5efa\u8bae\u5148\u89c2\u671b\u5e76\u7b49\u5f85\u8d22\u52a1\u548c\u98ce\u9669\u6570\u636e\u5237\u65b0\u3002",
        raw_breakdown: {
          weights: { fundamental: 30, solvency: 20, technical: 20, valuation: 15, risk: 15 },
          fallback: true,
        },
      },
    });
  }

  return rail();
}
