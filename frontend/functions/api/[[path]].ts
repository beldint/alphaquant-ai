export async function onRequest(context) {
  const url = new URL(context.request.url);
  const targetUrl = "https://web-production-74b0a.up.railway.app" + url.pathname + url.search;
  return fetch(targetUrl, {
    method: context.request.method,
    headers: context.request.headers,
    body: context.request.body,
  });
}
