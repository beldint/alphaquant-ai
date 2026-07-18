<template>
  <div>
    <div class="page-header flex-between">
      <div><h2>AI 分析</h2><p>基于技术指标、财务数据和模型生成股票分析报告</p></div>
    </div>
    <n-card size="small" class="mb-24">
      <n-grid :cols="2" :x-gap="12" :y-gap="12" responsive="screen">
        <n-grid-item><n-input v-model:value="symbol" placeholder="股票代码" clearable /></n-grid-item>
        <n-grid-item><n-select v-model:value="market" :options="marketOptions" /></n-grid-item>
        <n-grid-item><n-input-number v-model:value="lookbackDays" :min="20" :max="1000" placeholder="回溯天数" style="width:100%" /></n-grid-item>
        <n-grid-item><n-space wrap><n-button type="primary" :loading="loading" @click="doAnalysis">开始分析</n-button><n-button ghost :disabled="!stockStore.analysisResult" @click="downloadReport">下载 MD</n-button><n-button ghost :disabled="!stockStore.analysisResult" @click="downloadHtml">下载 HTML</n-button></n-space></n-grid-item>
      </n-grid>
      <n-collapse class="mt-12">
        <n-collapse-item title="AI 模型配置" name="ai">
          <n-grid :cols="1" :x-gap="12" :y-gap="12" responsive="screen">
            <n-grid-item>
              <n-select v-model:value="aiModel" :options="modelOptions" :filterable="true" placeholder="选择模型" size="small" @update:value="onModelChange" />
              <n-input v-if="aiModel === '__custom__'" v-model:value="aiCustom" class="mt-6" placeholder="输入自定义模型名" size="small" />
            </n-grid-item>
            <n-grid-item><n-input v-model:value="aiBaseUrl" placeholder="API 地址" size="small" /></n-grid-item>
            <n-grid-item><n-input v-model:value="aiApiKey" type="password" placeholder="API Key" show-password-on="click" size="small" /></n-grid-item>
          </n-grid>
          <n-p depth="3" class="mt-6" style="font-size: 12px">{{ modelHint }}</n-p>
          <n-space justify="end" class="mt-6"><n-button size="tiny" quaternary @click="clearConfig">清除本地配置</n-button></n-space>
        </n-collapse-item>
      </n-collapse>
    </n-card>
    <n-alert v-if="errorMessage" type="error" class="mb-24" title="分析失败">{{ errorMessage }}</n-alert>
    <template v-if="stockStore.analysisResult">
      <n-grid :cols="2" :x-gap="12" :y-gap="12" class="mb-24" responsive="screen">
        <n-grid-item><n-statistic label="股票代码" :value="stockStore.analysisResult.symbol" /></n-grid-item>
        <n-grid-item><n-statistic label="数据时间" :value="stockStore.analysisResult.data_timestamp.slice(0, 10)" /></n-grid-item>
        <n-grid-item span="2"><n-statistic label="分析模型" :value="stockStore.analysisResult.model" /></n-grid-item>
      </n-grid>
      
    </template>
  </div>
</template>
<script setup lang="ts">
import { computed, ref } from 'vue';
import { useStockStore } from '../stores/stock';
import { NAlert, NButton, NCard, NCollapse, NCollapseItem, NGrid, NGridItem, NInput, NInputNumber, NP, NSelect, NSpace, NStatistic, useMessage } from 'naive-ui';

const stockStore = useStockStore();
const message = useMessage();
const symbol = ref(localStorage.getItem('ai_last_symbol') || '');
const market = ref('A');
const lookbackDays = ref(120);
const aiModel = ref(localStorage.getItem('ai_model') || 'deepseek-chat');
const aiCustom = ref(localStorage.getItem('ai_custom') || '');
const aiBaseUrl = ref(localStorage.getItem('ai_base_url') || '');
const aiApiKey = ref(localStorage.getItem('ai_api_key') || '');
const loading = ref(false);
const errorMessage = ref('');
const marketOptions = [{ label: 'A股', value: 'A' }, { label: '港股', value: 'HK' }, { label: '美股', value: 'US' }];
const modelOptions = [
  { label: 'DeepSeek Chat', value: 'deepseek-chat', apiBaseUrl: 'https://api.deepseek.com' },
  { label: 'DeepSeek Reasoner', value: 'deepseek-reasoner', apiBaseUrl: 'https://api.deepseek.com' },
  { label: 'GPT-4o', value: 'gpt-4o', apiBaseUrl: 'https://api.openai.com' },
  { label: 'GPT-4o-mini', value: 'gpt-4o-mini', apiBaseUrl: 'https://api.openai.com' },
  { label: 'GPT-4.1', value: 'gpt-4.1', apiBaseUrl: 'https://api.openai.com' },
  { label: 'GPT-4.1-mini', value: 'gpt-4.1-mini', apiBaseUrl: 'https://api.openai.com' },
  { label: 'GPT-4.1-nano', value: 'gpt-4.1-nano', apiBaseUrl: 'https://api.openai.com' },
  { label: 'Claude 3.5 Sonnet', value: 'claude-3-5-sonnet-20241022', apiBaseUrl: 'https://api.anthropic.com' },
  { label: 'Claude 3.5 Haiku', value: 'claude-3-5-haiku-20241022', apiBaseUrl: 'https://api.anthropic.com' },
  { label: 'Gemini 2.0 Flash', value: 'gemini-2.0-flash', apiBaseUrl: 'https://generativelanguage.googleapis.com' },
  { label: 'Qwen Turbo', value: 'qwen-turbo', apiBaseUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1' },
  { label: 'Qwen Plus', value: 'qwen-plus', apiBaseUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1' },
  { label: 'Moonshot v1', value: 'moonshot-v1-8k', apiBaseUrl: 'https://api.moonshot.cn' },
  { label: '自定义', value: '__custom__', apiBaseUrl: '' },
];
const modelHint = computed(() => {
  if (aiCustom.value && aiModel.value === '__custom__') return '当前：' + aiCustom.value;
  const found = modelOptions.find(o => o.value === aiModel.value);
  return found && found.value !== '__custom__' ? '当前：' + found.label : '';
});
function onModelChange(value: string): void {
  if (value !== '__custom__') {
    aiCustom.value = '';
    localStorage.setItem('ai_model', value);
    const found = modelOptions.find(o => o.value === value);
    if (found && found.apiBaseUrl) {
      aiBaseUrl.value = found.apiBaseUrl;
      localStorage.setItem('ai_base_url', found.apiBaseUrl);
    }
  } else {
    aiBaseUrl.value = '';
    localStorage.removeItem('ai_base_url');
  }
}
function clearConfig(): void { aiModel.value = 'deepseek-chat'; aiCustom.value = ''; aiBaseUrl.value = ''; aiApiKey.value = ''; localStorage.removeItem('ai_model'); localStorage.removeItem('ai_custom'); localStorage.removeItem('ai_base_url'); localStorage.removeItem('ai_api_key'); message.success('已清除 AI 配置'); }
function downloadReport(): void {}
function downloadHtml(): void {}
async function doAnalysis(): Promise<void> {
  if (!symbol.value.trim()) { message.warning('请输入股票代码'); return; }
  loading.value = true; errorMessage.value = ''; localStorage.setItem('ai_last_symbol', symbol.value);
  try { await stockStore.analyze(symbol.value, market.value, lookbackDays.value, aiModel.value === '__custom__' ? aiCustom.value || undefined : aiModel.value || undefined, aiBaseUrl.value || undefined, aiApiKey.value || undefined); if (stockStore.error) errorMessage.value = stockStore.error; }
  catch (err: unknown) { errorMessage.value = err instanceof Error ? err.message : String(err); }
  finally { loading.value = false; }
}
</script>