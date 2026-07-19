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
        <n-grid-item span="2"><n-statistic label="分析模型" :value="getModelLabel(stockStore.analysisResult.model)" /></n-grid-item>
      </n-grid>
      <AnalysisReport :report="stockStore.analysisResult" :klineData="stockStore.klineData" :quote="stockStore.currentQuote" :loading="loading" />
      
    </template>
  </div>
</template>
<script setup lang="ts">
import AnalysisReport from '../components/AnalysisReport.vue';
import { computed, ref } from 'vue';
import { useRoute } from 'vue-router';
import { useStockStore } from '../stores/stock';
import { NAlert, NButton, NCard, NCollapse, NCollapseItem, NGrid, NGridItem, NInput, NInputNumber, NP, NSelect, NSpace, NStatistic, useMessage } from 'naive-ui';

const stockStore = useStockStore();
const message = useMessage();
const route = useRoute();

function detectMarket(sym: string): string {
  var s = sym.trim().toUpperCase();
  if (s.indexOf('.HK') >= 0) return 'HK';
  if (s.indexOf('.US') >= 0) return 'US';
  if (/^\d+$/.test(s)) return 'A';
  return 'US';
}

var querySymbol = route.query.symbol as string | undefined;
var queryMarket = route.query.market as string | undefined;

const symbol = ref(querySymbol || localStorage.getItem('ai_last_symbol') || '');
const market = ref(queryMarket || (symbol.value ? detectMarket(symbol.value) : 'A'));
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

// Auto-fill API base URL on page load
const initModel = aiModel.value;
if (initModel !== '__custom__') {
  const found = modelOptions.find(o => o.value === initModel);
  if (found && found.apiBaseUrl && (!aiBaseUrl.value || !modelOptions.some(m => m.apiBaseUrl === aiBaseUrl.value))) {
    aiBaseUrl.value = found.apiBaseUrl;
    localStorage.setItem('ai_base_url', found.apiBaseUrl);
  }
}

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
const downloadReport = () => {
  var md = stockStore.analysisResult?.report_markdown;
  if (!md) { message.warning('暂无分析报告可下载'); return; }
  var symbol = stockStore.analysisResult.symbol;
  var date = stockStore.analysisResult.data_timestamp.slice(0, 10);
  var filename = '分析报告_' + symbol + '_' + date + '.md';
  downloadViaForm(md, filename, 'text/markdown;charset=utf-8');
  message.success('下载完成');
}

const downloadHtml = () => {
  var md = stockStore.analysisResult?.report_markdown;
  if (!md) { message.warning('暂无分析报告可下载'); return; }
  var symbol = stockStore.analysisResult.symbol;
  var date = stockStore.analysisResult.data_timestamp.slice(0, 10);
  var filename = '分析报告_' + symbol + '_' + date + '.html';
  var htmlBody = md
    .replace(/### (.+)/g, '<h3>$1</h3>')
    .replace(/## (.+)/g, '<h2>$1</h2>')
    .replace(/# (.+)/g, '<h1>$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/\n/g, '<br/>');
  var fullHtml = '<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>' + symbol + ' 分析报告<\/title>\n<style>\nbody{font-family:-apple-system,BlinkMacSystemFont,sans-serif;max-width:800px;margin:20px auto;padding:20px;line-height:1.8;color:#333;font-size:15px}\nh1{color:#111;border-bottom:2px solid #1890ff;padding-bottom:8px;font-size:22px}\nh2{color:#222;border-bottom:1px solid #e8e8e8;padding-bottom:6px;margin-top:24px}\nh3{color:#333;border-left:3px solid #1890ff;padding-left:10px;margin-top:20px}\nstrong{color:#1890ff}\nli{margin-left:20px;margin-bottom:4px}\n<\/style>\n<\/head>\n<body>\n' + htmlBody + '\n</body>\n</html>';
  downloadViaForm(fullHtml, filename, 'text/html;charset=utf-8');
  message.success('下载完成');
}

function downloadViaForm(content, filename, contentType) {
  const blob = new Blob([content], { type: contentType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}




async function doAnalysis(): Promise<void> {
  if (!symbol.value.trim()) { message.warning('请输入股票代码'); return; }
  loading.value = true; errorMessage.value = ''; localStorage.setItem('ai_last_symbol', symbol.value);
  try {
    await stockStore.analyze(symbol.value, market.value, lookbackDays.value, aiModel.value === '__custom__' ? aiCustom.value || undefined : aiModel.value || undefined, aiBaseUrl.value || undefined, aiApiKey.value || undefined);
    if (stockStore.error) errorMessage.value = stockStore.error;
    // Fetch real kline data so the chart renders with actual market data
    if (!errorMessage.value) {
      const end = new Date();
      const start = new Date();
      start.setDate(start.getDate() - lookbackDays.value);
      const fmt = (d: Date) => d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
      await stockStore.fetchKline(symbol.value, market.value, fmt(start), fmt(end));
    }
  }
  catch (err: unknown) { errorMessage.value = err instanceof Error ? err.message : String(err); }
  finally { loading.value = false; }
}
</script>
