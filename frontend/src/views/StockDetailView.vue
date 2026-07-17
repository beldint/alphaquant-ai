<template>
  <div>
    <div class="page-header flex-between">
      <div><h2>{{ symbol }} <span class="text-muted" style="font-weight:400;font-size:16px">{{ stockName }}</span></h2></div>
      <n-space>
        <n-button size="small" :type="isWatched ? 'warning' : 'primary'" ghost @click="toggleWatchlist">
          {{ isWatched ? '已自选' : '加自选' }}
        </n-button>
        <n-button size="small" type="success" ghost @click="goToAnalysis">AI分析</n-button>
        <n-button size="small" ghost @click="downloadReport">下载报告</n-button>
      </n-space>
    </div>
    <n-grid :cols="4" :x-gap="16" class="mb-24" v-if="quote">
      <n-grid-item><n-statistic label="最新价" :value="quote.price" :tabular-nums="true" /></n-grid-item>
      <n-grid-item><n-statistic label="涨跌额" :value="quote.change" :tabular-nums="true" :style="quote.change >= 0 ? 'color:var(--up-color)' : 'color:var(--down-color)'" /></n-grid-item>
      <n-grid-item><n-statistic label="涨跌幅" :value="quote.pct_change + '%'" :tabular-nums="true" :style="quote.pct_change >= 0 ? 'color:var(--up-color)' : 'color:var(--down-color)'" /></n-grid-item>
      <n-grid-item><n-statistic label="成交量" :value="formatVolume(quote.volume)" :tabular-nums="true" /></n-grid-item>
    </n-grid>
    <n-card size="small" class="mb-24">
      <n-tabs type="line" :value="klinePeriod" @update:value="(v) => switchPeriod(v)">
        <n-tab-pane name="1M" tab="近1月"><KLineChart :data="klineData" /></n-tab-pane>
        <n-tab-pane name="3M" tab="近3月"><KLineChart :data="klineData" /></n-tab-pane>
        <n-tab-pane name="6M" tab="近6月"><KLineChart :data="klineData" /></n-tab-pane>
      </n-tabs>
    </n-card>
    <TechnicalIndicators :data="klineData" title="技术指标" />
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useStockStore } from '../stores/stock';
import { useWatchlistStore } from '../stores/watchlist';
import KLineChart from '../components/KLineChart.vue';
import TechnicalIndicators from '../components/TechnicalIndicators.vue';
const route = useRoute();
const router = useRouter();
const stockStore = useStockStore();
const watchlistStore = useWatchlistStore();
const symbol = computed(() => route.params.symbol as string);
const stockName = ref('');
const quote = computed(() => stockStore.currentQuote);
const klineData = computed(() => stockStore.klineData);
const klinePeriod = ref('1M');
const isWatched = computed(() => watchlistStore.isInWatchlist(symbol.value));
function toggleWatchlist() { if (isWatched.value) watchlistStore.remove(symbol.value); else watchlistStore.add(symbol.value, stockName.value); }
function goToAnalysis() { router.push({ name: 'analysis', query: { symbol: symbol.value, market: 'A' } }); }
async function downloadReport() {
  const url = window.location.origin + '/api/v1/analysis/download?symbol=' + symbol.value + '&market=A&lookback_days=120';
  window.open(url, '_blank');
}
function formatVolume(v) { if (v >= 1e8) return (v / 1e8).toFixed(2) + '亿'; if (v >= 1e4) return (v / 1e4).toFixed(2) + '万'; return v.toFixed(0); }
function switchPeriod(p) {
  klinePeriod.value = p;
  const days = p === '1M' ? 30 : p === '3M' ? 90 : 180;
  const end = new Date().toISOString().slice(0, 10);
  const start = new Date(Date.now() - days * 86400000).toISOString().slice(0, 10);
  stockStore.fetchKline(symbol.value, 'A', start, end);
}
onMounted(() => { stockStore.fetchQuote(symbol.value); switchPeriod('1M'); stockStore.fetchKline(symbol.value, 'A'); });
watch(symbol, () => { stockStore.clear(); stockStore.fetchQuote(symbol.value); switchPeriod('1M'); });
</script>