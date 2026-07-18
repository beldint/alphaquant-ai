import { defineStore } from 'pinia';
import { ref } from 'vue';
import { searchStocks, getQuote, getKline, getStockScore, analyzeStock, type StockScoreItem } from '../api';

export interface StockIdentity {
  symbol: string;
  name: string;
  market: string;
  exchange: string;
  industry: string | null;
}

export interface Quote {
  symbol: string;
  name: string;
  market: string;
  price: number;
  change: number;
  pct_change: number;
  volume: number;
  amount: number;
  timestamp: string;
  source: string;
}

export interface KlineRecord {
  trade_date: string;
  open_price: number;
  high_price: number;
  low_price: number;
  close_price: number;
  volume: number;
  amount: number;
}

export interface AnalysisReport {
  symbol: string;
  market: string;
  provider: string;
  model: string;
  report_markdown: string;
  objective_data: Record<string, unknown>;
  technical_summary: Record<string, unknown>;
  risk_summary: Record<string, unknown>;
  data_timestamp: string;
}

type NumericFieldKey = keyof Pick<KlineRecord, 'open_price' | 'high_price' | 'low_price' | 'close_price' | 'volume' | 'amount'> | keyof Pick<Quote, 'price' | 'change' | 'pct_change' | 'volume' | 'amount'>;

const NUMERIC_FIELDS_KLINE: Array<keyof KlineRecord> = ['open_price', 'high_price', 'low_price', 'close_price', 'volume', 'amount'];
const NUMERIC_FIELDS_QUOTE: Array<keyof Quote> = ['price', 'change', 'pct_change', 'volume', 'amount'];

function toNumber(value: unknown): unknown {
  if (typeof value === 'string') {
    const parsed = Number(value);
    return Number.isNaN(parsed) ? value : parsed;
  }
  return value;
}

function convertNumericFields<T extends object>(obj: T, fields: Array<keyof T>): T {
  const result = { ...(obj as Record<string, unknown>) } as Record<string, unknown>;
  for (const field of fields) {
    if (typeof result[String(field)] === 'string') {
      result[String(field)] = toNumber(result[String(field)]);
    }
  }
  return result as T;
}

function normalizeStockIdentity(item: Record<string, unknown>): StockIdentity {
  const symbol = String(item.symbol || item.s || '');
  return {
    symbol,
    name: String(item.name || item.n || ''),
    market: String(item.market || 'A'),
    exchange: String(item.exchange || item.e || 'SZSE'),
    industry: (item.industry as string | null | undefined) ?? null,
  };
}

export const useStockStore = defineStore('stock', () => {
  const searchResults = ref<StockIdentity[]>([]);
  const currentQuote = ref<Quote | null>(null);
  const klineData = ref<KlineRecord[]>([]);
  const analysisResult = ref<AnalysisReport | null>(null);
  const stockScore = ref<StockScoreItem | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  async function search(keyword: string, market = 'A'): Promise<void> {
    loading.value = true;
    error.value = null;
    try {
      const res = await searchStocks(keyword, market);
      if (res.code === 0 && res.data) {
        searchResults.value = res.data.map((item) => normalizeStockIdentity(item as Record<string, unknown>));
      }
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : String(err);
    } finally {
      loading.value = false;
    }
  }

  async function fetchQuote(symbol: string, market = 'A'): Promise<void> {
    loading.value = true;
    error.value = null;
    try {
      const res = await getQuote(symbol, market);
      if (res.code === 0 && res.data) {
        currentQuote.value = convertNumericFields(res.data as Quote, NUMERIC_FIELDS_QUOTE);
      }
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : String(err);
    } finally {
      loading.value = false;
    }
  }

  async function fetchKline(symbol: string, market = 'A', startDate?: string, endDate?: string): Promise<void> {
    loading.value = true;
    error.value = null;
    try {
      const res = await getKline(symbol, market, startDate, endDate);
      if (res.code === 0 && res.data) {
        klineData.value = res.data.map((item) => convertNumericFields(item as KlineRecord, NUMERIC_FIELDS_KLINE));
      }
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : String(err);
    } finally {
      loading.value = false;
    }
  }

  async function fetchScore(symbol: string, market = 'A'): Promise<void> {
    loading.value = true;
    error.value = null;
    try {
      const res = await getStockScore(symbol, market);
      if (res.code === 0 && res.data) {
        stockScore.value = res.data;
      }
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : String(err);
    } finally {
      loading.value = false;
    }
  }

  async function analyze(
    symbol: string,
    market = 'A',
    lookbackDays = 120,
    model?: string,
    apiBaseUrl?: string,
    apiKey?: string,
    provider?: string,
  ): Promise<void> {
    loading.value = true;
    error.value = null;
    try {
      const res = await analyzeStock(symbol, market, lookbackDays, model, apiBaseUrl, apiKey, provider);
      if (res.code === 0 && res.data) {
        analysisResult.value = res.data;
      }
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : String(err);
    } finally {
      loading.value = false;
    }
  }

  function clear(): void {
    searchResults.value = [];
    currentQuote.value = null;
    klineData.value = [];
    analysisResult.value = null;
    stockScore.value = null;
    error.value = null;
  }

  return {
    searchResults,
    currentQuote,
    klineData,
    analysisResult,
    stockScore,
    loading,
    error,
    search,
    fetchScore,
    fetchQuote,
    fetchKline,
    analyze,
    clear,
  };
});
