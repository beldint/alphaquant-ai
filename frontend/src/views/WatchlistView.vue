<template>
  <div>
    <div class="page-header"><h2>自选股</h2><p>管理您的自选股票列表</p></div>
    <n-data-table v-if="items.length > 0" :columns="columns" :data="items" :bordered="false" size="small" />
    <n-empty v-else description="暂无自选股，在行情中心或股票搜索中添加" style="margin-top:60px" />
  </div>
</template>
<script setup lang="ts">
import { h } from 'vue';
import { useRouter } from 'vue-router';
import { NButton, NTag, NDataTable } from 'naive-ui';
import type { DataTableColumn } from 'naive-ui';
import { useWatchlistStore } from '../stores/watchlist';
const router = useRouter();
const watchlistStore = useWatchlistStore();
const items = watchlistStore.items;
const columns: DataTableColumn<any>[] = [
  { title: '代码', key: 'symbol', width: 100 },
  { title: '名称', key: 'name', width: 140 },
  { title: '市场', key: 'market', width: 80, render: (row) => h(NTag, { size: 'small', type: row.market === 'A' ? 'warning' : 'info' }, () => row.market) },
  { title: '添加时间', key: 'addedAt', render: (row) => new Date(row.addedAt).toLocaleDateString('zh-CN') },
  { title: '操作', width: 180, render: (row) => [h(NButton, { size: 'tiny', type: 'primary', style: 'margin-right:8px', onClick: () => router.push({ name: 'stockDetail', params: { symbol: row.symbol } }) }, () => '查看'), h(NButton, { size: 'tiny', quaternary: true, onClick: () => watchlistStore.remove(row.symbol) }, () => '删除')] },
];
</script>
