<template>
  <div>
    <div class="page-header"><h2>股票搜索</h2><p>搜索 A 股、港股、美股股票信息</p></div>
    <n-card size="small" class="mb-24">
      <n-input-group>
        <n-input v-model:value="keyword" placeholder="输入股票代码或名称" clearable @keyup.enter="doSearch" @input="doSearch" />
        <n-button type="primary" @click="doSearch" :loading="loading">搜索</n-button>
      </n-input-group>
    </n-card>
    <n-data-table v-if="results.length > 0" :columns="columns" :data="results" :bordered="false" size="small" :loading="loading" />
    <n-empty v-else-if="!loading" description="输入关键词搜索股票" style="margin-top: 60px;" />
  </div>
</template>
<script setup lang="ts">
import { ref, h } from 'vue';
import { useRouter } from 'vue-router';
import { NButton, NTag, NDataTable } from 'naive-ui';
import type { DataTableColumn } from 'naive-ui';
import { useStockStore } from '../stores/stock';
import { searchStocks } from '../api';
import { useWatchlistStore } from '../stores/watchlist';
const router = useRouter();
const stockStore = useStockStore();
const watchlistStore = useWatchlistStore();
const keyword = ref('');
const loading = ref(false);
const results = ref<any[]>([]);
async function doSearch() {
  if (!keyword.value.trim()) return;
  loading.value = true;
  try {
    var res = await searchStocks(keyword.value.trim(), 'A');
    if (res.code === 0 && res.data) results.value = res.data;
    else results.value = [];
  } catch (e: any) {
    results.value = [];
  }
  loading.value = false;
}
const columns: DataTableColumn<any>[] = [
  { title: '代码', key: 'symbol', width: 100 },
  { title: '名称', key: 'name', width: 140 },
  { title: '市场', key: 'exchange', width: 80, render: (row) => h(NTag, { size: 'small', type: row.exchange === 'SSE' ? 'warning' : row.exchange === 'SZSE' ? 'info' : 'default' }, () => row.exchange) },
  { title: '行业', key: 'industry' },
  { title: '操作', width: 160, render: (row) => [h(NButton, { size: 'tiny', type: 'primary', style: 'margin-right:8px', onClick: () => router.push({ name: 'stockDetail', params: { symbol: row.symbol } }) }, () => '详情'), h(NButton, { size: 'tiny', quaternary: true, onClick: () => watchlistStore.add(row.symbol, row.name, row.market) }, () => '加自选')] },
];
</script>
