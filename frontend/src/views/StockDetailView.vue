<template>
  <div class="stock-detail-page">
    <div class="page-header" style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px">
      <div>
        <h2>{{ displayName }} <span class="text-muted" style="font-weight:400;font-size:14px">{{ displayMarket }}</span></h2>
      </div>
      <n-button size="small" type="primary" @click="goToAnalysis">AI分析</n-button>
<n-card size="small" class="mb-24" v-if="quote && quote.price && (Number(quote.price) > 0 || Number(quote.volume) > 0 || Number(quote.amount) > 0)">
      <n-grid :cols="2" :x-gap="12" :y-gap="8" responsive="screen">
        <n-grid-item>
          <div style="display:flex;align-items:baseline;gap:8px">
            <span style="font-size:28px;font-weight:700">{{ fmtPrice(quote.price) }}</span>
            <n-tag :type="quote.pct_change >= 0 ? 'error' : 'success'" size="small" bordered>
              {{ quote.pct_change >= 0 ? '+' : '' }}{{ fmtPct(quote.pct_change) }}
            </n-tag>
            <span :style="{color: quote.change >= 0 ? '#f56c6c' : '#67c23a', fontSize: '14px'}">
              {{ quote.change >= 0 ? '+' : '' }}{{ fmtPrice(quote.change) }}
            </span>
          </div>
        </n-grid-item>
        <n-grid-item>
          <n-grid :cols="2" :x-gap="8" :y-gap="4">
            <n-grid-item><n-statistic label="成交量" :value="fmtVolume(quote.volume)" :tabular-nums="true" /></n-grid-item>
            <n-grid-item><n-statistic label="成交额" :value="fmtAmount(quote.amount)" :tabular-nums="true" /></n-grid-item>
          </n-grid>
        </n-grid-item>
      </n-grid>
    </n-card>
<n-card size="small" class="mb-24" v-if="stockScore && !stockScore.data_insufficient">
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
      </n-grid><n-p depth="3" style="font-size:12px;margin-top:8px;color:#888;line-height:1.6">
评分说明：
• 基本面（30分）——考察公司的盈利能力（ROE）、成长性（收入增长）、财务健康度，得分越高公司基本面越好。
• 偿债能力（20分）——考察公司的资产负债率、现金流状况，得分越高财务越安全。
• 技术趋势（20分）——考察股价的短期和中期走势，得分越高趋势越好。
• 估值（15分）——考察市盈率PE和市净率PB是否合理，估值越低得分越高。
• 风险（15分）——考察质押比例、大股东减持、审计意见等风险因素，风险越低得分越高。
</n-p>
    </n-card>
    <n-card size="small" class="mb-24" v-if="stockScore && stockScore.data_insufficient">
      <template #header><n-h4 prefix="bar" style="margin:0">股票评分</n-h4></template>
      <n-empty description="分析数据不足，无法进行评分" style="padding: 24px 0">
        <template #extra>
          <p style="color: #888; font-size: 14px; margin: 0">当前股票的财务数据未能获取到，暂无足够数据进行综合评分。</p>
        </template>
      </n-empty>
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
            <n-grid-item><n-statistic label="PE(市率,估值指标)" :value="fmtNum(finData.pe_ttm)" /></n-grid-item>
            <n-grid-item><n-statistic label="PB(市净率,估值指标)" :value="fmtNum(finData.pb)" /></n-grid-item>
            <n-grid-item><n-statistic label="营收增长(收入同比增幅)" :value="fmtPct(finData.revenue_growth)" /></n-grid-item>
            <n-grid-item><n-statistic label="毛利率(收入减去成本后的利润占比，越高盈利能力越强)" :value="fmtPct(finData.gross_margin)" /></n-grid-item>
            <n-grid-item><n-statistic label="ROE(净资产收益率,盈利能力)" :value="fmtPct(finData.roe)" /></n-grid-item>
            <n-grid-item><n-statistic label="资产负债率(总负债÷总资产，越高说明负债越多，风险越大)" :value="fmtPct(finData.debt_ratio)" /></n-grid-item>
            <n-grid-item><n-statistic label="质押比例(大股东质押占比，越高平仓风险越大)" :value="fmtPct(finData.pledge_ratio)" /></n-grid-item>
            <n-grid-item><n-statistic label="商誉(收购溢价，越高减值风险越大)" :value="fmtMoney(finData.goodwill)" /></n-grid-item>
            <n-grid-item><n-statistic label="大股东减持(重要股东卖出股份)" :value="finData.major_reduction || '--'" /></n-grid-item>
            <n-grid-item><n-statistic label="审计意见(财报可信度)" :value="finData.auditor_change || '--'" /></n-grid-item>
          </n-grid>
        </n-collapse-item>
      </n-collapse>
    </n-card>
    </div>
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
const displayName = computed(() => {
  var n = quote.value?.name;
  if (n && n !== '--') return n;
  n = finData.value?.name;
  if (n && n !== '--') return n;
  return symbol.value;
});
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
function fmtPrice(v: any): string { var n = Number(v); if (!Number.isFinite(n) || n === 0) return '--'; return n.toFixed(2); }
function fmtVolume(v: any): string { var n = Number(v); if (!Number.isFinite(n) || n === 0) return '--'; if (n >= 1e8) return (n / 1e8).toFixed(2) + ' 亿'; if (n >= 1e4) return (n / 1e4).toFixed(2) + ' 万'; return n.toFixed(0); }
function fmtAmount(v: any): string { var n = Number(v); if (!Number.isFinite(n) || n === 0) return '--'; if (n >= 1e8) return (n / 1e8).toFixed(2) + ' 亿'; if (n >= 1e4) return (n / 1e4).toFixed(2) + ' 万'; return n.toFixed(0); }
function refreshPageData(): void { stockStore.clear(); void fetchFinancials(); void stockStore.fetchScore(symbol.value); void stockStore.fetchQuote(symbol.value); switchPeriod('1M'); }
onMounted(refreshPageData);

function goToAnalysis(): void {
  var m = (quote.value && quote.value.market) ? quote.value.market : "A";
  var sym = encodeURIComponent(symbol.value || "");
  window.location.href = "/analysis?symbol=" + sym + "&market=" + m;
}
watch(symbol, refreshPageData);

</script>