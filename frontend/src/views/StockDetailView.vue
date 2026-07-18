<template>
  <div>
    <div class="page-header flex-between">
      <div>
        <h2>{{ symbol }} <span class="text-muted" style="font-weight: 400; font-size: 16px">{{ stockName }}</span></h2>
      </div>
      <n-space>
        <n-button size="small" :type="isWatched ? 'warning' : 'primary'" ghost @click="toggleWatchlist">
          {{ isWatched ? '已自选' : '加自选' }}
        </n-button>
        <n-button size="small" type="success" ghost @click="goToAnalysis">AI分析</n-button>
        <n-button size="small" type="info" ghost @click="goToFinancials">财务数据</n-button>
      </n-space>
    </div>

    <n-grid :cols="4" :x-gap="16" class="mb-24" v-if="quote">
      <n-grid-item><n-statistic label="最新价" :value="quote.price != null ? quote.price.toFixed(2) : '-'" :tabular-nums="true" /></n-grid-item>
      <n-grid-item><n-statistic label="涨跌额" :value="quote.change != null ? quote.change.toFixed(2) : '-'" :tabular-nums="true" :style="quote.change >= 0 ? 'color:var(--up-color)' : 'color:var(--down-color)'" /></n-grid-item>
      <n-grid-item><n-statistic label="涨跌幅" :value="quote.pct_change != null ? Number(quote.pct_change.toFixed(2)) + '%' : '-'" :tabular-nums="true" :style="quote.pct_change >= 0 ? 'color:var(--up-color)' : 'color:var(--down-color)'" /></n-grid-item>
      <n-grid-item><n-statistic label="成交量" :value="formatVolume(quote.volume)" :tabular-nums="true" /></n-grid-item>
    </n-grid>

    <n-card size="small" class="mb-24" v-if="stockScore">
      <template #header>
        <n-space align="center">
          <n-h4 prefix="bar" style="margin: 0">股票评分</n-h4>
          <n-tag size="small" :type="ratingType(stockScore.rating)">评级 {{ stockScore.rating }}</n-tag>
        </n-space>
      </template>
      <n-grid :cols="6" :x-gap="12" :y-gap="12">
        <n-grid-item>
          <n-statistic label="综合评分" :value="stockScore.total_score" :tabular-nums="true">
            <template #suffix>/100</template>
          </n-statistic>
          <n-progress type="line" :percentage="roundTo2(stockScore.total_score)" :height="8" :border-radius="4" :color="scoreColor(stockScore.total_score)" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic label="基本面(30分)" :value="stockScore.fundamental_score.toFixed(1)" :tabular-nums="true" />
          <n-progress type="line" :percentage="roundTo2(stockScore.fundamental_score / 30 * 100)" :height="6" :border-radius="4" color="#f0a020" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic label="偿债能力(20分)" :value="stockScore.solvency_score.toFixed(1)" :tabular-nums="true" />
          <n-progress type="line" :percentage="roundTo2(stockScore.solvency_score / 20 * 100)" :height="6" :border-radius="4" color="#2080f0" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic label="技术趋势(20分)" :value="stockScore.technical_score.toFixed(1)" :tabular-nums="true" />
          <n-progress type="line" :percentage="roundTo2(stockScore.technical_score / 20 * 100)" :height="6" :border-radius="4" color="#18a058" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic label="估值(15分)" :value="stockScore.valuation_score.toFixed(1)" :tabular-nums="true" />
          <n-progress type="line" :percentage="roundTo2(stockScore.valuation_score / 15 * 100)" :height="6" :border-radius="4" color="#8a2be2" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic label="风险(15分)" :value="stockScore.risk_score.toFixed(1)" :tabular-nums="true" />
          <n-progress type="line" :percentage="roundTo2(stockScore.risk_score / 15 * 100)" :height="6" :border-radius="4" color="#d03050" />
        </n-grid-item>
      </n-grid>

      <n-space v-if="stockScore.strengths.length > 0" :size="4" wrap class="mt-24">
        <n-tag v-for="s in stockScore.strengths" :key="s" type="success" size="small">{{ s }}</n-tag>
      </n-space>
      <n-space v-if="stockScore.risks.length > 0" :size="4" wrap class="mt-24">
        <n-tag v-for="r in stockScore.risks" :key="r" type="warning" size="small">{{ r }}</n-tag>
      </n-space>
      <n-alert type="info" title="投资建议" size="small" closable v-if="stockScore.suggestion" class="mt-24">
        {{ stockScore.suggestion }}
      </n-alert>
    </n-card>

    <n-card size="small" class="mb-24">
      <n-tabs type="line" :value="klinePeriod" @update:value="(v) => switchPeriod(v)">
        <n-tab-pane name="1M" tab="近1月"><KLineChart :data="klineData" /></n-tab-pane>
        <n-tab-pane name="3M" tab="近3月"><KLineChart :data="klineData" /></n-tab-pane>
        <n-tab-pane name="6M" tab="近6月"><KLineChart :data="klineData" /></n-tab-pane>
      </n-tabs>
    </n-card>

    <TechnicalIndicators :data="klineData" title="技术指标" />

    <n-card title="财务指标" size="small" class="mt-24" v-if="finData">
      <n-collapse>
        <n-collapse-item title="盈利能力" name="profit">
          <n-grid :cols="4" :x-gap="12" :y-gap="8">
            <n-grid-item><n-statistic label="营业收入" :value="fmtFin(finData.revenue)" /></n-grid-item>
            <n-grid-item><n-statistic label="营收增长率" :value="fmtPct(finData.revenue_growth)" /></n-grid-item>
            <n-grid-item><n-statistic label="净利润" :value="fmtFin(finData.net_profit)" /></n-grid-item>
            <n-grid-item><n-statistic label="扣非净利润" :value="fmtFin(finData.deducted_net_profit)" /></n-grid-item>
            <n-grid-item><n-statistic label="毛利率" :value="fmtPct(finData.gross_margin)" /></n-grid-item>
            <n-grid-item><n-statistic label="净利率" :value="fmtPct(finData.net_margin)" /></n-grid-item>
            <n-grid-item><n-statistic label="ROE" :value="fmtPct(finData.roe)" /></n-grid-item>
            <n-grid-item><n-statistic label="报告期" :value="finData.report_date || '-'" /></n-grid-item>
          </n-grid>
        </n-collapse-item>
        <n-collapse-item title="偿债能力" name="debt">
          <n-grid :cols="4" :x-gap="12" :y-gap="8">
            <n-grid-item><n-statistic label="资产负债率" :value="fmtPct(finData.debt_ratio)" /></n-grid-item>
            <n-grid-item><n-statistic label="流动比率" :value="fmtNum(finData.current_ratio)" /></n-grid-item>
            <n-grid-item><n-statistic label="速动比率" :value="fmtNum(finData.quick_ratio)" /></n-grid-item>
            <n-grid-item><n-statistic label="货币资金" :value="fmtFin(finData.cash)" /></n-grid-item>
            <n-grid-item><n-statistic label="有息负债" :value="fmtFin(finData.interest_debt)" /></n-grid-item>
            <n-grid-item><n-statistic label="经营现金流" :value="fmtFin(finData.operating_cashflow)" /></n-grid-item>
          </n-grid>
        </n-collapse-item>
        <n-collapse-item title="估值指标" name="valuation">
          <n-grid :cols="4" :x-gap="12" :y-gap="8">
            <n-grid-item><n-statistic label="PE(TTM)" :value="fmtNum(finData.pe_ttm)" /></n-grid-item>
            <n-grid-item><n-statistic label="PB" :value="fmtNum(finData.pb)" /></n-grid-item>
            <n-grid-item><n-statistic label="PEG" :value="fmtNum(finData.peg)" /></n-grid-item>
            <n-grid-item><n-statistic label="股息率" :value="fmtPct(finData.dividend_yield)" /></n-grid-item>
            <n-grid-item><n-statistic label="总市值" :value="fmtFin(finData.market_cap)" /></n-grid-item>
          </n-grid>
        </n-collapse-item>
        <n-collapse-item title="风险提示" name="risk">
          <n-grid :cols="4" :x-gap="12" :y-gap="8">
            <n-grid-item><n-statistic label="质押比例" :value="fmtPct(finData.pledge_ratio)" /></n-grid-item>
            <n-grid-item><n-statistic label="商誉" :value="fmtFin(finData.goodwill)" /></n-grid-item>
            <n-grid-item><n-statistic label="大股东减持" :value="finData.major_reduction || '暂无'" /></n-grid-item>
            <n-grid-item><n-statistic label="审计意见" :value="finData.auditor_change || '暂无'" /></n-grid-item>
          </n-grid>
        </n-collapse-item>
      </n-collapse>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { NAlert, NCard, NCollapse, NCollapseItem, NGrid, NGridItem, NH4, NProgress, NSpace, NStatistic, NTabPane, NTabs, NTag } from 'naive-ui';
import KLineChart from '../components/KLineChart.vue';
import TechnicalIndicators from '../components/TechnicalIndicators.vue';
import { getFinancials } from '../api';
import { useStockStore } from '../stores/stock';
import { useWatchlistStore } from '../stores/watchlist';

const route = useRoute();
const router = useRouter();
const stockStore = useStockStore();
const watchlistStore = useWatchlistStore();
const symbol = computed(() => route.params.symbol as string);
const stockName = ref('');
const quote = computed(() => stockStore.currentQuote);
const klineData = computed(() => stockStore.klineData);
const stockScore = computed(() => stockStore.stockScore);
const klinePeriod = ref('1M');
const finData = ref<any>(null);

function fmtFin(value: any) {
  if (value == null || value === 0) return '-';
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return String(value);
  if (Math.abs(numeric) >= 1e8) return (numeric / 1e8).toFixed(2) + '亿';
  if (Math.abs(numeric) >= 1e4) return (numeric / 1e4).toFixed(2) + '万';
  return numeric.toFixed(2);
}

function fmtPct(value: any) {
  if (value == null || value === '') return '-';
  const numeric = Number.parseFloat(String(value).replace('%', ''));
  return Number.isFinite(numeric) ? Number(numeric.toFixed(2)) + '%' : '-';
}

function fmtNum(value: any) {
  if (value == null || value === '') return '-';
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric.toFixed(2) : String(value);
}

function roundTo2(value: number): number {
  if (!Number.isFinite(value)) return 0;
  return Math.round(value * 100) / 100;
}

async function fetchFinancials() {
  try {
    const response = await getFinancials(symbol.value);
    if (response.code === 0 && response.data) finData.value = response.data;
  } catch (error) {
    finData.value = null;
  }
}

const isWatched = computed(() => watchlistStore.isInWatchlist(symbol.value));
function toggleWatchlist() {
  const name = quote.value?.name || stockName.value || symbol.value;
  const market = quote.value?.market || 'A';
  const added = watchlistStore.toggle(symbol.value, name, market);
  if (added) {
    router.push({ name: 'watchlist' });
  }
}
function goToFinancials() { router.push({ name: 'financials', params: { symbol: symbol.value } }); }
function goToAnalysis() { router.push({ name: 'analysis', query: { symbol: symbol.value, market: 'A' } }); }
function scoreColor(score: number) { if (score >= 80) return '#18a058'; if (score >= 65) return '#2080f0'; if (score >= 50) return '#f0a020'; return '#d03050'; }
function ratingType(rating: string) { if (rating === 'A') return 'success'; if (rating === 'B') return 'info'; if (rating === 'C') return 'warning'; return 'error'; }
function formatVolume(value: number) { if (value >= 1e8) return (value / 1e8).toFixed(2) + '亿'; if (value >= 1e4) return (value / 1e4).toFixed(2) + '万'; return value.toFixed(0); }
function switchPeriod(period: string) {
  klinePeriod.value = period;
  const days = period === '1M' ? 30 : period === '3M' ? 90 : 180;
  const end = new Date().toISOString().slice(0, 10);
  const start = new Date(Date.now() - days * 86400000).toISOString().slice(0, 10);
  stockStore.fetchKline(symbol.value, 'A', start, end);
}

function refreshPageData() {
  stockStore.clear();
  fetchFinancials();
  stockStore.fetchScore(symbol.value);
  stockStore.fetchQuote(symbol.value);
  switchPeriod('1M');
}

onMounted(refreshPageData);
watch(symbol, refreshPageData);
</script>
