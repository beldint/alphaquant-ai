<template>
  <n-layout-sider
    bordered
    :width="240"
    :collapsed-width="64"
    :collapsed="collapsed"
    :native-scrollbar="false"
    class="app-sidebar"
  >
    <div class="sidebar-logo">
      <n-icon size="28" color="#2080f0">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z" />
        </svg>
      </n-icon>
      <span v-if="!collapsed" class="sidebar-title">AlphaQuant AI</span>
    </div>

    <n-menu
      :value="activeKey"
      :collapsed="collapsed"
      :collapsed-width="64"
      :collapsed-icon-size="22"
      :options="menuOptions"
      @update:value="handleMenuSelect"
    />

    <template #footer>
      <div v-if="!collapsed" class="sidebar-footer">
        <n-button quaternary size="small" @click="toggleCollapse">
          <template #icon>
            <n-icon>
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z" />
              </svg>
            </n-icon>
          </template>
          收起
        </n-button>
      </div>
    </template>
  </n-layout-sider>
</template>

<script setup lang="ts">
import { computed, h, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { NIcon, useMessage } from 'naive-ui';

const router = useRouter();
const route = useRoute();
const message = useMessage();
const collapsed = ref(false);
const activeKey = computed(() => (route.name as string) || 'dashboard');

function renderIcon(path: string) {
  return () => h(NIcon, null, { default: () => h('svg', { viewBox: '0 0 24 24', fill: 'currentColor', innerHTML: path }) });
}

const menuOptions = [
  { label: '行情中心', key: 'dashboard', icon: renderIcon('<path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"/>') },
  { label: '股票搜索', key: 'market', icon: renderIcon('<path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>') },
  { label: '自选股', key: 'watchlist', icon: renderIcon('<path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>') },
  { label: 'AI分析', key: 'analysis', icon: renderIcon('<path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/>') },
  { label: '清除本地数据', key: 'clearData', icon: renderIcon('<path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>') },
  { type: 'divider' },
  { label: '登录 / 注册', key: 'login', icon: renderIcon('<path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>') },
];

function handleMenuSelect(key: string): void {
  if (key === 'clearData') {
    const keys = ['ai_model', 'ai_base_url', 'ai_api_key', 'ai_custom', 'token'];
    for (const item of keys) {
      localStorage.removeItem(item);
    }
    message.success('已清除所有本地缓存数据');
    return;
  }
  router.push({ name: key });
}

function toggleCollapse(): void {
  collapsed.value = !collapsed.value;
}
</script>

<style scoped>
.app-sidebar { height: 100vh; background: var(--card-bg); }
.sidebar-logo { display: flex; align-items: center; gap: 10px; padding: 16px 20px; border-bottom: 1px solid var(--border-color); }
.sidebar-title { font-size: 18px; font-weight: 700; color: var(--text-primary); }
.sidebar-footer { padding: 12px 16px; border-top: 1px solid var(--border-color); display: flex; justify-content: center; }
</style>
