// Stock list for search (popular A-shares)
const STOCKS = [
  {s:'000001',n:'平安银行',e:'SZSE'},{s:'000002',n:'万科A',e:'SZSE'},{s:'000333',n:'美的集团',e:'SZSE'},
  {s:'000651',n:'格力电器',e:'SZSE'},{s:'000725',n:'京东方A',e:'SZSE'},{s:'000858',n:'五粮液',e:'SZSE'},
  {s:'002007',n:'华兰生物',e:'SZSE'},{s:'002230',n:'科大讯飞',e:'SZSE'},{s:'002236',n:'大华股份',e:'SZSE'},
  {s:'002304',n:'洋河股份',e:'SZSE'},{s:'002352',n:'顺丰控股',e:'SZSE'},{s:'002371',n:'北方华创',e:'SZSE'},
  {s:'002415',n:'海康威视',e:'SZSE'},{s:'002459',n:'晶澳科技',e:'SZSE'},{s:'002475',n:'立讯精密',e:'SZSE'},
  {s:'002594',n:'比亚迪',e:'SZSE'},{s:'002714',n:'牧原股份',e:'SZSE'},{s:'002812',n:'恩捷股份',e:'SZSE'},
  {s:'300014',n:'亿纬锂能',e:'SZSE'},{s:'300015',n:'爱尔眼科',e:'SZSE'},{s:'300059',n:'东方财富',e:'SZSE'},
  {s:'300122',n:'智飞生物',e:'SZSE'},{s:'300124',n:'汇川技术',e:'SZSE'},{s:'300274',n:'阳光电源',e:'SZSE'},
  {s:'300308',n:'中际旭创',e:'SZSE'},{s:'300413',n:'芒果超媒',e:'SZSE'},{s:'300433',n:'蓝思科技',e:'SZSE'},
  {s:'300450',n:'先导智能',e:'SZSE'},{s:'300498',n:'温氏股份',e:'SZSE'},{s:'300502',n:'新易盛',e:'SZSE'},
  {s:'300676',n:'华大基因',e:'SZSE'},{s:'300750',n:'宁德时代',e:'SZSE'},{s:'300759',n:'康龙化成',e:'SZSE'},
  {s:'300760',n:'迈瑞医疗',e:'SZSE'},{s:'300782',n:'卓胜微',e:'SZSE'},{s:'600036',n:'招商银行',e:'SSE'},
  {s:'600276',n:'恒瑞医药',e:'SSE'},{s:'600309',n:'万华化学',e:'SSE'},{s:'600519',n:'贵州茅台',e:'SSE'},
  {s:'600585',n:'海螺水泥',e:'SSE'},{s:'600690',n:'海尔智家',e:'SSE'},{s:'600809',n:'山西汾酒',e:'SSE'},
  {s:'600887',n:'伊利股份',e:'SSE'},{s:'600900',n:'长江电力',e:'SSE'},{s:'600941',n:'中国移动',e:'SSE'},
  {s:'601012',n:'隆基绿能',e:'SSE'},{s:'601166',n:'兴业银行',e:'SSE'},{s:'601318',n:'中国平安',e:'SSE'},
  {s:'601328',n:'交通银行',e:'SSE'},{s:'601398',n:'工商银行',e:'SSE'},{s:'601628',n:'中国人寿',e:'SSE'},
  {s:'601728',n:'中国电信',e:'SSE'},{s:'601857',n:'中国石油',e:'SSE'},{s:'601899',n:'紫金矿业',e:'SSE'},
  {s:'601939',n:'建设银行',e:'SSE'},{s:'688981',n:'中芯国际',e:'SSE'},{s:'688041',n:'海光信息',e:'SSE'},
  {s:'688256',n:'寒武纪',e:'SSE'},{s:'688012',n:'中微公司',e:'SSE'},{s:'688111',n:'金山办公',e:'SSE'},
  {s:'002466',n:'天齐锂业',e:'SZSE'},{s:'002460',n:'赣锋锂业',e:'SZSE'},{s:'603259',n:'药明康德',e:'SSE'},
  {s:'601088',n:'中国神华',e:'SSE'},{s:'600028',n:'中国石化',e:'SSE'},{s:'000625',n:'长安汽车',e:'SZSE'},
  {s:'600104',n:'上汽集团',e:'SSE'},{s:'600745',n:'闻泰科技',e:'SSE'},{s:'601766',n:'中国中车',e:'SSE'},
];

export async function onRequest(context) {
  const url = new URL(context.request.url);
  const path = url.pathname;
  const search = url.search;
  const method = context.request.method;
  const railwayUrl = "https://web-production-74b0a.up.railway.app" + path + search;
  const proxyToRailway = function() { return fetch(railwayUrl, {method:method, headers:context.request.headers, body:context.request.body}); };

  // Quote: use Yahoo Finance (accessible everywhere)
  const qm = path.match(/\/api\/v1\/stocks\/(\d+)\/quote$/);
  if (qm) {
    try {
      const sym = qm[1];
      const yahooSym = sym.startsWith("6") ? sym + ".SS" : sym + ".SZ";
      const yh = await fetch("https://query1.finance.yahoo.com/v8/finance/chart/" + yahooSym + "?interval=1d&range=5d", {headers:{"User-Agent":"Mozilla/5.0"}});
      const yj = await yh.json();
      const r = yj.chart.result[0];
      const m = r.meta;
      const close = m.regularMarketPrice;
      const prevClose = m.chartPreviousClose;
      const change = close - prevClose;
      const pct = (change / prevClose) * 100;
      return new Response(JSON.stringify({code:0,message:"success",data:{symbol:sym,name:m.symbol||sym,market:"A",price:close,change:change,pct_change:pct,volume:m.regularMarketVolume||0,amount:0,timestamp:new Date().toISOString(),source:"yahoo"}}),{headers:{"Content-Type":"application/json"}});
    } catch(e) { return proxyToRailway(); }
  }


  // Kline: use Yahoo Finance
  const km = path.match(/\/api\/v1\/stocks\/(\d+)\/kline$/);
  if (km) {
    try {
      const sym = km[1];
      const yahooSym = sym.startsWith("6") ? sym + ".SS" : sym + ".SZ";
      var sd = url.searchParams.get("start_date") || "";
      var ed = url.searchParams.get("end_date") || "";
      var range = "3mo";
      if (sd) { var days = (new Date(ed||new Date()) - new Date(sd)) / 86400000; if (days <= 31) range="1mo"; else if (days <= 62) range="2mo"; else if (days <= 93) range="3mo"; else if (days <= 183) range="6mo"; else range="1y"; }
      var yh = await fetch("https://query1.finance.yahoo.com/v8/finance/chart/" + yahooSym + "?interval=1d&range=" + range, {headers:{"User-Agent":"Mozilla/5.0"}});
      var yj = await yh.json();
      var r = yj.chart.result[0];
      var timestamps = r.timestamp || [];
      var quotes = r.indicators.quote[0];
      var result = [];
      for (var i = 0; i < timestamps.length; i++) {
        var dt = new Date(timestamps[i] * 1000);
        var ds = dt.getFullYear() + "-" + String(dt.getMonth()+1).padStart(2,"0") + "-" + String(dt.getDate()).padStart(2,"0");
        var o = quotes.open[i], h = quotes.high[i], l = quotes.low[i], c = quotes.close[i], v = quotes.volume[i];
        if (o && c) {
          result.push({trade_date:ds, open_price:o, high_price:h, low_price:l, close_price:c, volume:v||0, amount:(v||0)*o});
        }
      }
      if (result.length > 0) return new Response(JSON.stringify({code:0,message:"success",data:result}),{headers:{"Content-Type":"application/json"}});
    } catch(e) {}
    return proxyToRailway();
  }
  // Search: filter from stock list
  if (path === "/api/v1/stocks/search") {
    try {
      const kw = (url.searchParams.get("keyword") || "").toLowerCase();
      const result = [];
      for (var i = 0; i < STOCKS.length; i++) {
        var s = STOCKS[i];
        if (s.s.toLowerCase().includes(kw) || s.n.toLowerCase().includes(kw)) {
          result.push({symbol:s.s,name:s.n,market:"A",exchange:s.e,industry:""});
          if (result.length >= 20) break;
        }
      }
      if (result.length > 0) return new Response(JSON.stringify({code:0,message:"success",data:result}),{headers:{"Content-Type":"application/json"}});
    } catch(e) {}
    return proxyToRailway();
  }

  return proxyToRailway();
}