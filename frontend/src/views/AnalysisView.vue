<template>
  <div>
    <div class="page-header"><h2>AI 分析</h2><p>基于技术指标和AI模型生成专业股票分析报告</p></div>
    <n-card size="small" class="mb-24">
      <n-grid :cols="4" :x-gap="16">
        <n-grid-item><n-input v-model:value="symbol" placeholder="股票代码" clearable /></n-grid-item>
        <n-grid-item>
          <n-select v-model:value="market" :options="marketOptions" />
        </n-grid-item>
        <n-grid-item>
          <n-input-number v-model:value="lookbackDays" :min="20" :max="1000" placeholder="回溯天数" />
        </n-grid-item>
        <n-grid-item>
          <n-button type="primary" @click="doAnalysis" :loading="loading" block>开始分析</n-button>
        </n-grid-item>
      </n-grid>
    </n-card>
    <template v-if="stockStore.analysisResult">
      <n-grid :cols="3" :x-gap="16" class="mb-24">
        <n-grid-item>
          <n-statistic label="股票代码" :value="stockStore.analysisResult.symbol" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic label="数据时间" :value="stockStore.analysisResult.data_timestamp.slice(0, 10)" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic label="分析模型" :value="stockStore.analysisResult.model" />
        </n-grid-item>
      </n-grid>
      <TechnicalIndicators :data="klineData" title="技术指标概览" class="mb-24" />
      <AnalysisReport :report="stockStore.analysisResult?.report_markdown ?? null" :loading="loading" />
    </template>
    <n-empty v-else-if="!loading" description="输入股票代码并点击开始分析" style="margin-top:60px" />
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useStockStore } from '../stores/stock';
import TechnicalIndicators from '../components/TechnicalIndicators.vue';
import AnalysisReport from '../components/AnalysisReport.vue';
const route = useRoute();
const stockStore = useStockStore();
const symbol = ref(route.query.symbol as string || '000001');
const market = ref('A');
const lookbackDays = ref(120);
const loading = ref(false);
const klineData = ref<any[]>([]);
const downloading = ref(false);
const downloadReport = () => {
  const s = stockStore.analysisResult?.symbol || symbol.value;
  const url = `/api/v1/analysis/download?symbol=${s}&market=${market.value}&lookback_days=${lookbackDays.value}`;
  downloading.value = true;
  window.open(url, "_blank");
  setTimeout(() => { downloading.value = false; }, 3000);
};
const marketOptions = [{ label: 'A股', value: 'A' }, { label: '港股', value: 'HK' }, { label: '美股', value: 'US' }];
async function doAnalysis() {
  if (!symbol.value.trim()) return;
  loading.value = true;
  await stockStore.analyze(symbol.value, market.value, lookbackDays.value);
  await stockStore.fetchKline(symbol.value, market.value);
  klineData.value = stockStore.klineData;
  loading.value = false;
}
onMounted(() => { if (route.query.symbol) doAnalysis(); });
</script>
