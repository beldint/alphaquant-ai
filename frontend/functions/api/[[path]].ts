export async function onRequest(context) {
  const url = new URL(context.request.url);
  const path = url.pathname;
  const search = url.search;
  const method = context.request.method;

  function secid(s) {
    return s.startsWith("6")||s.startsWith("9") ? "1."+s : s.startsWith("4")||s.startsWith("8") ? "2."+s : "0."+s;
  }

  function json(data, status) {
    return new Response(JSON.stringify(data), {
      status: status || 200,
      headers: {"Content-Type": "application/json"}
    });
  }

  try {
    var m = path.match(/^\/api\/v1\/stocks\/([^\/]+)\/quote$/);
    if (m && method === "GET") {
      var s = m[1], sid = secid(s);
      var em = await fetch("https://push2.eastmoney.com/api/qt/stock/get?secid="+sid+"&fields=f43,f44,f45,f46,f47,f48,f169,f170,f57,f58", {headers: {"User-Agent":"Mozilla/5.0"}});
      var raw = await em.json(), d = raw.data || {};
      return json({code:0, message:"success", data:{
        symbol:s, name:d.f58||s, market:"A",
        price:(d.f43||0)/100, change:(d.f169||0)/100, pct_change:(d.f170||0)/100,
        volume:d.f47||0, amount:d.f48||0,
        timestamp:new Date().toISOString(), source:"eastmoney"
      }});
    }

    if (path === "/api/v1/stocks/search" && method === "GET") {
      var kw = (url.searchParams.get("keyword") || "").toLowerCase();
      var em = await fetch("https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=300&po=1&np=1&fltt=2&invt=2&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23&fields=f12,f14", {headers:{"User-Agent":"Mozilla/5.0"}});
      var raw = await em.json();
      var items = (raw.data||{}).diff||[];
      var filtered = items.filter(function(i) {
        return String(i.f12||"").toLowerCase().indexOf(kw) >= 0 || String(i.f14||"").toLowerCase().indexOf(kw) >= 0;
      }).slice(0,50).map(function(i) {
        var code = String(i.f12||"");
        return {symbol:code, name:String(i.f14||""), market:"A", exchange:code.startsWith("6")?"SSE":"SZSE", industry:""};
      });
      return json({code:0, message:"success", data:filtered});
    }
  } catch(e) {}

  // Proxy to Railway for other requests
  var target = "https://web-production-74b0a.up.railway.app" + path + search;
  return fetch(target, {method: method, headers: context.request.headers, body: context.request.body});
}