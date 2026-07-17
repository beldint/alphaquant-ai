export async function onRequest(context) {
  const url = new URL(context.request.url);
  const path = url.pathname;
  const search = url.search;

  // East Money proxy: Railway fetches data through Cloudflare to bypass network restrictions
  if (path.startsWith("/api/_em/")) {
    const emPath = path.replace("/api/_em/", "");
    const emUrl = "https://push2.eastmoney.com/" + emPath + search;
    const resp = await fetch(emUrl, { headers: { "User-Agent": "Mozilla/5.0" } });
    const text = await resp.text();
    return new Response(text, { headers: { "Content-Type": "application/json" } });
  }

  // Default: proxy to Railway backend
  const targetUrl = "https://web-production-74b0a.up.railway.app" + path + search;
  return fetch(targetUrl, {
    method: context.request.method,
    headers: context.request.headers,
    body: context.request.body,
  });
}