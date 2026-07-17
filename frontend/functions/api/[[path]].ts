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
  {s:'601166',n:'兴业银行',e:'SSE'},{s:'601318',n:'中国平安',e:'SSE'},{s:'601398',n:'工商银行',e:'SSE'},
  {s:'601857',n:'中国石油',e:'SSE'},{s:'601899',n:'紫金矿业',e:'SSE'},{s:'603259',n:'药明康德',e:'SSE'},
  {s:'601088',n:'中国神华',e:'SSE'},{s:'000625',n:'长安汽车',e:'SZSE'},{s:'600745',n:'闻泰科技',e:'SSE'},
  {s:'601766',n:'中国中车',e:'SSE'},{s:'002466',n:'天齐锂业',e:'SZSE'},{s:'002460',n:'赣锋锂业',e:'SZSE'},
];

function secid(s) { return s.startsWith("6")||s.startsWith("9") ? "1."+s : "0."+s; }
function yahooSym(s) { return s.startsWith("6") ? s+".SS" : s+".SZ"; }
function emResp(data) { return new Response(JSON.stringify(data), {headers:{"Content-Type":"application/json"}}); }
function railFetch(url,method,headers,body) { return fetch("https://web-production-74b0a.up.railway.app"+url.pathname+url.search, {method:method, headers:headers, body:body}); }

export async function onRequest(context) {
  const url = new URL(context.request.url);
  // Serve static assets directly - don't proxy to Railway
  if (!url.pathname.startsWith('/api/')) {
    return context.next();
  }
  const path = url.pathname;
  const method = context.request.method;
  const hdrs = context.request.headers;
  const body = context.request.body;
  const rail = function() { return railFetch(url,method,hdrs,body); };

  // === QUOTE: East Money (A-Share accurate) + Yahoo fallback ===
  const qm = path.match(/\/api\/v1\/stocks\/(\d+)\/quote$/);
  if (qm) {
    const sym = qm[1]; const sid = secid(sym);
    try {
      const r = await fetch("https://push2.eastmoney.com/api/qt/stock/get?secid="+sid+"&fields=f43,f44,f45,f46,f47,f48,f169,f170,f57,f58", {headers:{"User-Agent":"Mozilla/5.0"}});
      const j = await r.json(); const d = j.data || {};
      if (d.f43) {
        return emResp({code:0,message:"success",data:{symbol:sym,name:d.f58||sym,market:"A",
          price:d.f43/100,change:d.f169/100,pct_change:d.f170/100,volume:d.f47||0,amount:d.f48||0,
          timestamp:new Date().toISOString(),source:"eastmoney"}});
      }
    } catch(e) {}
    // Fallback: Yahoo Finance
    try {
      const r = await fetch("https://query1.finance.yahoo.com/v8/finance/chart/"+yahooSym(sym)+"?interval=1d&range=5d", {headers:{"User-Agent":"Mozilla/5.0"}});
      const j = await r.json(); const m = j.chart.result[0].meta;
      const close = m.regularMarketPrice, prev = m.chartPreviousClose;
      return emResp({code:0,message:"success",data:{symbol:sym,name:m.symbol||sym,market:"A",
        price:close,change:close-prev,pct_change:(close-prev)/prev*100,volume:m.regularMarketVolume||0,amount:0,
        timestamp:new Date().toISOString(),source:"yahoo"}});
    } catch(e) { return rail(); }
  }

  // === KLINE: East Money + Yahoo fallback ===
  const km = path.match(/\/api\/v1\/stocks\/(\d+)\/kline$/);
  if (km) {
    const sym = km[1]; const sid = secid(sym);
    var sd = url.searchParams.get("start_date")||""; var ed = url.searchParams.get("end_date")||"";
    try {
      var r = await fetch("https://push2.eastmoney.com/api/qt/stock/kline/get?secid="+sid+"&klt=101&fqt=1&beg="+sd.replace(/-/g,"")+"&end="+(ed?ed.replace(/-/g,""):""), {headers:{"User-Agent":"Mozilla/5.0"}});
      var j = await r.json(); var raw = (j.data||{}).klines||[];
      if (raw.length > 0) {
        var result = [];
        for (var i=0;i<raw.length;i++) {
          var p=raw[i].split(","); if(p.length<7) continue;
          result.push({trade_date:p[0],open_price:parseFloat(p[1]),close_price:parseFloat(p[2]),high_price:parseFloat(p[3]),low_price:parseFloat(p[4]),volume:parseInt(p[5]),amount:parseFloat(p[6])});
        }
        if (result.length > 0) return emResp({code:0,message:"success",data:result});
      }
    } catch(e) {}
    // Fallback: Yahoo Finance for kline
    try {
      var range="3mo";
      if(sd){var days=(new Date(ed||new Date())-new Date(sd))/86400000; range=days<=31?"1mo":days<=93?"3mo":days<=183?"6mo":"1y";}
      var r=await fetch("https://query1.finance.yahoo.com/v8/finance/chart/"+yahooSym(sym)+"?interval=1d&range="+range,{headers:{"User-Agent":"Mozilla/5.0"}});
      var j=await r.json(); var res=j.chart.result[0]; var ts=res.timestamp||[]; var q=res.indicators.quote[0]; var result=[];
      for(var i=0;i<ts.length;i++){
        var dt=new Date(ts[i]*1000); var ds=dt.getFullYear()+'-'+String(dt.getMonth()+1).padStart(2,'0')+'-'+String(dt.getDate()).padStart(2,'0');
        if(q.open[i]&&q.close[i]) result.push({trade_date:ds,open_price:q.open[i],high_price:q.high[i],low_price:q.low[i],close_price:q.close[i],volume:q.volume[i]||0,amount:(q.volume[i]||0)*q.open[i]});
      }
      if(result.length>0) return emResp({code:0,message:"success",data:result});
    } catch(e){}
    return rail();
  }

  // === SEARCH: embedded stock list ===
  if (path === "/api/v1/stocks/search") {
    try {
      const kw = (url.searchParams.get("keyword")||"").toLowerCase();
      const result = [];
      for (var i=0;i<STOCKS.length;i++) {
        var s=STOCKS[i]; if(s.s.toLowerCase().includes(kw)||s.n.toLowerCase().includes(kw)) {
          result.push({symbol:s.s,name:s.n,market:"A",exchange:s.e,industry:""});
          if(result.length>=20) break;
        }
      }
      if(result.length>0) return emResp({code:0,message:"success",data:result});
    } catch(e){}
    return rail();
  }

  return rail();
}