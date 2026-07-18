<template>
  <div>
    <div class="page-header">
      <h2>自选股</h2>
      <p>管理您的自选股票列表</p>
    </div>

    <n-data-table v-if="items.length > 0" :row-key="rowKey" :columns="columns" :data="items" :bordered="false" size="small" />
    <n-empty v-else description="暂无自选股，在行情中心或股票搜索中添加" style="margin-top: 60px" />
  </div>
</template>

<script setup lang="ts">
import { h } from 'vue';
import { storeToRefs } from 'pinia';
import { useRouter } from 'vue-router';
import { NButton, NTag, NDataTable, useMessage } from 'naive-ui';
import type { DataTableColumn } from 'naive-ui';
import { useWatchlistStore } from '../stores/watchlist';
import { formatExchange, formatMarket } from '../utils/market';

const router = useRouter();
const message = useMessage();
const watchlistStore = useWatchlistStore();
const { items } = storeToRefs(watchlistStore);

function removeAndStay(symbol: string): void {
  watchlistStore.remove(symbol);
  message.success('已从自选股移除');
}

function rowKey(row: { symbol: string }): string {
  return row.symbol;
}

const columns: DataTableColumn<any>[] = [
  { title: '代码', key: 'symbol', width: 100 },
  { title: '名称', key: 'name', width: 140 },
  {
    title: '市场',
    key: 'marketTag',
    width: 96,
    render: (row) => h(NTag, { size: 'small', type: row.market === 'A' ? 'warning' : row.market === 'HK' ? 'info' : 'default' }, () => formatMarket(row.market)),
  },
  {
    title: '交易所',
    key: 'exchangeTag',
    width: 96,
    render: (row) => h(NTag, { size: 'small', type: row.market === 'A' ? 'warning' : 'info' }, () => formatExchange(row.market === 'A' ? 'SZSE' : row.market === 'HK' ? 'HKEX' : row.market)),
  },
  { title: '添加时间', key: 'addedAt', render: (row) => new Date(row.addedAt).toLocaleDateString('zh-CN') },
  {
    title: '操作',
    key: 'actions',
    width: 180,
    render: (row) => [
      h(NButton, { size: 'tiny', type: 'primary', style: 'margin-right:8px', onClick: () => router.push({ name: 'stockDetail', params: { symbol: row.symbol } }) }, () => '查看'),
      h(NButton, { size: 'tiny', quaternary: true, type: 'warning', onClick: () => removeAndStay(row.symbol) }, () => '取消自选'),
    ],
  },
];
</script>
