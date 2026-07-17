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
  { type: 'group', label: 'DeepSeek', key: 'deepseek', options: [
    { label: 'DeepSeek Chat', value: 'deepseek-chat' },
    { label: 'DeepSeek Reasoner', value: 'deepseek-reasoner' },
    { label: 'DeepSeek V3', value: 'deepseek-chat' },
    { label: 'DeepSeek R1', value: 'deepseek-reasoner' },
  ]},
  { type: 'group', label: 'OpenAI', key: 'openai', options: [
    { label: 'GPT-4o', value: 'gpt-4o' },
    { label: 'GPT-4o mini', value: 'gpt-4o-mini' },
    { label: 'GPT-4 Turbo', value: 'gpt-4-turbo' },
    { label: 'GPT-4', value: 'gpt-4' },
    { label: 'GPT-3.5 Turbo', value: 'gpt-3.5-turbo' },
    { label: 'o1', value: 'o1' },
    { label: 'o1-mini', value: 'o1-mini' },
    { label: 'o3-mini', value: 'o3-mini' },
  ]},
  { type: 'group', label: 'Anthropic Claude', key: 'claude', options: [
    { label: 'Claude 3.5 Sonnet', value: 'claude-3-5-sonnet-20241022' },
    { label: 'Claude 3.5 Haiku', value: 'claude-3-5-haiku-20241022' },
    { label: 'Claude 3 Opus', value: 'claude-3-opus-20240229' },
    { label: 'Claude 3 Sonnet', value: 'claude-3-sonnet-20240229' },
    { label: 'Claude 3 Haiku', value: 'claude-3-haiku-20240307' },
  ]},
  { type: 'group', label: 'Google Gemini', key: 'gemini', options: [
    { label: 'Gemini 2.0 Flash', value: 'gemini-2.0-flash' },
    { label: 'Gemini 1.5 Pro', value: 'gemini-1.5-pro' },
    { label: 'Gemini 1.5 Flash', value: 'gemini-1.5-flash' },
    { label: 'Gemini 1.0 Pro', value: 'gemini-1.0-pro' },
  ]},
  { type: 'group', label: '阿里通义千问 (Qwen)', key: 'qwen', options: [
    { label: 'Qwen Max', value: 'qwen-max' },
    { label: 'Qwen Plus', value: 'qwen-plus' },
    { label: 'Qwen Turbo', value: 'qwen-turbo' },
    { label: 'Qwen Long', value: 'qwen-long' },
    { label: 'QwQ (Reasoning)', value: 'qwq-32b' },
  ]},
  { type: 'group', label: '月之暗面 Kimi', key: 'kimi', options: [
    { label: 'Moonshot v1 8K', value: 'moonshot-v1-8k' },
    { label: 'Moonshot v1 32K', value: 'moonshot-v1-32k' },
    { label: 'Moonshot v1 128K', value: 'moonshot-v1-128k' },
  ]},
  { type: 'group', label: '字节豆包 (Doubao)', key: 'doubao', options: [
    { label: 'Doubao Pro 32K', value: 'doubao-pro-32k' },
    { label: 'Doubao Pro 128K', value: 'doubao-pro-128k' },
    { label: 'Doubao Lite 32K', value: 'doubao-lite-32k' },
    { label: 'Doubao Lite 128K', value: 'doubao-lite-128k' },
  ]},
  { type: 'group', label: '百度文心 (ERNIE)', key: 'ernie', options: [
    { label: 'ERNIE 4.0', value: 'ernie-4.0' },
    { label: 'ERNIE 3.5', value: 'ernie-3.5' },
    { label: 'ERNIE Speed', value: 'ernie-speed' },
    { label: 'ERNIE Lite', value: 'ernie-lite' },
  ]},
  { type: 'group', label: '智谱 GLM (Zhipu)', key: 'glm', options: [
    { label: 'GLM-4', value: 'glm-4' },
    { label: 'GLM-4 Plus', value: 'glm-4-plus' },
    { label: 'GLM-4 Air', value: 'glm-4-air' },
    { label: 'GLM-4 Flash', value: 'glm-4-flash' },
  ]},
  { type: 'group', label: 'Meta Llama', key: 'llama', options: [
    { label: 'Llama 3.1 405B', value: 'llama-3.1-405b' },
    { label: 'Llama 3.1 70B', value: 'llama-3.1-70b' },
    { label: 'Llama 3.1 8B', value: 'llama-3.1-8b' },
    { label: 'Llama 3 70B', value: 'llama-3-70b' },
    { label: 'Llama 3 8B', value: 'llama-3-8b' },
  ]},
  { type: 'group', label: 'Mistral AI', key: 'mistral', options: [
    { label: 'Mistral Large', value: 'mistral-large-latest' },
    { label: 'Mistral Small', value: 'mistral-small-latest' },
    { label: 'Mixtral 8x7B', value: 'mixtral-8x7b' },
    { label: 'Mistral Nemo', value: 'mistral-nemo' },
  ]},
  { type: 'group', label: 'Groq', key: 'groq', options: [
    { label: 'Llama 3 (Groq)', value: 'llama3-70b-8192' },
    { label: 'Mixtral (Groq)', value: 'mixtral-8x7b-32768' },
    { label: 'Gemma2 (Groq)', value: 'gemma2-9b-it' },
  ]},
  { type: 'group', label: 'Together AI', key: 'together', options: [
    { label: 'Llama 3.1 (Together)', value: 'meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo' },
    { label: 'Mixtral (Together)', value: 'mistralai/Mixtral-8x22B-Instruct-v0.1' },
  ]},
  { type: 'group', label: 'DeepInfra', key: 'deepinfra', options: [
    { label: 'Llama 3.1 (DeepInfra)', value: 'meta-llama/Meta-Llama-3.1-70B-Instruct' },
    { label: 'Qwen2 (DeepInfra)', value: 'Qwen/Qwen2-72B-Instruct' },
  ]},
  { type: 'group', label: 'Fireworks AI', key: 'fireworks', options: [
    { label: 'Llama 3.1 (Fireworks)', value: 'llama-v3p1-70b-instruct' },
    { label: 'Mixtral (Fireworks)', value: 'mixtral-8x22b-instruct' },
  ]},
  { label: '-- 自定义模型 --', value: '__custom__' },
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
