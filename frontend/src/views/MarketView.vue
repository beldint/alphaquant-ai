<template>
  <div>
    <div class="page-header">
      <h2>琛屾儏涓績</h2>
      <p>瀹炴椂琛屾儏姒傝銆佸揩閫熸悳绱㈠拰娴忚鑲＄エ鏁版嵁</p>
    </div>

    <n-grid :cols="4" :x-gap="16" class="mb-24" responsive="screen">
      <n-grid-item><n-statistic label="涓婅瘉鎸囨暟" :value="shIndex" :tabular-nums="true" /></n-grid-item>
      <n-grid-item><n-statistic label="娣辫瘉鎴愭寚" :value="szIndex" :tabular-nums="true" /></n-grid-item>
      <n-grid-item><n-statistic label="鍒涗笟鏉挎寚" :value="cybIndex" :tabular-nums="true" /></n-grid-item>
      <n-grid-item><n-statistic label="绉戝垱50" :value="kcbIndex" :tabular-nums="true" /></n-grid-item>
    </n-grid>

    <n-card title="鑲＄エ鎼滅储" size="small" class="mb-24">
      <StockSearch ref="searchRef" @search="onSearchResults" />
      <div class="overflow-table"><n-data-table
        v-if="results.length > 0"
        :columns="columns"
        :data="results"
        :bordered="false"
        size="small"
        class="mb-16"
        :max-height="400"
      /></div>
      <n-empty v-if="results.length === 0" description="璇疯緭鍏ヨ偂绁ㄤ唬鐮佹垨鍚嶇О鎼滅储" style="margin-top: 24px" />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { h, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { NButton, NCard, NDataTable, NEmpty, NGrid, NGridItem, NStatistic, NTag } from 'naive-ui';
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
const shIndex = ref('--');
const szIndex = ref('--');
const cybIndex = ref('--');
const kcbIndex = ref('--');

function onSearchResults(rows: StockRow[]): void {
  results.value = rows;
}

function addWatch(row: StockRow): void {
  watchlistStore.add(row.symbol, row.name, row.market);
}

function goDetail(row: StockRow): void {
  router.push({ name: 'stockDetail', params: { symbol: row.symbol }, query: { market: row.market } });
}

function exchangeTag(row: StockRow) {
  return h(NTag, { size: 'small', type: row.exchange === 'SSE' ? 'warning' : row.exchange === 'SZSE' ? 'info' : 'default' }, () => formatExchange(row.exchange));
}

function actionButtons(row: StockRow) {
  return [
    h(NButton, { size: 'tiny', type: 'primary', style: 'margin-right:8px', onClick: () => goDetail(row) }, () => '璇︽儏'),
    h(NButton, { size: 'tiny', quaternary: true, onClick: () => addWatch(row) }, () => '加自选'),
  ];
}

const columns: DataTableColumn<StockRow>[] = [
  { title: '浠ｇ爜', key: 'symbol', width: 100 },
  { title: '鍚嶇О', key: 'name', width: 140 },
  { title: '甯傚満', key: 'exchangeTag', width: 96, render: exchangeTag },
  { title: '琛屼笟', key: 'industry', render: (row) => row.industry || '--' },
  { title: '鎿嶄綔', key: 'actions', width: 160, render: actionButtons },
];

async function loadIndexHint(symbol: string): Promise<string> {
  const response = await searchStocks(symbol, 'A');
  const first = Number(response.code) === 0 && response.data?.length ? response.data[0] : null;
  return first ? `${first.symbol} ${first.name}` : '--';
}

onMounted(async () => {
  try {
    const [sh, sz, cyb, kcb] = await Promise.all([
      loadIndexHint('000001'),
      loadIndexHint('000333'),
      loadIndexHint('300750'),
      loadIndexHint('688981'),
    ]);
    shIndex.value = sh;
    szIndex.value = sz;
    cybIndex.value = cyb;
    kcbIndex.value = kcb;
  } catch (error) {
    console.error(error);
  }
});
</script>
