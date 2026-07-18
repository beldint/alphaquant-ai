export function formatExchange(exchange: string | null | undefined): string {
  if (!exchange) return '-';
  if (exchange === 'SSE') return '上交所';
  if (exchange === 'SZSE') return '深交所';
  if (exchange === 'HKEX') return '港交所';
  if (exchange === 'NASDAQ') return '纳斯达克';
  if (exchange === 'NYSE') return '纽交所';
  if (exchange === 'AMEX') return '美交所';
  return exchange;
}

export function formatMarket(market: string | null | undefined): string {
  if (!market) return '-';
  if (market === 'A') return 'A股';
  if (market === 'HK') return '港股';
  if (market === 'US') return '美股';
  return market;
}
