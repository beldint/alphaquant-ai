<template>
  <div class="app-header">
    <div class="header-left">
      <n-breadcrumb>
        <n-breadcrumb-item>AlphaQuant AI</n-breadcrumb-item>
        <n-breadcrumb-item>{{ routeName }}</n-breadcrumb-item>
      </n-breadcrumb>
    </div>
    <div class="header-right">
      <template v-if="isLoggedIn">
        <n-tag type="success" size="small">{{ username }}</n-tag>
        <n-button text size="small" @click="handleLogout">退出</n-button>
        <n-button text size="tiny" @click="handleClearData" style="margin-left:4px">清除缓存</n-button>
      </template>
      <n-button v-else text size="small" @click="router.push({ name: 'login' })">登录</n-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const routeName = computed(() => {
  const map: Record<string, string> = {
    dashboard: '行情中心',
    market: '股票搜索',
    watchlist: '自选股',
    portfolio: '投资组合',
    analysis: 'AI分析',
    login: '登录',
    register: '注册',
    stockDetail: '股票详情',
    financials: '财务分析',
  };
  return map[route.name as string] || '未知';
});

const isLoggedIn = computed(() => authStore.isLoggedIn);
const username = computed(() => authStore.user?.username || '');

function handleClearData(): void {
  const keys = ['ai_model', 'ai_base_url', 'ai_api_key', 'ai_custom', 'portfolio_holdings', 'token'];
  for (const key of keys) {
    localStorage.removeItem(key);
  }
}

function handleLogout(): void {
  authStore.logout();
  router.push({ name: 'login' });
}
</script>

<style scoped>
.app-header { height: var(--header-height); display: flex; align-items: center; justify-content: space-between; padding: 0 24px; border-bottom: 1px solid var(--border-color); background: var(--card-bg); flex-shrink: 0; }
.header-left { display: flex; align-items: center; }
.header-right { display: flex; align-items: center; gap: 12px; }
</style>
