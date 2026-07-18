<template>
  <div>
    <div class="page-header"><h2>{{ symbol }} 财务数据</h2></div>
    <n-spin :show="loading">
      <n-alert v-if="!hasToken" type="warning" title="需要配置 Tushare Token" closable class="mb-24">
        财务数据通过 Tushare API 获取。请先在 Cloudflare Pages 环境变量中设置
        <n-code>TUSHARE_TOKEN</n-code>，然后重新部署。
      </n-alert>
      <n-grid :cols="2" :x-gap="16" :y-gap="16" v-if="data">
        <n-grid-item span="2">
          <n-card title="盈利能力" size="small">
            <n-grid :cols="4" :x-gap="12" :y-gap="8">
              <n-grid-item><n-statistic label="营业收入" :value="fmt(data.revenue)" /></n-grid-item>
              <n-grid-item><n-statistic label="营收增速" :value="fmtPct(data.revenue_growth)" /></n-grid-item>
              <n-grid-item><n-statistic label="净利润" :value="fmt(data.net_profit)" /></n-grid-item>
              <n-grid-item><n-statistic label="扣非净利润" :value="fmt(data.deducted_net_profit)" /></n-grid-item>
              <n-grid-item><n-statistic label="毛利率" :value="fmtPct(data.gross_margin)" /></n-grid-item>
              <n-grid-item><n-statistic label="净利率" :value="fmtPct(data.net_margin)" /></n-grid-item>
              <n-grid-item><n-statistic label="ROE" :value="fmtPct(data.roe)" /></n-grid-item>
              <n-grid-item><n-statistic label="报告期" :value="data.report_date||'-'" /></n-grid-item>
            </n-grid>
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card title="偿债能力" size="small">
            <n-grid :cols="2" :x-gap="12" :y-gap="8">
              <n-grid-item><n-statistic label="资产负债率" :value="fmtPct(data.debt_ratio)" /></n-grid-item>
              <n-grid-item><n-statistic label="流动比率" :value="fmt(data.current_ratio)" /></n-grid-item>
              <n-grid-item><n-statistic label="速动比率" :value="fmt(data.quick_ratio)" /></n-grid-item>
              <n-grid-item><n-statistic label="经营现金流" :value="fmt(data.operating_cashflow)" /></n-grid-item>
              <n-grid-item><n-statistic label="货币资金" :value="fmt(data.cash_equiv)" /></n-grid-item>
              <n-grid-item><n-statistic label="有息负债" :value="fmt(data.total_debt)" /></n-grid-item>
            </n-grid>
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card title="估值指标" size="small">
            <n-grid :cols="2" :x-gap="12" :y-gap="8">
              <n-grid-item><n-statistic label="PE(TTM)" :value="fmt(data.pe_ttm)" /></n-grid-item>
              <n-grid-item><n-statistic label="PB" :value="fmt(data.pb)" /></n-grid-item>
              <n-grid-item><n-statistic label="PEG" :value="fmt(data.peg)" /></n-grid-item>
              <n-grid-item><n-statistic label="股息率" :value="fmtPct(data.dividend_yield)" /></n-grid-item>
              <n-grid-item><n-statistic label="总市值" :value="fmt(data.market_cap)" /></n-grid-item>
            </n-grid>
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card title="运营指标" size="small">
            <n-grid :cols="2" :x-gap="12" :y-gap="8">
              <n-grid-item><n-statistic label="存货周转" :value="fmt(data.inventory_turnover)" /></n-grid-item>
              <n-grid-item><n-statistic label="应收周转" :value="fmt(data.ar_turnover)" /></n-grid-item>
              <n-grid-item><n-statistic label="商誉" :value="fmt(data.goodwill)" /></n-grid-item>
            </n-grid>
          </n-card>
        </n-grid-item>
        <n-grid-item span="2">
          <n-card title="风险提示" size="small">
            <n-grid :cols="3" :x-gap="12" :y-gap="8">
              <n-grid-item><n-statistic label="股权质押比例" :value="fmtPct(data.pledge_ratio)" /></n-grid-item>
              <n-grid-item><n-statistic label="大股东减持" :value="data.major_reduction||'暂无'" /></n-grid-item>
              <n-grid-item><n-statistic label="审计机构变更" :value="data.auditor_change||'暂无'" /></n-grid-item>
            </n-grid>
          </n-card>
        </n-grid-item>
      </n-grid>
    </n-spin>
    <n-button @click="$router.back()" class="mt-24">返回</n-button>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { getFinancials } from '../api';

const route = useRoute();
const symbol = ref(route.params.symbol as string);
const data = ref<any>(null);
const loading = ref(true);
const hasToken = ref(true);

function fmt(v: any) { if (v == null || v === 0) return '-'; if (v >= 1e8) return (v / 1e8).toFixed(2) + '亿'; if (v >= 1e4) return (v / 1e4).toFixed(2) + '万'; return typeof v === 'number' ? v.toFixed(2) : v; }
function fmtPct(v: any) { if (v == null) return '-'; return Number(parseFloat(v).toFixed(2)) + '%'; }

onMounted(async () => {
  try {
    const r = await getFinancials(symbol.value);
    if (r.code === 0 && r.data) { data.value = r.data; hasToken.value = true; }
    else hasToken.value = false;
  } catch(e) { hasToken.value = false; }
  loading.value = false;
});
</script>