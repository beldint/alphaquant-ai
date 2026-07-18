import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
export interface WatchlistItem { symbol: string; name: string; market: string; addedAt: string }
export const useWatchlistStore = defineStore('watchlist', () => {
  const items = ref<WatchlistItem[]>([]);
  function load() { try { const raw = localStorage.getItem('watchlist'); if (raw) items.value = JSON.parse(raw); } catch {} }
  function save() { localStorage.setItem('watchlist', JSON.stringify(items.value)); }
  const isInWatchlist = computed(() => (symbol: string) => items.value.some(i => i.symbol === symbol));
  function add(symbol: string, name: string, market = 'A') { if (!isInWatchlist.value(symbol)) { items.value.push({ symbol, name, market, addedAt: new Date().toISOString() }); save(); } }
  function remove(symbol: string) { items.value = items.value.filter(i => i.symbol !== symbol); save(); }
  function toggle(symbol: string, name: string, market = 'A'): boolean {
    if (isInWatchlist.value(symbol)) {
      remove(symbol);
      return false;
    }
    add(symbol, name, market);
    return true;
  }
  load();
  return { items, isInWatchlist, add, remove, toggle };
});
