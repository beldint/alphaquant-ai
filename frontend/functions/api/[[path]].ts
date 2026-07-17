export async function onRequest(context) {
  const url = new URL(context.request.url);
  const path = url.pathname;
  const search = url.search;
  const target = "https://web-production-74b0a.up.railway.app" + path + search;

  try {
    const qm = path.match(/\/api\/v1\/stocks\/([^\/]+)\/quote$/);
    if (qm) {
      const sym = qm[1];
      const sid = sym.startsWith("6") ? "1." + sym : "0." + sym;
      const er = await fetch("https://push2.eastmoney.com/api/qt/stock/get?secid=" + sid + "&fields=f43,f44,f45,f46,f47,f48,f169,f170,f57,f58", {headers: {"User-Agent": "Mozilla/5.0"}});
      const r = await er.json();
      const d = r.data || {};
      return new Response(JSON.stringify({code:0,message:"success",data:{symbol:sym,name:d.f58||sym,market:"A",price:(d.f43||0)/100,change:(d.f169||0)/100,pct_change:(d.f170||0)/100,volume:d.f47||0,amount:d.f48||0,timestamp:new Date().toISOString(),source:"eastmoney"}}),{headers:{"Content-Type":"application/json"}});
    }
  } catch(e) { return fetch(target, {method: context.request.method, headers: context.request.headers, body: context.request.body}); }

  try {
    if (path === "/api/v1/stocks/search") {
      const kw = (url.searchParams.get("keyword") || "").toLowerCase();
      const lr = await fetch("https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=300&po=1&np=1&fltt=2&invt=2&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23&fields=f12,f14", {headers: {"User-Agent": "Mozilla/5.0"}});
      const r = await lr.json();
      const items = (r.data||{}).diff||[]; const result = [];
      for(let i=0;i<items.length;i++){
        const c = String(items[i].f12||""); const n = String(items[i].f14||"");
        if(c.toLowerCase().includes(kw)||n.toLowerCase().includes(kw)){result.push({symbol:c,name:n});if(result.length>=50)break;}
      }
      return new Response(JSON.stringify({code:0,message:"success",data:result}),{headers:{"Content-Type":"application/json"}});
    }
  } catch(e) { return fetch(target, {method: context.request.method, headers: context.request.headers, body: context.request.body}); }

  return fetch(target, {method: context.request.method, headers: context.request.headers, body: context.request.body});
}