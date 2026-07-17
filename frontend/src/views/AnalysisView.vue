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
          <n-space>
          <n-button type="primary" @click="doAnalysis" :loading="loading">开始分析</n-button>
          <n-button @click="downloadReport" :disabled="!stockStore.analysisResult" ghost>下载报告</n-button>
        </n-space>
        </n-grid-item>
      </n-grid>
      <n-collapse class="mt-12" :expanded-names="showAiConfig ? ['ai'] : []" @update:expanded-names="function(v) { showAiConfig = v.length > 0; }">
        <n-collapse-item title="AI 模型配置" name="ai">
          <n-grid :cols="3" :x-gap="12">
            <n-grid-item>
              <n-select v-model:value="aiModel" :options="modelOptions" placeholder="选择模型" size="small"
                :filterable="true" :tag="true" @update:value="function(v) { if (v === '__custom__') aiModel = aiCustom || ''; else aiCustom = ''; }" />
              <n-input v-if="aiModel === '__custom__'" v-model:value="aiCustom" placeholder="输入自定义模型名" size="small" class="mt-6" />
            </n-grid-item>
            <n-grid-item><n-input v-model:value="aiBaseUrl" placeholder="API 地址 (如 https://api.deepseek.com/v1)" size="small" /></n-grid-item>
            <n-grid-item><n-input v-model:value="aiApiKey" type="password" placeholder="API Key" show-password-on="click" size="small" /></n-grid-item>
          </n-grid>
        </n-collapse-item>
      </n-collapse>
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
import { ref } from 'vue';
import { useRoute } from 'vue-router';
import { useStockStore } from '../stores/stock';
import TechnicalIndicators from '../components/TechnicalIndicators.vue';
import AnalysisReport from '../components/AnalysisReport.vue';
import { NCollapse, NCollapseItem, NSelect } from 'naive-ui';
const route = useRoute();
const stockStore = useStockStore();
const symbol = ref(route.query.symbol as string || '000001');
const market = ref('A');
const lookbackDays = ref(120);
const aiModel = ref(localStorage.getItem('ai_model') || '');
const aiBaseUrl = ref(localStorage.getItem('ai_base_url') || '');
const aiApiKey = ref(localStorage.getItem('ai_api_key') || '');
const showAiConfig = ref(!!localStorage.getItem('ai_model') || !!localStorage.getItem('ai_base_url') || !!localStorage.getItem('ai_api_key'));
const aiCustom = ref('');
const modelOptions = [
  { label: 'DeepSeek Chat', value: 'deepseek-chat' },
  { label: 'DeepSeek Reasoner', value: 'deepseek-reasoner' },
  { label: 'GPT-4o', value: 'gpt-4o' },
  { label: 'GPT-4o-mini', value: 'gpt-4o-mini' },
  { label: 'Claude 3.5 Sonnet', value: 'claude-3-5-sonnet-20241022' },
  { label: 'Qwen Max', value: 'qwen-max' },
  { label: 'Qwen Plus', value: 'qwen-plus' },
  { label: '自定义', value: '__custom__' },
];
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
  localStorage.setItem('ai_model', aiModel.value);
  localStorage.setItem('ai_base_url', aiBaseUrl.value);
  localStorage.setItem('ai_api_key', aiApiKey.value);
  loading.value = true;
  const m = aiModel.value === '__custom__' ? aiCustom.value || undefined : aiModel.value || undefined;
  const u = aiBaseUrl.value || undefined;
  const k = aiApiKey.value || undefined;
  await stockStore.analyze(symbol.value, market.value, lookbackDays.value, m, u, k);
  await stockStore.fetchKline(symbol.value, market.value);
  klineData.value = stockStore.klineData;
  loading.value = false;
}


function downloadReport() {
  if (!stockStore.analysisResult?.report_markdown) return;
  var blob = new Blob([stockStore.analysisResult.report_markdown], { type: "text/markdown;charset=utf-8" });
  var url = URL.createObjectURL(blob);
  var a = document.createElement("a");
  a.href = url;
  a.download = "analysis_" + symbol.value + "_" + market.value + "_" + lookbackDays.value + "d.md";
  a.click();
  URL.revokeObjectURL(url);
}
</script>
