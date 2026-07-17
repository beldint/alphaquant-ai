import { defineStore } from 'pinia';
import { ref, watch } from 'vue';
export interface PortfolioHolding { symbol: string; name: string; quantity: number; averageCost: number; marketValue: number; pnl: number }
export const usePortfolioStore = defineStore('portfolio', () => {
  const _saved = typeof localStorage !== 'undefined' ? localStorage.getItem('portfolio_holdings') : null;
  const holdings = ref<PortfolioHolding[]>(_saved ? JSON.parse(_saved) : []);
  watch(holdings, function(v) {
    if (typeof localStorage !== 'undefined') localStorage.setItem('portfolio_holdings', JSON.stringify(v));
  }, { deep: true });
  function addOrUpdate(h: PortfolioHolding) {
    var idx = holdings.value.findIndex(function(i) { return i.symbol === h.symbol; });
    if (idx >= 0) holdings.value[idx] = h;
    else holdings.value.push(h);
  }
  function remove(symbol: string) {
    holdings.value = holdings.value.filter(function(i) { return i.symbol !== symbol; });
  }
  return { holdings, addOrUpdate, remove };
});