<template>
  <div>
    <div class="page-header">
      <h2>行情中心</h2>
      <p>实时行情概览，快速搜索和浏览股票数据</p>
    </div>
    <n-grid :cols="2" :x-gap="12" :y-gap="12" class="mb-24" responsive="screen">
      <n-grid-item><n-statistic label="上证指数" :value="shIndex" :tabular-nums="true" /></n-grid-item>
      <n-grid-item><n-statistic label="深证成指" :value="szIndex" :tabular-nums="true" /></n-grid-item>
      <n-grid-item><n-statistic label="创业板指" :value="cybIndex" :tabular-nums="true" /></n-grid-item>
      <n-grid-item><n-statistic label="科创50" :value="kcbIndex" :tabular-nums="true" /></n-grid-item>
    </n-grid>
    <n-card title="股票搜索" size="small" class="mb-24">
      <StockSearch ref="searchRef" @search="onSearchResults" />
      <div class="overflow-table">
        <n-data-table v-if="results.length > 0" :columns="columns" :data="results" :bordered="false" size="small" class="mb-16" :max-height="400" />
      </div>
    </n-card>
    <n-card title="热门股票" size="small">
      <div class="overflow-table">
        <n-data-table :columns="hotColumns" :data="hotStocks" :bordered="false" size="small" :loading="loading" />
      </div>
    </n-card>
  </div>
</template>
<script setup lang="ts">
import { h, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { NButton, NCard, NDataTable, NGrid, NGridItem, NStatistic, NTag } from 'naive-ui';
import type { DataTableColumn } from 'naive-ui';
import { searchStocks } from '../api';
import StockSearch from '../components/StockSearch.vue';
import { useWatchlistStore } from '../stores/watchlist';
import { formatExchange } from '../utils/market';
import type { StockIdentity } from '../stores/stock';
type StockRow = StockIdentity;
const router = useRouter();
const watchlistStore = useWatchlistStore();
const searchRef = ref<InstanceType<typeof StockSearch> | null>(null);
const results = ref<StockRow[]>([]);
const loading = ref(false);
const shIndex = ref('---');
const szIndex = ref('---');
const cybIndex = ref('---');
const kcbIndex = ref('---');
const hotStocks = ref<StockRow[]>([
  { symbol: '000001', name: '平安银行', market: 'A', exchange: 'SZSE', industry: '银行' },
  { symbol: '600519', name: '贵州茅台', market: 'A', exchange: 'SSE', industry: '食品饮料' },
  { symbol: '000858', name: '五粮液', market: 'A', exchange: 'SZSE', industry: '食品饮料' },
  { symbol: '600036', name: '招商银行', market: 'A', exchange: 'SSE', industry: '银行' },
  { symbol: '300750', name: '宁德时代', market: 'A', exchange: 'SZSE', industry: '电力设备' },
  { symbol: '601318', name: '中国平安', market: 'A', exchange: 'SSE', industry: '非银金融' },
  { symbol: '000333', name: '美的集团', market: 'A', exchange: 'SZSE', industry: '家用电器' },
  { symbol: '600900', name: '长江电力', market: 'A', exchange: 'SSE', industry: '公用事业' },
]);
function onSearchResults(rows: StockRow[]): void { results.value = rows; }
function addWatch(row: StockRow): void { watchlistStore.add(row.symbol, row.name, row.market); }
function goDetail(row: StockRow): void { router.push({ name: 'stockDetail', params: { symbol: row.symbol } }); }
function exchangeTag(row: StockRow) { return h(NTag, { size: 'small', type: row.exchange === 'SSE' ? 'warning' : row.exchange === 'SZSE' ? 'info' : 'default' }, () => formatExchange(row.exchange)); }
function actionButtons(row: StockRow) { return [h(NButton, { size: 'tiny', type: 'primary', style: 'margin-right:8px', onClick: () => goDetail(row) }, () => '详情'), h(NButton, { size: 'tiny', quaternary: true, onClick: () => addWatch(row) }, () => '加自选')]; }
const columns: DataTableColumn<StockRow>[] = [
  { title: '代码', key: 'symbol', width: 100 },
  { title: '名称', key: 'name', width: 140 },
  { title: '市场', key: 'exchangeTag', width: 96, render: exchangeTag },
  { title: '行业', key: 'industry' },
  { title: '操作', key: 'actions', width: 160, render: actionButtons },
];
const hotColumns: DataTableColumn<StockRow>[] = [
  { title: '代码', key: 'symbol', width: 100 },
  { title: '名称', key: 'name', width: 140 },
  { title: '市场', key: 'exchangeTag', width: 96, render: exchangeTag },
  { title: '行业', key: 'industry' },
  { title: '操作', key: 'actions', width: 100, render: (row) => h(NButton, { size: 'tiny', type: 'primary', onClick: () => goDetail(row) }, () => '查看') },
];
async function loadIndexHint(symbol: string): Promise<string> {
  const response = await searchStocks(symbol, 'A');
  const first = response.code === 0 && response.data?.length ? response.data[0] : null;
  return first ? first.symbol + ' ' + first.name : '---';
}
onMounted(async () => {
  try {
    const [sh, sz, cyb, kcb] = await Promise.all([
      loadIndexHint('000001'), loadIndexHint('000333'), loadIndexHint('300750'), loadIndexHint('688981'),
    ]);
    shIndex.value = sh; szIndex.value = sz; cybIndex.value = cyb; kcbIndex.value = kcb;
  } catch (error) { console.error(error); }
});
</script>