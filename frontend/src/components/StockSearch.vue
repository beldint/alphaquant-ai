<template>
  <div>
    <n-input-group>
      <n-input v-model:value="keyword" placeholder="输入股票代码或名称搜索" clearable @keyup.enter="doSearch" />
      <n-button type="primary" @click="doSearch" :loading="loading">
        <template #icon><n-icon><svg viewBox="0 0 24 24" fill="currentColor"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg></n-icon></template>搜索
      </n-button>
    </n-input-group>
  </div>
</template>
<script setup lang="ts">
import { ref } from 'vue';
import { useStockStore } from '../stores/stock';
const emit = defineEmits<{ search: [results: any[]] }>();
const keyword = ref('');
const loading = ref(false);
const stockStore = useStockStore();
async function doSearch() {
  if (!keyword.value.trim()) return;
  loading.value = true;
  await stockStore.search(keyword.value.trim(), 'ALL');
  emit('search', stockStore.searchResults);
  loading.value = false;
}
function setKeyword(val: string) { keyword.value = val; }
defineExpose({ setKeyword, doSearch });
</script>
