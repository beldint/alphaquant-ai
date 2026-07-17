import { defineStore } from 'pinia';
import { ref } from 'vue';
export interface PortfolioHolding { symbol: string; name: string; quantity: number; averageCost: number; marketValue: number; pnl: number }
export const usePortfolioStore = defineStore('portfolio', () => {
  const holdings = ref<PortfolioHolding[]>([]);
  function addOrUpdate(h: PortfolioHolding) { const idx = holdings.value.findIndex(i => i.symbol === h.symbol); if (idx >= 0) holdings.value[idx] = h; else holdings.value.push(h); }
  function remove(symbol: string) { holdings.value = holdings.value.filter(i => i.symbol !== symbol); }
  return { holdings, addOrUpdate, remove };
});
