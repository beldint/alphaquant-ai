<template>
  <div class="stock-detail-page">
    <div class="page-header">
      <div>
        <h2>{{ displayName }} <span class="text-muted" style="font-weight:400;font-size:14px">{{ displayMarket }}</span></h2>
      </div>
<n-card size="small" class="mb-24" v-if="stockScore">
      <template #header><n-space align="center"><n-h4 prefix="bar" style="margin:0">股票评分</n-h4><n-tag size="small" :type="ratingType(stockScore.rating)">评级 {{ stockScore.rating || '--' }}</n-tag></n-space></template>
      <n-grid :cols="2" :x-gap="12" :y-gap="12" responsive="screen">
        <n-grid-item>
          <n-statistic label="综合评分" :value="fmtScore(stockScore.total_score)" :tabular-nums="true"><template #suffix>{{ stockScore.total_score == null ? '' : '/100' }}</template></n-statistic>
          <n-progress v-if="stockScore.total_score != null" type="line" :percentage="roundTo2(stockScore.total_score)" :height="8" :border-radius="4" :color="scoreColor(stockScore.total_score)" />
        </n-grid-item>
        <n-grid-item><n-statistic label="基本面(30分)" :value="fmtScore(stockScore.fundamental_score)" :tabular-nums="true" /><n-progress v-if="stockScore.fundamental_score != null" type="line" :percentage="roundTo2(stockScore.fundamental_score / 30 * 100)" :height="6" :border-radius="4" color="#f0a020" /></n-grid-item>
        <n-grid-item><n-statistic label="偿债能力(20分)" :value="fmtScore(stockScore.solvency_score)" :tabular-nums="true" /><n-progress v-if="stockScore.solvency_score != null" type="line" :percentage="roundTo2(stockScore.solvency_score / 20 * 100)" :height="6" :border-radius="4" color="#2080f0" /></n-grid-item>
        <n-grid-item><n-statistic label="技术趋势(20分)" :value="fmtScore(stockScore.technical_score)" :tabular-nums="true" /><n-progress v-if="stockScore.technical_score != null" type="line" :percentage="roundTo2(stockScore.technical_score / 20 * 100)" :height="6" :border-radius="4" color="#18a058" /></n-grid-item>
        <n-grid-item><n-statistic label="估值(15分)" :value="fmtScore(stockScore.valuation_score)" :tabular-nums="true" /><n-progress v-if="stockScore.valuation_score != null" type="line" :percentage="roundTo2(stockScore.valuation_score / 15 * 100)" :height="6" :border-radius="4" color="#8a2be2" /></n-grid-item>
        <n-grid-item><n-statistic label="风险(15分)" :value="fmtScore(stockScore.risk_score)" :tabular-nums="true" /><n-progress v-if="stockScore.risk_score != null" type="line" :percentage="roundTo2(stockScore.risk_score / 15 * 100)" :height="6" :border-radius="4" color="#d03050" /></n-grid-item>
      </n-grid>
    </n-card>

    <n-card size="small" class="mb-24">
      <n-tabs type="line" :value="klinePeriod" @update:value="(value) => switchPeriod(String(value))">
        <n-tab-pane name="1M" tab="近1月"><KLineChart :data="klineData" /></n-tab-pane>
        <n-tab-pane name="3M" tab="近3月"><KLineChart :data="klineData" /></n-tab-pane>
        <n-tab-pane name="6M" tab="近6月"><KLineChart :data="klineData" /></n-tab-pane>
      </n-tabs>
    </n-card>

    <n-card size="small" class="mb-24">
      <TechnicalIndicators :data="klineData" />
    </n-card>

    <n-card size="small" v-if="finData">
      <n-collapse>
        <n-collapse-item title="财务数据" name="finance">
          <n-grid :cols="2" :x-gap="12" :y-gap="8" responsive="screen">
            <n-grid-item><n-statistic label="PE(TTM)" :value="fmtNum(finData.pe_ttm)" /></n-grid-item>
            <n-grid-item><n-statistic label="PB" :value="fmtNum(finData.pb)" /></n-grid-item>
            <n-grid-item><n-statistic label="营收增长" :value="fmtPct(finData.revenue_growth)" /></n-grid-item>
            <n-grid-item><n-statistic label="毛利率" :value="fmtPct(finData.gross_margin)" /></n-grid-item>
            <n-grid-item><n-statistic label="ROE" :value="fmtPct(finData.roe)" /></n-grid-item>
            <n-grid-item><n-statistic label="资产负债率" :value="fmtPct(finData.debt_ratio)" /></n-grid-item>
            <n-grid-item><n-statistic label="质押比例" :value="fmtPct(finData.pledge_ratio)" /></n-grid-item>
            <n-grid-item><n-statistic label="商誉" :value="fmtMoney(finData.goodwill)" /></n-grid-item>
            <n-grid-item><n-statistic label="大股东减持" :value="finData.major_reduction || '--'" /></n-grid-item>
            <n-grid-item><n-statistic label="审计意见" :value="finData.auditor_change || '--'" /></n-grid-item>
          </n-grid>
        </n-collapse-item>
      </n-collapse>
    </n-card>
  </div>
</template>
<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { NCard, NCollapse, NCollapseItem, NGrid, NGridItem, NH4, NProgress, NSpace, NStatistic, NTabPane, NTabs, NTag } from 'naive-ui';
import KLineChart from '../components/KLineChart.vue';
import TechnicalIndicators from '../components/TechnicalIndicators.vue';
import { getFinancials } from '../api';
import { useStockStore } from '../stores/stock';

const route = useRoute();

const stockStore = useStockStore();

const symbol = computed(() => route.params.symbol as string);
const quote = computed(() => stockStore.currentQuote);
const displayName = computed(() => quote.value?.name || finData.value?.name || '--');
const displayMarket = computed(() => {
  var m = quote.value?.market || 'A';
  if (m === 'A') return 'A股';
  if (m === 'HK') return '港股';
  if (m === 'US') return '美股';
  return m;
});
const klineData = computed(() => stockStore.klineData);
const stockScore = computed(() => stockStore.stockScore);
const klinePeriod = ref('1M');
const finData = ref<Record<string, any> | null>(null);
function toNumber(value: unknown): number | null { if (value === null || value === undefined || value === '' || value === '--') return null; const numeric = Number(String(value).replace(/,/g, '').replace('%', '')); return Number.isFinite(numeric) ? numeric : null; }
function fmtMoney(value: unknown): string { const numeric = toNumber(value); if (numeric === null || numeric === 0) return '--'; if (Math.abs(numeric) >= 1e8) return (numeric / 1e8).toFixed(2) + ' 亿'; if (Math.abs(numeric) >= 1e4) return (numeric / 1e4).toFixed(2) + ' 万'; return numeric.toFixed(2); }
function fmtPct(value: unknown): string { const numeric = toNumber(value); return numeric === null ? '--' : numeric.toFixed(2) + '%'; }
function fmtNum(value: unknown): string { const numeric = toNumber(value); return numeric === null ? '--' : numeric.toFixed(2); }
function fmtScore(value: number | null): string { return value === null || value === undefined ? '--' : value.toFixed(1); }
function roundTo2(value: number): number { if (!Number.isFinite(value)) return 0; return Math.round(value * 100) / 100; }
async function fetchFinancials(): Promise<void> { try { const response = await getFinancials(symbol.value); finData.value = Number(response.code) === 0 && response.data ? response.data : null; } catch { finData.value = null; } }
function scoreColor(score: number): string { if (score >= 80) return '#18a058'; if (score >= 65) return '#2080f0'; if (score >= 50) return '#f0a020'; return '#d03050'; }
function ratingType(rating: string): 'default' | 'success' | 'info' | 'warning' | 'error' { if (rating === 'A') return 'success'; if (rating === 'B') return 'info'; if (rating === 'C') return 'warning'; if (rating === 'D') return 'error'; return 'default'; }
function switchPeriod(period: string): void { klinePeriod.value = period; const days = period === '1M' ? 30 : period === '3M' ? 90 : 180; const end = new Date().toISOString().slice(0, 10); const start = new Date(Date.now() - days * 86400000).toISOString().slice(0, 10); void stockStore.fetchKline(symbol.value, 'A', start, end); }
function refreshPageData(): void { stockStore.clear(); void fetchFinancials(); void stockStore.fetchScore(symbol.value); void stockStore.fetchQuote(symbol.value); switchPeriod('1M'); }
onMounted(refreshPageData);
watch(symbol, refreshPageData);
</script>