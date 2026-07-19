<template>
  <div class="financial-view">
    <div class="page-header flex-between">
      <div><h2>{{ symbol }} 财务数据</h2><p v-if="data?.name" class="page-subtitle">{{ data.name }} · {{ dataSourceText }}</p></div>
      <n-button tertiary @click="$router.back()">返回</n-button>
    </div>
    <n-spin :show="loading">
      <n-alert v-if="errorMessage" type="warning" title="财务数据暂不可用" closable class="mb-24">{{ errorMessage }}</n-alert>
      <n-empty v-if="!loading && !hasFinancialData" description="暂未获取到可展示的财务指标" />
      <n-grid v-else-if="data" :cols="1" :x-gap="12" :y-gap="12" responsive="screen">
        <n-grid-item>
          <n-card title="盈利能力(赚钱能力指标)" size="small">
            <n-grid :cols="2" :x-gap="12" :y-gap="8" responsive="screen">
              <n-grid-item><n-statistic label="营业收入" :value="fmtMoney(data.revenue)" /></n-grid-item>
              <n-grid-item><n-statistic label="营收增长(同比增幅)" :value="fmtPct(data.revenue_growth)" /></n-grid-item>
              <n-grid-item><n-statistic label="净利润(赚的钱)" :value="fmtMoney(data.net_profit)" /></n-grid-item>
              <n-grid-item><n-statistic label="扣非净利润(主业赚的钱)" :value="fmtMoney(data.deducted_net_profit)" /></n-grid-item>
              <n-grid-item><n-statistic label="毛利率(产品赚钱能力)" :value="fmtPct(data.gross_margin)" /></n-grid-item>
              <n-grid-item><n-statistic label="净利率(最终赚钱能力)" :value="fmtPct(data.net_margin)" /></n-grid-item>
              <n-grid-item><n-statistic label="净资产收益率(ROE,股东回报率)" :value="fmtPct(data.roe)" /></n-grid-item>
              <n-grid-item><n-statistic label="报告期(财务数据所属期间)" :value="data.report_date || '-'" /></n-grid-item>
            </n-grid>
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card title="偿债能力(还债能力指标)" size="small">
            <n-grid :cols="2" :x-gap="12" :y-gap="8" responsive="screen">
              <n-grid-item><n-statistic label="资产负债率(负债占比)" :value="fmtPct(data.debt_ratio)" /></n-grid-item>
              <n-grid-item><n-statistic label="流动比率(短期偿债能力)" :value="fmtNumber(data.current_ratio)" /></n-grid-item>
              <n-grid-item><n-statistic label="速动比率(快速偿债能力)" :value="fmtNumber(data.quick_ratio)" /></n-grid-item>
              <n-grid-item><n-statistic label="经营现金流(真金白银入账)" :value="fmtMoney(data.operating_cashflow)" /></n-grid-item>
              <n-grid-item><n-statistic label="货币资金(手头现金)" :value="fmtMoney(data.cash)" /></n-grid-item>
              <n-grid-item><n-statistic label="有息负债(要付利息的债)" :value="fmtMoney(data.interest_debt)" /></n-grid-item>
            </n-grid>
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card title="估值指标(贵不贵衡量)" size="small">
            <n-grid :cols="2" :x-gap="12" :y-gap="8" responsive="screen">
              <n-grid-item><n-statistic label="市盈率(PE(滚动12个月))" :value="fmtNumber(data.pe_ttm)" /></n-grid-item>
              <n-grid-item><n-statistic label="市净率(PB)" :value="fmtNumber(data.pb)" /></n-grid-item>
              <n-grid-item><n-statistic label="PEG(市盈率/盈利增长率)" :value="fmtNumber(data.peg)" /></n-grid-item>
              <n-grid-item><n-statistic label="股息率(分红回报率)" :value="fmtPct(data.dividend_yield)" /></n-grid-item>
              <n-grid-item><n-statistic label="总市值(公司总价值)" :value="fmtMoney(data.market_cap)" /></n-grid-item>
              <n-grid-item><n-statistic label="总股本(总股票数量)" :value="fmtMoney(data.total_shares)" /></n-grid-item>
            </n-grid>
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card title="运营指标(经营效率)" size="small">
            <n-grid :cols="2" :x-gap="12" :y-gap="8" responsive="screen">
              <n-grid-item><n-statistic label="存货周转天数(卖货速度)" :value="fmtNumber(data.inventory_days)" /></n-grid-item>
              <n-grid-item><n-statistic label="应收周转天数(回款速度)" :value="fmtNumber(data.ar_days)" /></n-grid-item>
              <n-grid-item><n-statistic label="商誉(收购溢价)" :value="fmtMoney(data.goodwill)" /></n-grid-item>
            </n-grid>
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card title="风险提示(潜在风险)" size="small">
            <n-grid :cols="2" :x-gap="12" :y-gap="8" responsive="screen">
              <n-grid-item><n-statistic label="股权质押比例(大股东抵押风险)" :value="fmtPct(data.pledge_ratio)" /></n-grid-item>
              <n-grid-item><n-statistic label="大股东减持(重要股东卖股票)" :value="data.major_reduction || '暂无'" /></n-grid-item>
              <n-grid-item><n-statistic label="审计意见变更(财务可信度变化)" :value="data.auditor_change || '未变更'" /></n-grid-item>
            </n-grid>
          </n-card>
        </n-grid-item>
      </n-grid>
    </n-spin>
  </div>
</template>
<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { NAlert, NButton, NCard, NEmpty, NGrid, NGridItem, NSpin, NStatistic } from 'naive-ui';
import { getFinancials } from '../api';
const route = useRoute();
const symbol = route.params.symbol as string;
const data = ref<any>(null);
const loading = ref(true);
const errorMessage = ref('');
const hasFinancialData = ref(false);
const dataSourceText = '东方财富';
function fmtMoney(value: unknown): string {
  if (value == null || value === '' || value === '--') return '--';
  const n = Number(value);
  if (!Number.isFinite(n)) return '--';
  if (Math.abs(n) >= 1e8) return (n / 1e8).toFixed(2) + ' 亿';
  if (Math.abs(n) >= 1e4) return (n / 1e4).toFixed(2) + ' 万';
  return n.toFixed(2);
}
function fmtPct(value: unknown): string {
  if (value == null || value === '' || value === '--') return '--';
  const n = Number(value);
  return Number.isFinite(n) ? n.toFixed(2) + '%' : '--';
}
function fmtNumber(value: unknown): string {
  if (value == null || value === '' || value === '--') return '--';
  const n = Number(value);
  return Number.isFinite(n) ? n.toFixed(2) : '--';
}
onMounted(async () => {
  try {
    const res = await getFinancials(symbol);
    if (Number(res.code) === 0 && res.data) {
      data.value = res.data;
      hasFinancialData.value = Object.values(res.data).some(v => v != null && v !== '' && v !== '--');
    }
  } catch (err: unknown) { errorMessage.value = err instanceof Error ? err.message : String(err); }
  finally { loading.value = false; }
});
</script>
<style scoped>
.financial-view .page-header { display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 8px; margin-bottom: 20px; }
.financial-view .page-subtitle { color: var(--text-secondary); margin-top: 2px; font-size: 13px; }
</style>