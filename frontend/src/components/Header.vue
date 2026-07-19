<template>
  <div class="app-header">
    <div class="header-left">
      <n-breadcrumb>
        <n-breadcrumb-item>AlphaQuant AI</n-breadcrumb-item>
        <n-breadcrumb-item>{{ routeName }}</n-breadcrumb-item>
      </n-breadcrumb>
    </div>
    <div class="header-right">
      <n-tooltip trigger="hover" :placement="'bottom'">
        <template #trigger>
          <n-button text size="tiny" @click="cycleTheme" style="font-size:16px;display:flex;align-items:center">
            <svg v-if="themeStore.mode === 'day'" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58a.996.996 0 0 0-1.41 0 .996.996 0 0 0 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0s.39-1.03 0-1.41L5.99 4.58zm12.37 12.37a.996.996 0 0 0-1.41 0 .996.996 0 0 0 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0a.996.996 0 0 0 0-1.41l-1.06-1.06zm1.06-10.96a.996.996 0 0 0 0-1.41.996.996 0 0 0-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06zM7.05 18.36a.996.996 0 0 0 0-1.41.996.996 0 0 0-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06z"/>
            </svg>
            <svg v-else-if="themeStore.mode === 'night'" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 3a9 9 0 1 0 9 9c0-.46-.04-.92-.1-1.36a5.389 5.389 0 0 1-4.4 2.26 5.403 5.403 0 0 1-3.14-9.8c-.44-.06-.9-.1-1.36-.1z"/>
            </svg>
            <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
            </svg>
          </n-button>
        </template>
        {{ themeLabel }}
      </n-tooltip>
      <n-button text size="tiny" @click="handleClearData">清除缓存</n-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { useThemeStore } from '../stores/theme';

const themeStore = useThemeStore();
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

const themeLabel = computed(() => {
  const labels: Record<string, string> = { day: '白天模式', night: '黑夜模式', eyeCare: '护眼模式' };
  return labels[themeStore.mode] || '白天模式';
});

function cycleTheme(): void {
  themeStore.toggle();
}

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