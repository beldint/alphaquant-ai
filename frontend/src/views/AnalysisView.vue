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
      <n-collapse class="mt-12">
        <n-collapse-item title="AI 模型配置" name="ai">
          <n-grid :cols="3" :x-gap="12">
            <n-grid-item>
              <n-select v-model:value="aiModel" :options="modelOptions" placeholder="选择模型" size="small"
                :filterable="true" @update:value="onModelChange" />
              <n-input v-if="aiModel === '__custom__'" v-model:value="aiCustom" placeholder="输入自定义模型名" size="small" class="mt-6" />
            </n-grid-item>
            <n-grid-item><n-input v-model:value="aiBaseUrl" placeholder="API 地址 (如 http://localhost:11434/v1)" size="small" /></n-grid-item>
            <n-grid-item><n-input v-model:value="aiApiKey" type="password" placeholder="API Key" show-password-on="click" size="small" /></n-grid-item>
          </n-grid>
          <n-p depth="3" class="mt-6" style="font-size:12px">
{{ aiModel && aiModel !== '__custom__' ? (getProviderUrl(aiModel) ? '默认 API 地址: ' + getProviderUrl(aiModel) : '') : '选择模型后自动填入默认 API 地址' }}
          </n-p>
          <n-space justify="end" class="mt-6">
            <n-button size="tiny" quaternary @click="clearConfig">清除所有本地数据</n-button>
          </n-space>
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
import { ref, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useStockStore } from '../stores/stock';
import TechnicalIndicators from '../components/TechnicalIndicators.vue';
import AnalysisReport from '../components/AnalysisReport.vue';
import { NCollapse, NCollapseItem, NSelect, NP, useMessage } from 'naive-ui';
const route = useRoute();
const message = useMessage();
const stockStore = useStockStore();
const symbol = ref(route.query.symbol as string || '000001');
const market = ref('A');
const lookbackDays = ref(120);
const aiModel = ref(localStorage.getItem('ai_model') || '');
const aiBaseUrl = ref(localStorage.getItem('ai_base_url') || '');
const aiApiKey = ref(localStorage.getItem('ai_api_key') || '');
const aiCustom = ref('');
const modelOptions = [
  { type: 'group', label: 'DeepSeek', key: 'deepseek', children: [
    { label: 'DeepSeek V3 (最新)', value: 'deepseek-chat' },
    { label: 'DeepSeek R1 (最新)', value: 'deepseek-reasoner' },
    { label: 'DeepSeek R1-0528', value: 'deepseek-r1-0528' },
    { label: 'DeepSeek V3-0324', value: 'deepseek-v3-0324' },
  ]},
  { type: 'group', label: 'OpenAI', key: 'openai', children: [
    { label: 'GPT-4.1 (最新)', value: 'gpt-4.1' },
    { label: 'GPT-4.1 mini (最新)', value: 'gpt-4.1-mini' },
    { label: 'GPT-4.1 nano (最新)', value: 'gpt-4.1-nano' },
    { label: 'GPT-5 (最新)', value: 'gpt-5' },
    { label: 'GPT-5 mini (最新)', value: 'gpt-5-mini' },
    { label: 'GPT-4o', value: 'gpt-4o' },
    { label: 'GPT-4o mini', value: 'gpt-4o-mini' },
    { label: 'o3', value: 'o3' },
    { label: 'o3-mini', value: 'o3-mini' },
    { label: 'o4-mini', value: 'o4-mini' },
    { label: 'o1', value: 'o1' },
    { label: 'o1-mini', value: 'o1-mini' },
    { label: 'GPT-4 Turbo', value: 'gpt-4-turbo' },
    { label: 'GPT-4', value: 'gpt-4' },
    { label: 'GPT-3.5 Turbo', value: 'gpt-3.5-turbo' },
  ]},
  { type: 'group', label: 'Anthropic Claude', key: 'claude', children: [
    { label: 'Claude Sonnet 4.5 (最新)', value: 'claude-sonnet-4-20250630' },
    { label: 'Claude Sonnet 4', value: 'claude-sonnet-4-20250514' },
    { label: 'Claude Opus 4.5 (最新)', value: 'claude-opus-4-20250630' },
    { label: 'Claude Opus 4', value: 'claude-opus-4-20250514' },
    { label: 'Claude 3.5 Sonnet v2', value: 'claude-3-5-sonnet-v2@20241022' },
    { label: 'Claude 3.5 Haiku', value: 'claude-3-5-haiku-20241022' },
    { label: 'Claude 3 Opus', value: 'claude-3-opus-20240229' },
    { label: 'Claude 3 Sonnet', value: 'claude-3-sonnet-20240229' },
    { label: 'Claude 3 Haiku', value: 'claude-3-haiku-20240307' },
  ]},
  { type: 'group', label: 'Google Gemini', key: 'gemini', children: [
    { label: 'Gemini 2.5 Pro (最新)', value: 'gemini-2.5-pro-exp-03-25' },
    { label: 'Gemini 2.5 Flash (最新)', value: 'gemini-2.5-flash-preview-04-17' },
    { label: 'Gemini 2.0 Flash', value: 'gemini-2.0-flash' },
    { label: 'Gemini 1.5 Pro', value: 'gemini-1.5-pro' },
    { label: 'Gemini 1.5 Flash', value: 'gemini-1.5-flash' },
    { label: 'Gemini 1.0 Pro', value: 'gemini-1.0-pro' },
  ]},
  { type: 'group', label: '阿里通义千问 (Qwen)', key: 'qwen', children: [
    { label: 'Qwen3 Max (最新)', value: 'qwen3-max' },
    { label: 'Qwen3 (最新)', value: 'qwen3' },
    { label: 'Qwen3 Plus', value: 'qwen3-plus' },
    { label: 'QwQ (推理模型)', value: 'qwq-32b' },
    { label: 'Qwen Max', value: 'qwen-max' },
    { label: 'Qwen Plus', value: 'qwen-plus' },
    { label: 'Qwen Turbo', value: 'qwen-turbo' },
    { label: 'Qwen Long', value: 'qwen-long' },
  ]},
  { type: 'group', label: '月之暗面 Kimi', key: 'kimi', children: [
    { label: 'Kimi k3 (最新)', value: 'kimi-k3' },
    { label: 'Kimi k2', value: 'kimi-k2' },
    { label: 'Moonshot v1 8K', value: 'moonshot-v1-8k' },
    { label: 'Moonshot v1 32K', value: 'moonshot-v1-32k' },
    { label: 'Moonshot v1 128K', value: 'moonshot-v1-128k' },
  ]},
  { type: 'group', label: '字节豆包 (Doubao)', key: 'doubao', children: [
    { label: 'Doubao Pro 32K', value: 'doubao-pro-32k' },
    { label: 'Doubao Pro 128K', value: 'doubao-pro-128k' },
    { label: 'Doubao Lite 32K', value: 'doubao-lite-32k' },
    { label: 'Doubao Lite 128K', value: 'doubao-lite-128k' },
  ]},
  { type: 'group', label: '百度文心 (ERNIE)', key: 'ernie', children: [
    { label: 'ERNIE 4.5 Turbo (最新)', value: 'ernie-4.5-turbo' },
    { label: 'ERNIE 4.0', value: 'ernie-4.0' },
    { label: 'ERNIE 3.5', value: 'ernie-3.5' },
    { label: 'ERNIE Speed', value: 'ernie-speed' },
    { label: 'ERNIE Lite', value: 'ernie-lite' },
  ]},
  { type: 'group', label: '智谱 GLM (Zhipu)', key: 'glm', children: [
    { label: 'GLM-4 (最新)', value: 'glm-4' },
    { label: 'GLM-4 Plus', value: 'glm-4-plus' },
    { label: 'GLM-4 Air', value: 'glm-4-air' },
    { label: 'GLM-4 Flash', value: 'glm-4-flash' },
    { label: 'GLM-4V (视觉)', value: 'glm-4v' },
    { label: 'CodeGeeX', value: 'codegeex-4' },
  ]},
  { type: 'group', label: '零一万物 Yi', key: 'yi', children: [
    { label: 'Yi Lightning (最新)', value: 'yi-lightning' },
    { label: 'Yi Large', value: 'yi-large' },
    { label: 'Yi Medium', value: 'yi-medium' },
    { label: 'Yi Spark', value: 'yi-spark' },
  ]},
  { type: 'group', label: '百川智能 (Baichuan)', key: 'baichuan', children: [
    { label: 'Baichuan 4 (最新)', value: 'baichuan4' },
    { label: 'Baichuan 3 Turbo', value: 'baichuan3-turbo' },
  ]},
  { type: 'group', label: 'MiniMax', key: 'minimax', children: [
    { label: 'MiniMax T1 (最新)', value: 'minimax-t1' },
    { label: 'MiniMax 01', value: 'minimax-01' },
  ]},
  { type: 'group', label: 'Meta Llama', key: 'llama', children: [
    { label: 'Llama 4 (最新)', value: 'llama-4' },
    { label: 'Llama 3.1 405B', value: 'llama-3.1-405b' },
    { label: 'Llama 3.1 70B', value: 'llama-3.1-70b' },
    { label: 'Llama 3.1 8B', value: 'llama-3.1-8b' },
    { label: 'Llama 3 70B', value: 'llama-3-70b' },
    { label: 'Llama 3 8B', value: 'llama-3-8b' },
  ]},
  { type: 'group', label: 'Mistral AI', key: 'mistral', children: [
    { label: 'Mistral Large (最新)', value: 'mistral-large-2506' },
    { label: 'Mistral Small (最新)', value: 'mistral-small-2506' },
    { label: 'Mixtral 8x22B', value: 'mixtral-8x22b' },
    { label: 'Mixtral 8x7B', value: 'mixtral-8x7b' },
    { label: 'Mistral Nemo', value: 'mistral-nemo' },
  ]},
  { type: 'group', label: 'Groq Cloud', key: 'groq', children: [
    { label: 'Llama 3.1 (Groq)', value: 'llama-3.1-70b-versatile' },
    { label: 'Llama 3 (Groq)', value: 'llama3-70b-8192' },
    { label: 'Mixtral (Groq)', value: 'mixtral-8x7b-32768' },
    { label: 'Gemma 2 (Groq)', value: 'gemma2-9b-it' },
    { label: 'DeepSeek (Groq)', value: 'deepseek-r1-distill-llama-70b' },
  ]},
  { type: 'group', label: 'Together AI', key: 'together', children: [
    { label: 'Llama 3.1 (Together)', value: 'meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo' },
    { label: 'Llama 3 (Together)', value: 'meta-llama/Llama-3-70b-chat-hf' },
    { label: 'Mixtral (Together)', value: 'mistralai/Mixtral-8x22B-Instruct-v0.1' },
    { label: 'Qwen 2.5 (Together)', value: 'Qwen/Qwen2.5-72B-Instruct-Turbo' },
    { label: 'DeepSeek (Together)', value: 'deepseek-ai/DeepSeek-R1' },
  ]},
  { type: 'group', label: 'DeepInfra', key: 'deepinfra', children: [
    { label: 'Llama 3.1 (DeepInfra)', value: 'meta-llama/Meta-Llama-3.1-70B-Instruct' },
    { label: 'Qwen 2.5 (DeepInfra)', value: 'Qwen/Qwen2.5-72B-Instruct' },
  ]},
  { type: 'group', label: 'Fireworks AI', key: 'fireworks', children: [
    { label: 'Llama 3.1 (Fireworks)', value: 'accounts/fireworks/models/llama-v3p1-70b-instruct' },
    { label: 'Mixtral (Fireworks)', value: 'accounts/fireworks/models/mixtral-8x22b-instruct' },
    { label: 'DeepSeek (Fireworks)', value: 'accounts/fireworks/models/deepseek-r1' },
  ]},
  { type: 'group', label: 'Reka AI', key: 'reka', children: [
    { label: 'Reka Core (最新)', value: 'reka-core' },
    { label: 'Reka Flash', value: 'reka-flash' },
  ]},
  { type: 'group', label: '🏠 Ollama (本地)', key: 'ollama', children: [
    { label: 'Llama 3.1 (Ollama)', value: 'llama3.1' },
    { label: 'Llama 3 (Ollama)', value: 'llama3' },
    { label: 'Qwen 2.5 (Ollama)', value: 'qwen2.5' },
    { label: 'Qwen 2 (Ollama)', value: 'qwen2' },
    { label: 'DeepSeek R1 (Ollama)', value: 'deepseek-r1:7b' },
    { label: 'DeepSeek V3 (Ollama)', value: 'deepseek-v3' },
    { label: 'Mistral (Ollama)', value: 'mistral' },
    { label: 'Gemma 2 (Ollama)', value: 'gemma2' },
    { label: 'Phi-3 (Ollama)', value: 'phi3' },
    { label: 'Yi (Ollama)', value: 'yi' },
    { label: 'GLM-4 (Ollama)', value: 'glm4' },
    { label: 'CodeGemma (Ollama)', value: 'codegemma' },
  ]},
  { type: 'group', label: '🏠 vLLM (本地)', key: 'vllm', children: [
    { label: 'vLLM 已部署模型', value: 'vllm-default' },
  ]},
  { type: 'group', label: '🏠 LM Studio (本地)', key: 'lmstudio', children: [
    { label: 'LM Studio 已加载模型', value: 'lm-studio-default' },
  ]},
  { type: 'group', label: '🏠 LocalAI (本地)', key: 'localai', children: [
    { label: 'LocalAI 默认', value: 'localai-default' },
  ]},
  { type: 'group', label: '🏠 llama.cpp (本地)', key: 'llamacpp', children: [
    { label: 'llama.cpp 服务', value: 'llama-cpp-default' },
  ]},
  { label: '-- 自定义模型 --', value: '__custom__' },
];

const providerUrls: Record<string, string> = {
  deepseek: 'https://api.deepseek.com/v1',
  openai: 'https://api.openai.com/v1',
  claude: 'https://api.anthropic.com/v1',
  gemini: 'https://generativelanguage.googleapis.com/v1beta',
  qwen: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
  kimi: 'https://api.moonshot.cn/v1',
  doubao: 'https://ark.cn-beijing.volces.com/api/v3',
  ernie: 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat',
  glm: 'https://open.bigmodel.cn/api/paas/v4',
  yi: 'https://api.lingyiwanwu.com/v1',
  baichuan: 'https://api.baichuan-ai.com/v1',
  minimax: 'https://api.minimax.chat/v1',
  ollama: 'http://localhost:11434/v1',
  vllm: 'http://localhost:8000/v1',
  lmstudio: 'http://localhost:1234/v1',
  localai: 'http://localhost:8080/v1',
  llamacpp: 'http://localhost:8080/v1',
  oobabooga: 'http://localhost:5000/v1',
  xinference: 'http://localhost:9997/v1',
  jan: 'http://localhost:1337/v1',
  groq: 'https://api.groq.com/openai/v1',
  together: 'https://api.together.xyz/v1',
  deepinfra: 'https://api.deepinfra.com/v1/openai',
  fireworks: 'https://api.fireworks.ai/inference/v1',
  reka: 'https://api.reka.ai/v1',
  mistral: 'https://api.mistral.ai/v1',
  llama: '',
};
watch(aiModel, function(val) {
  if (val && val !== '__custom__') {
    if (val.indexOf('deepseek') >= 0) aiBaseUrl.value = 'https://api.deepseek.com/v1';
    else if (val.indexOf('gpt-') >= 0 || val.indexOf('o1') >= 0 || val.indexOf('o3') >= 0 || val.indexOf('o4') >= 0) aiBaseUrl.value = 'https://api.openai.com/v1';
    else if (val.indexOf('claude') >= 0) aiBaseUrl.value = 'https://api.anthropic.com/v1';
    else if (val.indexOf('gemini') >= 0) aiBaseUrl.value = 'https://generativelanguage.googleapis.com/v1beta';
    else if (val.indexOf('qwen') >= 0 || val.indexOf('qwq') >= 0) aiBaseUrl.value = 'https://dashscope.aliyuncs.com/compatible-mode/v1';
    else if (val.indexOf('moonshot') >= 0 || val.indexOf('kimi') >= 0) aiBaseUrl.value = 'https://api.moonshot.cn/v1';
    else if (val.indexOf('doubao') >= 0) aiBaseUrl.value = 'https://ark.cn-beijing.volces.com/api/v3';
    else if (val.indexOf('ernie') >= 0) aiBaseUrl.value = 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat';
    else if (val.indexOf('glm') >= 0 || val.indexOf('codegeex') >= 0) aiBaseUrl.value = 'https://open.bigmodel.cn/api/paas/v4';
    else if (val.indexOf('yi-') >= 0) aiBaseUrl.value = 'https://api.lingyiwanwu.com/v1';
    else if (val.indexOf('baichuan') >= 0) aiBaseUrl.value = 'https://api.baichuan-ai.com/v1';
    else if (val.indexOf('minimax') >= 0) aiBaseUrl.value = 'https://api.minimax.chat/v1';
    else if (val.indexOf('mistral') >= 0 || val.indexOf('mixtral') >= 0) aiBaseUrl.value = 'https://api.mistral.ai/v1';
    else if (val.indexOf('groq') >= 0) aiBaseUrl.value = 'https://api.groq.com/openai/v1';
    else if (val.indexOf('together') >= 0) aiBaseUrl.value = 'https://api.together.xyz/v1';
    else if (val.indexOf('deepinfra') >= 0) aiBaseUrl.value = 'https://api.deepinfra.com/v1/openai';
    else if (val.indexOf('fireworks') >= 0) aiBaseUrl.value = 'https://api.fireworks.ai/inference/v1';
    else if (val.indexOf('reka') >= 0) aiBaseUrl.value = 'https://api.reka.ai/v1';
    else if (val.indexOf('vllm') >= 0) aiBaseUrl.value = 'http://localhost:8000/v1';
    else if (val.indexOf('lm-studio') >= 0) aiBaseUrl.value = 'http://localhost:1234/v1';
    else if (val.indexOf('localai') >= 0 || val.indexOf('llama-cpp') >= 0) aiBaseUrl.value = 'http://localhost:8080/v1';
    else if (val.indexOf('oobabooga') >= 0) aiBaseUrl.value = 'http://localhost:5000/v1';
    else if (val.indexOf('xinference') >= 0) aiBaseUrl.value = 'http://localhost:9997/v1';
    else if (val.indexOf('jan-') >= 0) aiBaseUrl.value = 'http://localhost:1337/v1';
    else if (val.indexOf('llama') >= 0) aiBaseUrl.value = '';
    else aiBaseUrl.value = 'http://localhost:11434/v1';
  }
});
function getProviderKey(val: string): string | null {
  for (var g of modelOptions) {
    if (g.type === "group" && g.children) {
      for (var o of g.children) {
        if (o.value === val) return g.key;
      }
    }
  }
  return null;
}
function getProviderUrl(val: string): string {
  var pk = getProviderKey(val);
  if (pk && providerUrls[pk]) return providerUrls[pk];
  return '';
}
const loading = ref(false);
const klineData = ref<any[]>([]);
const downloading = ref(false);
const marketOptions = [{ label: 'A股', value: 'A' }, { label: '港股', value: 'HK' }, { label: '美股', value: 'US' }];
async function doAnalysis() {
  if (!symbol.value.trim()) return;
  var _m = aiModel.value === '__custom__' ? aiCustom.value : aiModel.value;
  if (!_m || !aiBaseUrl.value || !aiApiKey.value) {
    message.warning('请先展开 AI 模型配置，填写模型名、API 地址和 API Key');
    return;
  }
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

const modelHint = computed(function() {
  if (aiModel.value && aiModel.value !== '__custom__') {
    var url = getProviderUrl(aiModel.value);
    if (url) return '默认 API 地址: ' + url;
  }
  return '';
});

function clearConfig() {
  localStorage.removeItem('ai_model');
  localStorage.removeItem('ai_base_url');
  localStorage.removeItem('ai_api_key');
  localStorage.removeItem('ai_custom');
  aiModel.value = '';
  aiBaseUrl.value = '';
  aiApiKey.value = '';
  aiCustom.value = '';
  message.success('已清除已保存的 AI 配置');
}

function onModelChange(v) {
  if (v === '__custom__') { aiModel.value = '__custom__'; }
  else { aiModel.value = v; aiCustom.value = ''; var u = getProviderUrl(v); if (u) aiBaseUrl.value = u; }
}
  var url = URL.createObjectURL(blob);
  var a = document.createElement("a");
  a.href = url;
  a.download = "analysis_" + symbol.value + "_" + market.value + "_" + lookbackDays.value + "d.md";
  a.click();
  URL.revokeObjectURL(url);
}
</script>
