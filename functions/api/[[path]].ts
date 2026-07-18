const STOCKS = [
  { symbol: "000001", name: "\u5e73\u5b89\u94f6\u884c", exchange: "SZSE" },
  { symbol: "000002", name: "\u4e07\u79d1A", exchange: "SZSE" },
  { symbol: "000333", name: "\u7f8e\u7684\u96c6\u56e2", exchange: "SZSE" },
  { symbol: "000651", name: "\u683c\u529b\u7535\u5668", exchange: "SZSE" },
  { symbol: "000725", name: "\u4eac\u4e1c\u65b9A", exchange: "SZSE" },
  { symbol: "000858", name: "\u4e94\u7cae\u6db2", exchange: "SZSE" },
  { symbol: "002230", name: "\u79d1\u5927\u8baf\u98de", exchange: "SZSE" },
  { symbol: "002415", name: "\u6d77\u5eb7\u5a01\u89c6", exchange: "SZSE" },
  { symbol: "002475", name: "\u7acb\u8baf\u7cbe\u5bc6", exchange: "SZSE" },
  { symbol: "002594", name: "\u6bd4\u4e9a\u8fea", exchange: "SZSE" },
  { symbol: "300014", name: "\u4ebf\u7eac\u9502\u80fd", exchange: "SZSE" },
  { symbol: "300015", name: "\u7231\u5c14\u773c\u79d1", exchange: "SZSE" },
  { symbol: "300059", name: "\u4e1c\u65b9\u8d22\u5bcc", exchange: "SZSE" },
  { symbol: "300124", name: "\u6c47\u5ddd\u6280\u672f", exchange: "SZSE" },
  { symbol: "300274", name: "\u9633\u5149\u7535\u6e90", exchange: "SZSE" },
  { symbol: "300308", name: "\u4e2d\u9645\u65ed\u521b", exchange: "SZSE" },
  { symbol: "300502", name: "\u65b0\u6613\u76db", exchange: "SZSE" },
  { symbol: "300750", name: "\u5b81\u5fb7\u65f6\u4ee3", exchange: "SZSE" },
  { symbol: "300760", name: "\u8fc8\u745e\u533b\u7597", exchange: "SZSE" },
  { symbol: "600000", name: "\u6d66\u53d1\u94f6\u884c", exchange: "SSE" },
  { symbol: "600009", name: "\u4e0a\u6d77\u673a\u573a", exchange: "SSE" },
  { symbol: "600016", name: "\u6c11\u751f\u94f6\u884c", exchange: "SSE" },
  { symbol: "600030", name: "\u4e2d\u4fe1\u8bc1\u5238", exchange: "SSE" },
  { symbol: "600036", name: "\u62db\u5546\u94f6\u884c", exchange: "SSE" },
  { symbol: "600276", name: "\u6052\u745e\u533b\u836f", exchange: "SSE" },
  { symbol: "600309", name: "\u4e07\u534e\u5316\u5b66", exchange: "SSE" },
  { symbol: "600519", name: "\u8d35\u5dde\u8305\u53f0", exchange: "SSE" },
  { symbol: "600690", name: "\u6d77\u5c14\u667a\u5bb6", exchange: "SSE" },
  { symbol: "600745", name: "\u95fb\u6cf0\u79d1\u6280", exchange: "SSE" },
  { symbol: "600809", name: "\u5c71\u897f\u6c7e\u9152", exchange: "SSE" },
  { symbol: "600887", name: "\u4f0a\u5229\u80a1\u4efd", exchange: "SSE" },
  { symbol: "600900", name: "\u957f\u6c5f\u7535\u529b", exchange: "SSE" },
  { symbol: "600941", name: "\u4e2d\u56fd\u79fb\u52a8", exchange: "SSE" },
  { symbol: "601088", name: "\u4e2d\u56fd\u795e\u534e", exchange: "SSE" },
  { symbol: "601166", name: "\u5174\u4e1a\u94f6\u884c", exchange: "SSE" },
  { symbol: "601318", name: "\u4e2d\u56fd\u5e73\u5b89", exchange: "SSE" },
  { symbol: "601398", name: "\u5de5\u5546\u94f6\u884c", exchange: "SSE" },
  { symbol: "601766", name: "\u4e2d\u56fd\u4e2d\u8f66", exchange: "SSE" },
  { symbol: "601857", name: "\u4e2d\u56fd\u77f3\u6cb9", exchange: "SSE" },
  { symbol: "601899", name: "\u7d2b\u91d1\u77ff\u4e1a", exchange: "SSE" },
  { symbol: "603259", name: "\u836f\u660e\u5eb7\u5fb7", exchange: "SSE" },
  { symbol: "688981", name: "\u4e2d\u82af\u56fd\u9645", exchange: "SSE" },
];

function jsonResponse(data) {
  return new Response(JSON.stringify(data), {
    headers: { "Content-Type": "application/json; charset=utf-8" },
  });
}

function normalizeStock(item) {
  return {
    symbol: item.symbol || item.s || "",
    name: item.name || item.n || "",
    market: item.market || "A",
    exchange: item.exchange || item.e || "SZSE",
    industry: item.industry || null,
  };
}

function searchLocalStocks(keyword) {
  const kw = keyword.trim();
  const upper = kw.toUpperCase();
  if (!kw) return [];
  return STOCKS.filter((stock) => {
    return stock.symbol.includes(upper) || stock.name.includes(kw);
  }).slice(0, 20).map(normalizeStock);
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

async function handleSearch(url) {
  const keyword = url.searchParams.get("keyword") || "";
  const localResults = searchLocalStocks(keyword);
  if (localResults.length > 0) {
    return jsonResponse({ code: 0, message: "success", data: localResults });
  }
  try {
    const remoteResults = await searchEastMoney(keyword);
    if (remoteResults.length > 0) {
      return jsonResponse({ code: 0, message: "success", data: remoteResults });
    }
  } catch (error) {
    console.error("stock search provider failed", error);
  }
  return null;
}

export async function onRequest(context) {
  const url = new URL(context.request.url);
  if (url.pathname.startsWith('/api/')) {
    if (url.pathname === "/api/v1/stocks/search") {
      const response = await handleSearch(url);
      if (response) return response;
    }
    const target = 'https://alphaquant-ai-production.up.railway.app' + url.pathname + url.search;
    return fetch(target, {method: context.request.method, headers: context.request.headers, body: context.request.body});
  }
  try { const r = await context.env.ASSETS.fetch(context.request); if (r.status !== 404) return r; } catch(e) {}
  const idx = new URL(context.request.url); idx.pathname = '/index.html';
  return context.env.ASSETS.fetch(new Request(idx));
}
