// === STOCK SEARCH ===
const SEARCH_PATH = /\/api\/v1\/stocks\/search/;

async function handleSearch(kw, market) {
  if (!kw) return null;
  // Try East Money API for full stock search
  try {
    const r = await fetch("https://searchadapter.eastmoney.com/api/suggest/get_SearchSuggestList?input="+encodeURIComponent(kw)+"&type=14&token=D43BF722C8E33BDC906FB84D85E326E8", {headers:{"User-Agent":"Mozilla/5.0"}});
    const j = await r.json();
    if (j && j.Data && Array.isArray(j.Data)) {
      var results = [];
      for (var i=0;i<j.Data.length;i++) {
        var d = j.Data[i];
        if (d.Code && d.Name) {
          var sym = String(d.Code).padStart(6,"0");
          var exch = d.Code.startsWith("6")||d.Code.startsWith("9") ? "SSE" : "SZSE";
          results.push({symbol:sym, name:d.Name, market:"A", exchange:exch, industry:null});
        }
      }
      if (results.length > 0) return results;
    }
  } catch(e) {}
  // Fallback to local stock list
  var stocks = [
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
  var upper = kw.toUpperCase();
  var results = stocks.filter(function(s) { return s.s.indexOf(upper)>=0 || s.n.indexOf(kw)>=0; });
  return results.slice(0, 20);
}

function secid(s) { return s.startsWith("6")||s.startsWith("9") ? "1."+s : "0."+s; }
function yahooSym(s) { return s.startsWith("6") ? s+".SS" : s+".SZ"; }
function emResp(data) { return new Response(JSON.stringify(data), {headers:{"Content-Type":"application/json"}}); }
function railFetch(url,method,headers,body) { return fetch("https://web-production-74b0a.up.railway.app"+url.pathname+url.search, {method:method, headers:headers, body:body}); }

export async function onRequest(context) {
  const url = new URL(context.request.url);
  // Non-API requests: try ASSETS, fallback to index.html for SPA
  if (!url.pathname.startsWith('/api/')) {
    const resp = await context.env.ASSETS.fetch(context.request).catch(() => null);
    if (resp && resp.status !== 404) return resp;
    const idxUrl = new URL(context.request.url);
    idxUrl.pathname = '/index.html';
    return context.env.ASSETS.fetch(new Request(idxUrl)).catch(() => new Response('Not Found', {status: 404}));
  }

  const path = url.pathname;
  const method = context.request.method;
  const hdrs = context.request.headers;
  const body = context.request.body;
  const rail = function() { return railFetch(url,method,hdrs,body); };

  // === STOCK SEARCH: East Money API + local fallback ===
  if (SEARCH_PATH.test(path)) {
    const kw = url.searchParams.get("keyword") || "";
    const market = url.searchParams.get("market") || "A";
    const results = await handleSearch(kw, market);
    if (results && results.length > 0) {
      return emResp({code:0,message:"success",data:results});
    }
    const r = await rail();
    if (r.ok) return r;
    return emResp({code:0,message:"success",data:results || []});
  }

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
    // Yahoo Fallback
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
    // Yahoo Fallback
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

  // === FINANCIALS: Tushare API (if token configured) + Yahoo Finance fallback ===
  if (url.pathname.startsWith("/api/v1/stocks/") && url.pathname.endsWith("/financials")) {
    const sym = url.pathname.split("/")[4];
    const tsToken = context.env.TUSHARE_TOKEN || "";

    if (tsToken) {
      try {
        const finResp = await fetch("https://api.tushare.pro", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({"token": tsToken, "api_name": "fina_indicator", "params": {"ts_code": sym.startsWith("6") ? sym+".SH" : sym+".SZ", "limit": 1}, "fields": "roe,gross_margin,net_margin,revenue,net_profit,debt_to_assets"})
        });
        const finData = await finResp.json();
        var fin = (finData.data||{}).items||[];
        var finRow = fin.length > 0 ? fin[0] : [];
        if (finRow && finRow.length > 1 && typeof finRow[1] === "number") {
          return emResp({code:0,message:"success",data:{
            market_cap: null, pe_ttm: null, pb: null, peg: null, dividend_yield: null,
            roe: finRow[1] != null ? Number(Number(finRow[1]*100).toFixed(2)) + "%" : null,
            gross_margin: finRow[2] != null ? Number(Number(finRow[2]*100).toFixed(2)) + "%" : null,
            net_margin: finRow[3] != null ? Number(Number(finRow[3]*100).toFixed(2)) + "%" : null,
            revenue: finRow[4] != null ? Number(Number(finRow[4]).toFixed(2)) : null,
            net_profit: finRow[5] != null ? Number(Number(finRow[5]).toFixed(2)) : null,
            debt_ratio: finRow[6] != null ? Number(Number(finRow[6]*100).toFixed(2)) + "%" : null,
            revenue_growth: null, deducted_net_profit: null,
            current_ratio: null, quick_ratio: null, operating_cashflow: null,
            cash_equiv: null, total_debt: null,
            inventory_turnover: null, ar_turnover: null, goodwill: null,
            pledge_ratio: null, major_reduction: null, auditor_change: null,
            report_date: null
          }});
        }
      } catch(e) {}
    }

    // Fallback to Yahoo Finance for financials
    try {
      var ySym2 = sym.startsWith("6") ? sym+".SS" : sym+".SZ";
      const r = await fetch("https://query1.finance.yahoo.com/v10/finance/quoteSummary/"+ySym2+"?modules=price,defaultKeyStatistics,financialData,calendarEvents", {headers:{"User-Agent":"Mozilla/5.0"}});
      const d = await r.json();
      const q = ((d.quoteSummary||{}).result||[{}])[0]||{};
      const ks = q.defaultKeyStatistics||{}, fd = q.financialData||{}, ce = q.calendarEvents||{};
      const raw = (v) => v&&v.raw ? v.raw : null;
      return emResp({code:0,message:"success",data:{
        pe_ttm: raw(ks.trailingPE), pb: raw(ks.priceToBook),
        market_cap: raw(q.price?.marketCap), peg: raw(ks.pegRatio),
        dividend_yield: raw(ks.dividendYield) ? (raw(ks.dividendYield)*100).toFixed(2) : null,
        roe: raw(ks.returnOnEquity) ? (raw(ks.returnOnEquity)*100).toFixed(2) : null,
        gross_margin: raw(fd.grossMargins) ? (raw(fd.grossMargins)*100).toFixed(2) : null,
        net_margin: raw(fd.profitMargins) ? (raw(fd.profitMargins)*100).toFixed(2) : null,
        revenue: raw(fd.totalRevenue), revenue_growth: raw(fd.revenueGrowth) ? (raw(fd.revenueGrowth)*100).toFixed(2) : null,
        net_profit: raw(fd.netIncome) || null, deducted_net_profit: null,
        current_ratio: raw(fd.currentRatio), quick_ratio: raw(fd.quickRatio),
        debt_ratio: raw(ks.debtToEquity) ? raw(ks.debtToEquity).toFixed(2) : null,
        operating_cashflow: raw(fd.operatingCashflow),
        cash_equiv: null, total_debt: null,
        inventory_turnover: null, ar_turnover: null, goodwill: null,
        pledge_ratio: null, major_reduction: null, auditor_change: null,
        report_date: (ce.earnings||{}).earningsDate ? (ce.earnings.earningsDate[0]||{}).fmt||null : null
      }});
    } catch(e) {}
    return rail();
  }

  // === SCORE: computed from Yahoo Finance data ===
  const scoreMatch = url.pathname.startsWith('/api/v1/stocks/') && url.pathname.endsWith('/score') ? [null, url.pathname.split('/')[4]] : null;
  if (scoreMatch) {
    const sym = scoreMatch[1] || "", ySym = sym.match(/^[569]/) ? sym+".SS" : sym+".SZ";
    try {
      const r = await fetch("https://query1.finance.yahoo.com/v8/finance/chart/"+ySym+"?range=6mo&interval=1d", {headers:{"User-Agent":"Mozilla/5.0"}});
      if (r.ok) {
        const d = await r.json(), q = ((d.chart||{}).result||[{}])[0]||{}, c = ((q.indicators||{}).quote||[{}])[0]||{}, cls = (c.close||[]).filter(x=>x!==null);
        if(cls.length>5){let t=15,v=10,f=12,al=3,se=10,l=cls[cls.length-1],p5=cls[cls.length-5],p20=cls[Math.max(0,cls.length-20)];
          if(l&&p5){let p=(l-p5)/p5*100;if(p>3)t+=8;else if(p>0)t+=5;else if(p>-3)t+=3}
          if(l&&p20){let p=(l-p20)/p20*100;if(p>5){se+=5;t+=7}else if(p>2){se+=3;t+=5}}
          if(cls.length>10){let a5=cls.slice(-5).reduce((a,b)=>a+b,0)/5,a10=cls.slice(-10).reduce((a,b)=>a+b,0)/10;if(a5>a10){t+=5;v+=5}}
          let tot=Math.min(t+v+f+al+se,100),str=[],risk=[];
          if(t>=22)str.push("技术趋势健康");else if(t<=12)risk.push("技术面偏弱");
          if(se>=15)str.push("短期走势强劲");else if(se<=8)risk.push("短期走势偏弱");
          return emResp({code:0,message:"success",data:{symbol:sym,name:sym,total_score:tot,tech_score:Math.min(t,30),volume_score:Math.min(v,20),fundamental_score:Math.min(f,25),valuation_score:Math.min(al,5),sentiment_score:Math.min(se,20),summary:"综合评分 "+tot+"/100",strengths:str,risks:risk,suggestion:tot>=80?"长期配置价值较高":tot>=65?"技术面转好，可分批建仓":tot>=50?"建议观望":"建议回避"}});
        }
      }
    } catch(e) {}
    return emResp({code:0,message:"success",data:{symbol:sym,name:sym,total_score:50,tech_score:15,volume_score:10,fundamental_score:12,valuation_score:3,sentiment_score:10,summary:"综合评分 50/100",strengths:[],risks:["数据源不可用"],suggestion:"建议观望"}});
  }

  // === DEFAULT: proxy to Railway ===
  return rail();
}
