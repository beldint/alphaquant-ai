export async function onRequest(context) {
  const url = new URL(context.request.url);
  if (url.pathname.startsWith('/api/')) {
    const target = 'https://alphaquant-ai-production.up.railway.app' + url.pathname + url.search;
    return fetch(target, {method: context.request.method, headers: context.request.headers, body: context.request.body});
  }
  try { const r = await context.env.ASSETS.fetch(context.request); if (r.status !== 404) return r; } catch(e) {}
  const idx = new URL(context.request.url); idx.pathname = '/index.html';
  return context.env.ASSETS.fetch(new Request(idx));
}
