<template>
  <div>
    <div class="page-header flex-between">
      <div><h2>{{ symbol }} <span class="text-muted" style="font-weight:400;font-size:16px">{{ stockName }}</span></h2></div>
      <n-space>
        <n-button size="small" :type="isWatched ? 'warning' : 'primary'" ghost @click="toggleWatchlist">
          {{ isWatched ? '已自选' : '加自选' }}
        </n-button>
        <n-button size="small" type="success" ghost @click="goToAnalysis">AI分析</n-button>
      </n-space>
    </div>
    <n-grid :cols="4" :x-gap="16" class="mb-24" v-if="quote">
      <n-grid-item><n-statistic label="最新价" :value="quote.price" :tabular-nums="true" /></n-grid-item>
      <n-grid-item><n-statistic label="涨跌额" :value="quote.change" :tabular-nums="true" :style="quote.change >= 0 ? 'color:var(--up-color)' : 'color:var(--down-color)'" /></n-grid-item>
      <n-grid-item><n-statistic label="涨跌幅" :value="quote.pct_change + '%'" :tabular-nums="true" :style="quote.pct_change >= 0 ? 'color:var(--up-color)' : 'color:var(--down-color)'" /></n-grid-item>
      <n-grid-item><n-statistic label="成交量" :value="formatVolume(quote.volume)" :tabular-nums="true" /></n-grid-item>
    </n-grid>
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
            <n-grid-item><n-statistic label="净利润" :value="fmtFin(finData.net_profit)" /></n-grid-item>
            <n-grid-item><n-statistic label="扣非净利润" :value="fmtFin(finData.deducted_net_profit)" /></n-grid-item>
            <n-grid-item><n-statistic label="毛利率" :value="finData.gross_margin != null ? finData.gross_margin + '%' : '-'"/></n-grid-item>
            <n-grid-item><n-statistic label="净利率" :value="finData.net_margin != null ? finData.net_margin + '%' : '-'"/></n-grid-item>
            <n-grid-item><n-statistic label="ROE" :value="finData.roe != null ? finData.roe + '%' : '-'"/></n-grid-item>
            <n-grid-item><n-statistic label="营业收入" :value="fmtFin(finData.revenue)" /></n-grid-item>
            <n-grid-item><n-statistic label="营收增速" :value="finData.revenue_growth != null ? finData.revenue_growth + '%' : '-'"/></n-grid-item>
            <n-grid-item><n-statistic label="报告期" :value="finData.report_date || '-'" /></n-grid-item>
          </n-grid>
        </n-collapse-item>
        <n-collapse-item title="偿债能力" name="debt">
          <n-grid :cols="4" :x-gap="12" :y-gap="8">
            <n-grid-item><n-statistic label="资产负债率" :value="finData.debt_ratio != null ? finData.debt_ratio + '%' : '-'"/></n-grid-item>
            <n-grid-item><n-statistic label="流动比率" :value="finData.current_ratio != null ? finData.current_ratio : '-'" /></n-grid-item>
            <n-grid-item><n-statistic label="速动比率" :value="finData.quick_ratio != null ? finData.quick_ratio : '-'" /></n-grid-item>
            <n-grid-item><n-statistic label="经营现金流" :value="fmtFin(finData.operating_cashflow)" /></n-grid-item>
          </n-grid>
        </n-collapse-item>
        <n-collapse-item title="估值指标" name="valuation">
          <n-grid :cols="4" :x-gap="12" :y-gap="8">
            <n-grid-item><n-statistic label="PE(TTM)" :value="finData.pe_ttm != null ? finData.pe_ttm.toFixed(2) : '-'" /></n-grid-item>
            <n-grid-item><n-statistic label="PB" :value="finData.pb != null ? finData.pb.toFixed(2) : '-'" /></n-grid-item>
            <n-grid-item><n-statistic label="总市值" :value="fmtFin(finData.market_cap)" /></n-grid-item>
          </n-grid>
        </n-collapse-item>
        <n-collapse-item title="风险提示" name="risk">
          <n-p style="font-size:13px;color:#888">质押比例: {{ finData.pledge_ratio != null ? finData.pledge_ratio + "%" : "暂无数据" }}</n-p>
          <n-p style="font-size:13px;color:#888">大股东减持: {{ finData.major_reduction || "暂无" }}</n-p>
          <n-p style="font-size:13px;color:#888">审计机构变更: {{ finData.auditor_change || "暂无" }}</n-p>
        </n-collapse-item>
      </n-collapse>
    </n-card>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useStockStore } from '../stores/stock';
import { useWatchlistStore } from '../stores/watchlist';
import KLineChart from '../components/KLineChart.vue';
import TechnicalIndicators from '../components/TechnicalIndicators.vue';
import { NCard, NCollapse, NCollapseItem, NGrid, NGridItem, NStatistic, NP } from 'naive-ui';
const route = useRoute();
const router = useRouter();
const stockStore = useStockStore();
const watchlistStore = useWatchlistStore();
const symbol = computed(() => route.params.symbol as string);
const stockName = ref('');
const quote = computed(() => stockStore.currentQuote);
const klineData = computed(() => stockStore.klineData);
const klinePeriod = ref('1M');
const finData = ref<any>(null);
function fmtFin(v: any) { if (v == null || v === 0) return '-'; if (v >= 1e8) return (v / 1e8).toFixed(2) + '亿'; if (v >= 1e4) return (v / 1e4).toFixed(2) + '万'; return v.toFixed(2); }
async function fetchFinancials() { try { var r = await getFinancials(symbol.value); if (r.code === 0 && r.data) finData.value = r.data; } catch(e) {} }
const isWatched = computed(() => watchlistStore.isInWatchlist(symbol.value));
function toggleWatchlist() { if (isWatched.value) watchlistStore.remove(symbol.value); else watchlistStore.add(symbol.value, stockName.value); }
function goToAnalysis() { router.push({ name: 'analysis', query: { symbol: symbol.value, market: 'A' } }); }
function formatVolume(v) { if (v >= 1e8) return (v / 1e8).toFixed(2) + '亿'; if (v >= 1e4) return (v / 1e4).toFixed(2) + '万'; return v.toFixed(0); }
function switchPeriod(p) {
  klinePeriod.value = p;
  const days = p === '1M' ? 30 : p === '3M' ? 90 : 180;
  const end = new Date().toISOString().slice(0, 10);
  const start = new Date(Date.now() - days * 86400000).toISOString().slice(0, 10);
  stockStore.fetchKline(symbol.value, 'A', start, end);
}
onMounted(() => { stockStore.fetchQuote(symbol.value); switchPeriod('1M'); stockStore.fetchKline(symbol.value, 'A'); });
watch(symbol, () => { stockStore.clear(); stockStore.fetchQuote(symbol.value); switchPeriod('1M'); fetchFinancials(); });
</script>