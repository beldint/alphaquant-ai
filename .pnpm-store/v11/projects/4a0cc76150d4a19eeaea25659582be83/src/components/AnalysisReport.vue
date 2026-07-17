<template>
  <n-card title="AI 分析报告" size="small" v-if="report">
    <n-spin :show="loading">
      <div class="report-content" v-html="renderedHtml"></div>
    </n-spin>
  </n-card>
</template>
<script setup lang="ts">
import { computed } from 'vue';
const props = defineProps<{ report: string | null; loading: boolean }>();
const renderedHtml = computed(() => {
  if (!props.report) return '<p style="color:#999">暂无分析数据</p>';
  return props.report
    .replace(/### (.+)/g, '<h3>$1</h3>')
    .replace(/## (.+)/g, '<h2>$1</h2>')
    .replace(/# (.+)/g, '<h1>$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br/>')
    .replace(/- (.+)/g, '<li>$1</li>');
});
</script>
<style scoped>.report-content { line-height: 1.8; font-size: 14px; } .report-content h1, .report-content h2, .report-content h3 { margin: 16px 0 8px; } .report-content li { margin-left: 20px; }</style>
