<template>
  <div class="app-header">
    <div class="header-left">
      <n-breadcrumb>
        <n-breadcrumb-item>AlphaQuant AI</n-breadcrumb-item>
        <n-breadcrumb-item>{{ routeName }}</n-breadcrumb-item>
      </n-breadcrumb>
    </div>
    <div class="header-right">
      <n-button text size="tiny" @click="handleClearData">清除缓存</n-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();

const routeName = computed(() => {
  const map: Record<string, string> = {
    dashboard: '行情中心',
    market: '股票搜索',
    watchlist: '自选股',
    portfolio: '投资组合',
    analysis: 'AI分析',
    stockDetail: '股票详情',
    financials: '财务分析',
  };
  return map[route.name as string] || '未知';
});

function handleClearData(): void {
  const keys = ['ai_model', 'ai_base_url', 'ai_api_key', 'ai_custom', 'portfolio_holdings', 'token'];
  for (const key of keys) {
    localStorage.removeItem(key);
  }
}
</script>

<style scoped>
.app-header { height: var(--header-height); display: flex; align-items: center; justify-content: space-between; padding: 0 24px; border-bottom: 1px solid var(--border-color); background: var(--card-bg); flex-shrink: 0; }
.header-left { display: flex; align-items: center; }
.header-right { display: flex; align-items: center; gap: 12px; }
</style>
