import { apiClient, type ApiResponse } from './client';
/* Health */
export async function checkHealth(): Promise<ApiResponse<{ api: boolean; database: boolean; redis: boolean }>> {
  const { data } = await apiClient.get('/health');
  return data;
}
/* Auth */
export async function loginApi(usernameOrEmail: string, password: string): Promise<ApiResponse<{ access_token: string; refresh_token: string; token_type: string; expires_in: number }>> {
  const { data } = await apiClient.post('/auth/login', { username_or_email: usernameOrEmail, password });
  return data;
}
export async function registerApi(username: string, email: string, password: string, fullName?: string): Promise<ApiResponse<{ id: string; username: string; email: string; full_name: string | null; is_active: boolean; is_superuser: boolean; created_at: string; updated_at: string }>> {
  const { data } = await apiClient.post('/auth/register', { username, email, password, full_name: fullName });
  return data;
}
/* Stocks */
export async function searchStocks(keyword: string, market = 'A'): Promise<ApiResponse<Array<{ symbol: string; name: string; market: string; exchange: string; industry: string | null }>>> {
  const { data } = await apiClient.get('/stocks/search', { params: { keyword, market } });
  return data;
}
export async function getQuote(symbol: string, market = 'A'): Promise<ApiResponse<{ symbol: string; name: string; market: string; price: number; change: number; pct_change: number; volume: number; amount: number; timestamp: string; source: string }>> {
  const { data } = await apiClient.get(`/stocks/${symbol}/quote`, { params: { market } });
  return data;
}
export async function getKline(symbol: string, market = 'A', startDate?: string, endDate?: string, adjust = 'qfq'): Promise<ApiResponse<Array<{ trade_date: string; open_price: number; high_price: number; low_price: number; close_price: number; volume: number; amount: number }>>> {
  const { data } = await apiClient.get(`/stocks/${symbol}/kline`, { params: { market, start_date: startDate, end_date: endDate, adjust } });
  return data;
}
/* Analysis */
export async function getFinancials(symbol: string, market = 'A'): Promise<ApiResponse<any>> {
  const { data } = await apiClient.get('/stocks/' + symbol + '/financials', { params: { market } });
  return data;
}

export async function analyzeStock(symbol: string, market = 'A', lookbackDays = 120, model?: string, apiBaseUrl?: string, apiKey?: string): Promise<ApiResponse<{ symbol: string; market: string; provider: string; model: string; report_markdown: string; objective_data: Record<string, unknown>; technical_summary: Record<string, unknown>; risk_summary: Record<string, unknown>; data_timestamp: string }>> {
  const { data } = await apiClient.post('/analysis/stock', { symbol, market, lookback_days: lookbackDays, model: model || undefined, api_base_url: apiBaseUrl || undefined, api_key: apiKey || undefined });
  return data;
}

/* Scoring */
export interface StockScoreItem {
  symbol: string;
  name: string;
  total_score: number;
  tech_score: number;
  volume_score: number;
  fundamental_score: number;
  valuation_score: number;
  sentiment_score: number;
  summary: string;
  strengths: string[];
  risks: string[];
  suggestion: string;
}
export async function getStockScore(symbol: string, market = 'A'): Promise<ApiResponse<StockScoreItem>> {
  const { data } = await apiClient.get('/stocks/' + symbol + '/score', { params: { market } });
  return data;
}
