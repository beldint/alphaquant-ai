<template>
  <div>
    <div class="page-header"><h2>行情中心</h2><p>实时行情概览，快速搜索和浏览股票数据</p></div>
    <n-grid :cols="4" :x-gap="16" class="mb-24">
      <n-grid-item><n-statistic label="上证指数" :value="shIndex" :tabular-nums="true" /></n-grid-item>
      <n-grid-item><n-statistic label="深证成指" :value="szIndex" :tabular-nums="true" /></n-grid-item>
      <n-grid-item><n-statistic label="创业板指" :value="cybIndex" :tabular-nums="true" /></n-grid-item>
      <n-grid-item><n-statistic label="科创板指" :value="kcbIndex" :tabular-nums="true" /></n-grid-item>
    </n-grid>
    <n-card title="股票搜索" size="small" class="mb-24">
      <StockSearch @search="onSearchResults" ref="searchRef" />
      <n-data-table v-if="results.length > 0" :columns="columns" :data="results" :bordered="false" size="small" class="mb-16" :max-height="400" />
    </n-card>
    <n-card title="热门股票" size="small">
      <n-data-table :columns="hotColumns" :data="hotStocks" :bordered="false" size="small" :loading="loading" />
    </n-card>
  </div>
</template>
<script setup lang="ts">
import { ref, h, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { NButton, NTag, NDataTable } from 'naive-ui';
import type { DataTableColumn } from 'naive-ui';
import { searchStocks } from "../api";
import StockSearch from '../components/StockSearch.vue';
import { useStockStore } from '../stores/stock';
import { useWatchlistStore } from '../stores/watchlist';
const router = useRouter();
const stockStore = useStockStore();
const watchlistStore = useWatchlistStore();
const searchRef = ref<any>(null);
const results = ref<any[]>([]);
const loading = ref(false);
const shIndex = ref('---');
const szIndex = ref('---');
const cybIndex = ref('---');
const kcbIndex = ref('---');
function onSearchResults(r: any[]) { results.value = r; }
const columns: DataTableColumn<any>[] = [
  { title: '代码', key: 'symbol', width: 100 },
  { title: '名称', key: 'name', width: 140 },
  { title: '市场', key: 'exchange', width: 80, render: (row) => h(NTag, { size: 'small', type: row.exchange === 'SSE' ? 'warning' : 'info' }, () => row.exchange) },
  { title: '行业', key: 'industry' },
  { title: '操作', width: 160, render: (row) => [h(NButton, { size: 'tiny', type: 'primary', style: 'margin-right:8px', onClick: () => router.push({ name: 'stockDetail', params: { symbol: row.symbol } }) }, () => '详情'), h(NButton, { size: 'tiny', quaternary: true, onClick: () => watchlistStore.add(row.symbol, row.name, row.market) }, () => '加自选')] },
];
const hotStocks = ref([
  { symbol: '000001', name: '平安银行', exchange: 'SZSE', industry: '银行' },
  { symbol: '600519', name: '贵州茅台', exchange: 'SSE', industry: '食品饮料' },
  { symbol: '000858', name: '五粮液', exchange: 'SZSE', industry: '食品饮料' },
  { symbol: '600036', name: '招商银行', exchange: 'SSE', industry: '银行' },
  { symbol: '300750', name: '宁德时代', exchange: 'SZSE', industry: '电力设备' },
  { symbol: '601318', name: '中国平安', exchange: 'SSE', industry: '保险' },
  { symbol: '000333', name: '美的集团', exchange: 'SZSE', industry: '家用电器' },
  { symbol: '600900', name: '长江电力', exchange: 'SSE', industry: '公用事业' },
]);
const hotColumns: DataTableColumn<any>[] = [
  { title: '代码', key: 'symbol', width: 100 },
  { title: '名称', key: 'name', width: 140 },
  { title: '市场', key: 'exchange', width: 80, render: (row) => h(NTag, { size: 'small', type: row.exchange === 'SSE' ? 'warning' : 'info' }, () => row.exchange) },
  { title: '行业', key: 'industry' },
  { title: '操作', width: 100, render: (row) => h(NButton, { size: 'tiny', type: 'primary', onClick: () => router.push({ name: 'stockDetail', params: { symbol: row.symbol } }) }, () => '查看') },
];
onMounted(async () => {
  try {
    const res = await searchStocks("000001", "A");
    if (res.code === 0 && res.data && res.data.length > 0)
      shIndex.value = res.data[0].symbol + " " + res.data[0].name;
    const res2 = await searchStocks("000333", "A");
    if (res2.code === 0 && res2.data && res2.data.length > 0)
      szIndex.value = res2.data[0].symbol + " " + res2.data[0].name;
    const res3 = await searchStocks("300750", "A");
    if (res3.code === 0 && res3.data && res3.data.length > 0)
      cybIndex.value = res3.data[0].symbol + " " + res3.data[0].name;
    const res4 = await searchStocks("688981", "A");
    if (res4.code === 0 && res4.data && res4.data.length > 0)
      kcbIndex.value = res4.data[0].symbol + " " + res4.data[0].name;
  } catch(e) { console.error(e) }
});
</script>
