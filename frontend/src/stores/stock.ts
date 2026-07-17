import { defineStore } from 'pinia';
import { ref } from 'vue';
import { searchStocks, getQuote, getKline, analyzeStock } from '../api';
export interface StockIdentity { symbol: string; name: string; market: string; exchange: string; industry: string | null }
export interface Quote { symbol: string; name: string; market: string; price: number; change: number; pct_change: number; volume: number; amount: number; timestamp: string; source: string }
export interface KlineRecord { trade_date: string; open_price: number; high_price: number; low_price: number; close_price: number; volume: number; amount: number }
export interface AnalysisReport { symbol: string; market: string; provider: string; model: string; report_markdown: string; objective_data: Record<string, unknown>; technical_summary: Record<string, unknown>; risk_summary: Record<string, unknown>; data_timestamp: string }

const NUMERIC_FIELDS_KLINE = ["open_price","high_price","low_price","close_price","volume","amount"];
const NUMERIC_FIELDS_QUOTE = ["price","change","pct_change","volume","amount"];
function toNum(val) { if (typeof val === "string") { var n = Number(val); return isNaN(n) ? val : n; } return val; }
function convertNumericFields(obj, fields) { var r = Object.assign({}, obj); for (var i = 0; i < fields.length; i++) { var f = fields[i]; if (typeof r[f] === "string") r[f] = toNum(r[f]); } return r; }

export const useStockStore = defineStore('stock', () => {
  const searchResults = ref<StockIdentity[]>([]);
  const currentQuote = ref<Quote | null>(null);
  const klineData = ref<KlineRecord[]>([]);
  const analysisResult = ref<AnalysisReport | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);
  async function search(keyword: string, market = 'A') { loading.value = true; error.value = null; try { const res = await searchStocks(keyword, market); if (res.code === 0 && res.data) searchResults.value = res.data; } catch (e: any) { error.value = e.message; } finally { loading.value = false; } }
  async function fetchQuote(symbol: string, market = 'A') { loading.value = true; error.value = null; try { const res = await getQuote(symbol, market); if (res.code === 0 && res.data) currentQuote.value = convertNumericFields(res.data, NUMERIC_FIELDS_QUOTE); } catch (e: any) { error.value = e.message; } finally { loading.value = false; } }
  async function fetchKline(symbol: string, market = 'A', startDate?: string, endDate?: string) { loading.value = true; error.value = null; try { const res = await getKline(symbol, market, startDate, endDate); if (res.code === 0 && res.data) klineData.value = res.data.map(function(d) { return convertNumericFields(d, NUMERIC_FIELDS_KLINE); }); } catch (e: any) { error.value = e.message; } finally { loading.value = false; } }
  async function analyze(symbol: string, market = 'A', lookbackDays = 120) { loading.value = true; error.value = null; try { const res = await analyzeStock(symbol, market, lookbackDays); if (res.code === 0 && res.data) analysisResult.value = res.data; } catch (e: any) { error.value = e.message; } finally { loading.value = false; } }
  function clear() { searchResults.value = []; currentQuote.value = null; klineData.value = []; analysisResult.value = null; }
  return { searchResults, currentQuote, klineData, analysisResult, loading, error, search, fetchQuote, fetchKline, analyze, clear };
});
