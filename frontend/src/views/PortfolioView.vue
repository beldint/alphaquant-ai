<template>
  <div>
    <div class="page-header"><h2>投资组合</h2><p>追踪和管理您的投资组合</p></div>
    <n-card size="small" class="mb-24">
      <n-grid :cols="3" :x-gap="16">
        <n-grid-item><n-statistic label="持仓数量" :value="holdings.length" :tabular-nums="true" /></n-grid-item>
        <n-grid-item><n-statistic label="总市值" :value="totalValue.toFixed(2)" :tabular-nums="true" /></n-grid-item>
        <n-grid-item><n-statistic label="总盈亏" :value="totalPnl.toFixed(2)" :tabular-nums="true" :style="totalPnl >= 0 ? 'color:var(--up-color)' : 'color:var(--down-color)'" /></n-grid-item>
      </n-grid>
    </n-card>
    <n-data-table v-if="holdings.length > 0" :columns="columns" :data="holdings" :bordered="false" size="small" />
    <n-empty v-else description="暂无持仓数据" style="margin-top:60px" />
  </div>
</template>
<script setup lang="ts">
import { computed, h } from 'vue';
import { NButton, NDataTable } from 'naive-ui';
import type { DataTableColumn } from 'naive-ui';
import { usePortfolioStore } from '../stores/portfolio';
const portfolioStore = usePortfolioStore();
const holdings = portfolioStore.holdings;
const totalValue = computed(() => holdings.reduce((s, h) => s + h.marketValue, 0));
const totalPnl = computed(() => holdings.reduce((s, h) => s + h.pnl, 0));
const columns: DataTableColumn<any>[] = [
  { title: '代码', key: 'symbol', width: 100 },
  { title: '名称', key: 'name', width: 140 },
  { title: '持仓', key: 'quantity', width: 100 },
  { title: '成本价', key: 'averageCost', width: 100 },
  { title: '市值', key: 'marketValue', width: 120, render: (row) => row.marketValue.toFixed(2) },
  { title: '盈亏', key: 'pnl', width: 120, render: (row) => h('span', { style: { color: row.pnl >= 0 ? 'var(--up-color)' : 'var(--down-color)' } }, row.pnl.toFixed(2)) },
  { title: '操作', width: 100, render: (row) => h(NButton, { size: 'tiny', quaternary: true, onClick: () => portfolioStore.remove(row.symbol) }, () => '删除') },
];
</script>
