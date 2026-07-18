<template>
  <div>
    <div class="page-header flex-between">
      <div>
        <h2>AI 分析</h2>
        <p>基于技术指标、财务数据和模型生成股票分析报告</p>
      </div>
    </div>

    <n-card size="small" class="mb-24">
      <n-grid :cols="4" :x-gap="16" :y-gap="12">
        <n-grid-item>
          <n-input v-model:value="symbol" placeholder="股票代码" clearable />
        </n-grid-item>
        <n-grid-item>
          <n-select v-model:value="market" :options="marketOptions" />
        </n-grid-item>
        <n-grid-item>
          <n-input-number v-model:value="lookbackDays" :min="20" :max="1000" placeholder="回溯天数" />
        </n-grid-item>
        <n-grid-item>
          <n-space>
            <n-button type="primary" :loading="loading" @click="doAnalysis">开始分析</n-button>
            <n-button ghost :disabled="!stockStore.analysisResult" @click="downloadReport">下载 MD</n-button>
            <n-button ghost :disabled="!stockStore.analysisResult" @click="downloadHtml">下载 HTML</n-button>
          </n-space>
        </n-grid-item>
      </n-grid>

      <n-collapse class="mt-12">
        <n-collapse-item title="AI 模型配置" name="ai">
          <n-grid :cols="3" :x-gap="12" :y-gap="12">
            <n-grid-item>
              <n-select
                v-model:value="aiModel"
                :options="modelOptions"
                :filterable="true"
                placeholder="选择模型"
                size="small"
                @update:value="onModelChange"
              />
              <n-input
                v-if="aiModel === '__custom__'"
                v-model:value="aiCustom"
                class="mt-6"
                placeholder="输入自定义模型名"
                size="small"
              />
            </n-grid-item>
            <n-grid-item>
              <n-input v-model:value="aiBaseUrl" placeholder="API 地址，如 https://api.openai.com/v1" size="small" />
            </n-grid-item>
            <n-grid-item>
              <n-input v-model:value="aiApiKey" type="password" placeholder="API Key" show-password-on="click" size="small" />
            </n-grid-item>
          </n-grid>
          <n-p depth="3" class="mt-6" style="font-size: 12px">
            {{ modelHint }}
          </n-p>
          <n-space justify="end" class="mt-6">
            <n-button size="tiny" quaternary @click="clearConfig">清除本地配置</n-button>
          </n-space>
        </n-collapse-item>
      </n-collapse>
    </n-card>

    <n-alert v-if="errorMessage" type="error" class="mb-24" title="分析失败">
      {{ errorMessage }}
    </n-alert>

    <template v-if="stockStore.analysisResult">
      <n-grid :cols="3" :x-gap="16" :y-gap="12" class="mb-24">
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
      <AnalysisReport :report="stockStore.analysisResult.report_markdown" :loading="loading" />
    </template>

    <n-empty v-else-if="!loading" description="输入股票代码并点击开始分析" style="margin-top: 60px" />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { NAlert, NButton, NCard, NCollapse, NCollapseItem, NEmpty, NGrid, NGridItem, NInput, NInputNumber, NP, NSelect, NSpace, NStatistic, useMessage } from 'naive-ui';
import TechnicalIndicators from '../components/TechnicalIndicators.vue';
import AnalysisReport from '../components/AnalysisReport.vue';
import { useStockStore } from '../stores/stock';

type MarketValue = 'A' | 'HK' | 'US';

const route = useRoute();
const message = useMessage();
const stockStore = useStockStore();

const symbol = ref(String(route.query.symbol || '000001'));
const market = ref<MarketValue>('A');
const lookbackDays = ref(120);
const aiModel = ref(localStorage.getItem('ai_model') || '');
const aiBaseUrl = ref(localStorage.getItem('ai_base_url') || '');
const aiApiKey = ref(localStorage.getItem('ai_api_key') || '');
const aiCustom = ref(localStorage.getItem('ai_custom') || '');
const loading = ref(false);
const klineData = ref<any[]>([]);

const marketOptions = [
  { label: 'A股', value: 'A' },
  { label: '港股', value: 'HK' },
  { label: '美股', value: 'US' },
];

const modelOptions = [
  { label: 'DeepSeek Chat', value: 'deepseek-chat' },
  { label: 'DeepSeek Reasoner', value: 'deepseek-reasoner' },
  { label: 'GPT-4.1', value: 'gpt-4.1' },
  { label: 'GPT-4o', value: 'gpt-4o' },
  { label: 'Claude Sonnet 4', value: 'claude-sonnet-4-20250514' },
  { label: 'Gemini 2.5 Flash', value: 'gemini-2.5-flash-preview-04-17' },
  { label: 'Qwen3', value: 'qwen3' },
  { label: 'Kimi K2', value: 'kimi-k2' },
  { label: '自定义模型', value: '__custom__' },
];

const providerUrls: Record<string, string> = {
  deepseek: 'https://api.deepseek.com/v1',
  openai: 'https://api.openai.com/v1',
  claude: 'https://api.anthropic.com/v1',
  gemini: 'https://generativelanguage.googleapis.com/v1beta',
  qwen: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
  kimi: 'https://api.moonshot.cn/v1',
};

const errorMessage = computed(() => stockStore.error);

const modelHint = computed(() => {
  if (aiModel.value && aiModel.value !== '__custom__') {
    const url = getProviderUrl(aiModel.value);
    return url ? `默认 API 地址: ${url}` : '';
  }
  return '选择模型后可自动填充默认 API 地址';
});

watch(aiModel, (val) => {
  if (val && val !== '__custom__') {
    const url = getProviderUrl(val);
    if (url) aiBaseUrl.value = url;
  }
});

function getProviderKey(val: string): string | null {
  if (val.startsWith('deepseek')) return 'deepseek';
  if (val.startsWith('gpt-') || val === 'o1' || val === 'o1-mini' || val === 'o3' || val === 'o3-mini' || val === 'o4-mini') return 'openai';
  if (val.startsWith('claude')) return 'claude';
  if (val.startsWith('gemini')) return 'gemini';
  if (val.startsWith('qwen') || val.startsWith('qwq')) return 'qwen';
  if (val.startsWith('kimi') || val.startsWith('moonshot')) return 'kimi';
  return null;
}

function getProviderUrl(val: string): string {
  const key = getProviderKey(val);
  return key ? providerUrls[key] || '' : '';
}

async function doAnalysis() {
  const cleanSymbol = symbol.value.trim();
  const selectedModel = aiModel.value === '__custom__' ? aiCustom.value.trim() : aiModel.value.trim();

  if (!cleanSymbol) {
    message.warning('请输入股票代码');
    return;
  }
  if (!selectedModel || !aiBaseUrl.value.trim() || !aiApiKey.value.trim()) {
    message.warning('请先填写模型名、API 地址和 API Key');
    return;
  }

  localStorage.setItem('ai_model', aiModel.value);
  localStorage.setItem('ai_base_url', aiBaseUrl.value);
  localStorage.setItem('ai_api_key', aiApiKey.value);
  localStorage.setItem('ai_custom', aiCustom.value);

  loading.value = true;
  try {
    await stockStore.analyze(cleanSymbol, market.value, lookbackDays.value, selectedModel, aiBaseUrl.value.trim(), aiApiKey.value.trim());
    await stockStore.fetchKline(cleanSymbol, market.value);
    klineData.value = stockStore.klineData;
    if (stockStore.error) {
      message.error(stockStore.error);
    } else {
      message.success('分析完成');
    }
  } finally {
    loading.value = false;
  }
}

function downloadReport() {
  const report = stockStore.analysisResult?.report_markdown;
  if (!report) return;
  const blob = new Blob([report], { type: 'text/markdown;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = `analysis_${symbol.value}_${market.value}_${lookbackDays.value}d.md`;
  anchor.click();
  URL.revokeObjectURL(url);
}

function downloadHtml() {
  const md = stockStore.analysisResult?.report_markdown;
  if (!md) return;

  const html = md
    .replace(/### (.+)/g, '<h3>$1</h3>')
    .replace(/## (.+)/g, '<h2>$1</h2>')
    .replace(/# (.+)/g, '<h1>$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br/>')
    .replace(/- (.+)/g, '<li>$1</li>');

  const doc = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>AI 分析报告 - ${symbol.value}</title>
  <style>
    body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;max-width:900px;margin:0 auto;padding:24px;line-height:1.8;color:#222}
    h1{border-bottom:2px solid #2080f0;padding-bottom:8px}
    h2{margin-top:24px}
    h3{margin-top:16px}
    .header{text-align:center;margin-bottom:24px}
    .footer{text-align:center;margin-top:40px;padding-top:16px;border-top:1px solid #eee;color:#888;font-size:12px}
  </style>
</head>
<body>
  <div class="header">
    <h1>AI 股票分析报告</h1>
    <div>股票: ${symbol.value} | 市场: ${market.value} | 回溯: ${lookbackDays.value} 天 | 生成时间: ${new Date().toLocaleString()}</div>
  </div>
  <div class="content">${html}</div>
  <div class="footer">由 AlphaQuant AI 生成 | 仅供参考，不构成投资建议</div>
</body>
</html>`;

  const blob = new Blob([doc], { type: 'text/html;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = `analysis_${symbol.value}_${market.value}_${lookbackDays.value}d.html`;
  anchor.click();
  URL.revokeObjectURL(url);
}

function clearConfig() {
  localStorage.removeItem('ai_model');
  localStorage.removeItem('ai_base_url');
  localStorage.removeItem('ai_api_key');
  localStorage.removeItem('ai_custom');
  aiModel.value = '';
  aiBaseUrl.value = '';
  aiApiKey.value = '';
  aiCustom.value = '';
  message.success('已清除本地 AI 配置');
}

function onModelChange(v: string) {
  if (v === '__custom__') {
    aiCustom.value = '';
    return;
  }
  aiCustom.value = '';
  const url = getProviderUrl(v);
  if (url) aiBaseUrl.value = url;
}
</script>
