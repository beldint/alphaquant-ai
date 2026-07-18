<template>
  <div>
    <div class="page-header">
      <h2>股票搜索</h2>
      <p>搜索 A 股、港股、美股股票信息</p>
    </div>

    <n-card size="small" class="mb-24">
      <n-input-group>
        <n-input v-model:value="keyword" placeholder="输入股票代码或名称" clearable @keyup.enter="doSearch" />
        <n-button type="primary" :loading="loading" @click="doSearch">搜索</n-button>
      </n-input-group>
    </n-card>

    <n-data-table
      v-if="results.length > 0"
      :columns="columns"
      :data="results"
      :bordered="false"
      size="small"
      :loading="loading"
    />

    <n-empty v-else-if="!loading" description="输入关键词搜索股票" style="margin-top: 60px;" />
  </div>
</template>

<script setup lang="ts">
import { h, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { NButton, NTag, NDataTable } from 'naive-ui';
import type { DataTableColumn } from 'naive-ui';
import { searchStocks } from '../api';
import { useWatchlistStore } from '../stores/watchlist';
import { formatExchange } from '../utils/market';

interface SearchRow {
  symbol: string;
  name: string;
  market: string;
  exchange: string;
  industry: string | null;
}

const router = useRouter();
const watchlistStore = useWatchlistStore();
const keyword = ref('');
const loading = ref(false);
const results = ref<SearchRow[]>([]);
let searchTimer: ReturnType<typeof setTimeout> | null = null;

watch(keyword, () => {
  if (searchTimer) clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    searchTimer = null;
    void doSearch();
  }, 400);
});

async function doSearch(): Promise<void> {
  if (!keyword.value.trim()) return;
  loading.value = true;
  try {
    const res = await searchStocks(keyword.value.trim(), 'A');
    if (res.code === 0 && res.data) {
      results.value = res.data.map((item) => ({
        symbol: item.symbol || '',
        name: item.name || '',
        market: item.market || 'A',
        exchange: item.exchange || 'SZSE',
        industry: item.industry || null,
      }));
    } else {
      results.value = [];
    }
  } catch {
    results.value = [];
  } finally {
    loading.value = false;
  }
}

function toggleWatch(row: SearchRow): void {
  const added = watchlistStore.toggle(row.symbol, row.name, row.market);
  if (added) {
    router.push({ name: 'watchlist' });
  }
}

const columns: DataTableColumn<SearchRow>[] = [
  { title: '代码', key: 'symbol', width: 100 },
  { title: '名称', key: 'name', width: 140 },
  {
    title: '市场',
    key: 'exchange',
    width: 96,
    render: (row) => h(NTag, { size: 'small', type: row.exchange === 'SSE' ? 'warning' : row.exchange === 'SZSE' ? 'info' : 'default' }, () => formatExchange(row.exchange)),
  },
  { title: '行业', key: 'industry' },
  {
    title: '操作',
    key: 'actions',
    width: 180,
    render: (row) => {
      const watched = watchlistStore.isInWatchlist(row.symbol);
      return [
        h(NButton, {
          size: 'tiny',
          type: 'primary',
          style: 'margin-right:8px',
          onClick: () => router.push({ name: 'stockDetail', params: { symbol: row.symbol } }),
        }, () => '详情'),
        h(NButton, {
          size: 'tiny',
          quaternary: true,
          type: watched ? 'warning' : 'primary',
          onClick: () => toggleWatch(row),
        }, () => (watched ? '已自选' : '加自选')),
      ];
    },
  },
];
</script>
