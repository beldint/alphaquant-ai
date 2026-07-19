<template>
  <div v-if="report" class="analysis-report">
    <n-card title="价格趋势图" size="small" class="mb-24 report-card">
      <div v-if="klineData && klineData.length > 0">
        <div ref="chartRef" class="chart-container"></div>
        <n-p depth="3" class="chart-note">
          说明：蓝色折线为收盘价走势，下方红绿柱为成交量（红色：下跌日，绿色：上涨日）。数据来源于公开行情，仅供分析参考。
        </n-p>
      </div>
      <n-empty v-else description="暂无实时K线数据，无法显示趋势图" />
    </n-card>

    <n-card title="技术指标摘要" size="small" class="mb-24 report-card">
      <n-grid cols="2 s:3 m:4" :x-gap="8" :y-gap="8" responsive="screen">
        <n-grid-item v-for="(item, idx) in techItems" :key="idx">
          <div class="indicator-card" :class="'indicator-' + (idx % 6)">
            <div class="indicator-label">{{ item.label }}</div>
            <div class="indicator-value" :class="valueColorClass(item.value)">{{ item.value }}</div>
            <div class="indicator-desc">{{ item.desc }}</div>
          </div>
        </n-grid-item>
      </n-grid>
      <n-p depth="3" class="indicator-note">
        提示：将鼠标悬停在指标标签上可查看详细说明。数据基于最新{{ klineData?.length || 0 }}个交易日计算。
      </n-p>
    </n-card>

    <n-card v-if="riskItems.length > 0" title="风险指标" size="small" class="mb-24 report-card">
      <n-grid cols="2 s:3" :x-gap="8" :y-gap="8" responsive="screen">
        <n-grid-item v-for="(item, i) in riskItems" :key="i">
          <div class="risk-card" :class="'risk-' + item.level">
            <div class="risk-label">{{ item.label }}
              <n-tag size="tiny" :type="riskTagType(item.level)" class="risk-tag">
                {{ item.level === 'high' ? '高风险' : item.level === 'mid' ? '中等' : '正常' }}
              </n-tag>
            </div>
            <div class="risk-value">{{ item.value }}</div>
            <div class="risk-desc">{{ item.desc }}</div>
          </div>
        </n-grid-item>
      </n-grid>
    </n-card>

    <n-card title="AI 投资分析报告" size="small" class="mb-24 report-card">
      <template #header-extra>
        <n-space>
          <n-button size="tiny" quaternary @click="scrollToTop">回到顶部</n-button>
        </n-space>
      </template>
      <n-spin :show="loading">
        <div class="report-content" v-html="renderedHtml"></div>
      </n-spin>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, watch, nextTick, onUnmounted } from 'vue';
import * as echarts from 'echarts';
import type { AnalysisReport, KlineRecord, Quote } from '../stores/stock';

const props = defineProps<{ report: AnalysisReport | null; klineData?: KlineRecord[]; quote?: Quote | null; loading?: boolean }>();
const chartRef = ref<HTMLDivElement>();
let chartInstance: echarts.ECharts | null = null;

function scrollToTop(): void {
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function valueColorClass(v: any): string {
  if (v === '--' || v == null) return '';
  var n = parseFloat(String(v).replace(/[^0-9.\-]/g, ''));
  if (isNaN(n)) return '';
  if (n > 0) return 'value-up';
  if (n < 0) return 'value-down';
  return '';
}

function riskTagType(level: string): any {
  if (level === 'high') return 'error';
  if (level === 'mid') return 'warning';
  return 'default';
}

function renderChart() {
  if (!chartRef.value || !props.klineData || props.klineData.length === 0) return;
  if (chartInstance) { chartInstance.dispose(); }
  chartInstance = echarts.init(chartRef.value);
  
  var dates = props.klineData.map(function(k) { return k.trade_date; });
  var closes = props.klineData.map(function(k) { return k.close_price; });
  var volumes = props.klineData.map(function(k) { return k.volume; });
  var opens = props.klineData.map(function(k) { return k.open_price; });
  
  var volColors = props.klineData.map(function(k, i) {
    return k.close_price >= opens[i] ? '#26a69a' : '#ef5350';
  });

  chartInstance.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      backgroundColor: 'rgba(255,255,255,0.95)',
      borderColor: '#ddd',
      borderWidth: 1,
      textStyle: { fontSize: 12, color: '#333' },
      formatter: function(params: any[]) {
        if (!params || params.length === 0) return '';
        var res = '<div style="font-weight:600;margin-bottom:4px">' + params[0].axisValue + '</div>';
        for (var p = 0; p < params.length; p++) {
          if (params[p].seriesName === '收盘价') {
            res += '<div style="display:flex;justify-content:space-between"><span>收盘价</span><strong>' + params[p].value + ' 元</strong></div>';
          } else if (params[p].seriesName === '成交量') {
            res += '<div style="display:flex;justify-content:space-between"><span>成交量</span><strong>' + Number(params[p].value).toLocaleString() + ' 手</strong></div>';
          }
        }
        return '<div style="padding:4px 0">' + res + '</div>';
      }
    },
    legend: { data: ['收盘价', '成交量'], top: 4, textStyle: { fontSize: 11 }, itemWidth: 16, itemHeight: 8 },
    grid: [
      { left: 50, right: 20, top: 36, bottom: '52%' },
      { left: 50, right: 20, top: '56%', bottom: '26%' }
    ],
    xAxis: [
      {
        type: 'category', data: dates,
        axisLine: { onZero: false },
        axisLabel: { rotate: 30, fontSize: 10, margin: 4 },
        splitLine: { show: false },
        axisTick: { alignWithLabel: true }
      },
      {
        type: 'category', gridIndex: 1, data: dates,
        axisLabel: { show: false },
        splitLine: { show: false }
      }
    ],
    yAxis: [
      {
        type: 'value', scale: true,
        splitLine: { lineStyle: { type: 'dashed', color: '#e8e8e8' } },
        axisLabel: { formatter: '{value} 元', fontSize: 10 }
      },
      {
        type: 'value', gridIndex: 1,
        splitLine: { show: false },
        axisLabel: {
          fontSize: 10,
          formatter: function(v: number) {
            if (v >= 1e8) return (v / 1e8).toFixed(1) + '亿';
            if (v >= 1e4) return (v / 1e4).toFixed(1) + '万';
            return v.toFixed(0);
          }
        }
      }
    ],
    dataZoom: [
      { type: 'inside', xAxisIndex: [0, 1], start: 0, end: 100 },
      {
        type: 'slider', height: 18, bottom: 2,
        borderColor: '#ddd',
        fillerColor: 'rgba(24,144,255,0.1)',
        handleStyle: { color: '#1890ff' },
        labelFormatter: function(v: number) { return dates[v]?.slice(5) || ''; },
        start: 0, end: 100
      }
    ],
    series: [
      {
        name: '收盘价',
        type: 'line',
        data: closes,
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 2, color: '#1890ff' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(24,144,255,0.25)' },
            { offset: 1, color: 'rgba(24,144,255,0.02)' }
          ])
        },
        markLine: {
          silent: true,
          data: [
            { type: 'average', name: '均价', label: { formatter: '均价: {c}', fontSize: 10 } }
          ],
          lineStyle: { color: '#fa8c16', type: 'dashed', width: 1 }
        }
      },
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: props.klineData.map(function(k, i) {
          return { value: volumes[i], itemStyle: { color: volColors[i] } };
        }),
        barWidth: '50%'
      }
    ]
  });
}

var techItems = computed(function() {
  if (!props.report?.technical_summary) return [];
  var map = {
    'latest_close': { label: '最新收盘价', desc: '最近一个交易日的收盘价格' },
    'ma_5': { label: 'MA5 均线(5天)', desc: '过去5个交易日收盘价的平均值' },
    'ma_10': { label: 'MA10 均线(10天)', desc: '过去10个交易日收盘价的平均值' },
    'ma_20': { label: 'MA20 均线(20天)', desc: '过去20个交易日收盘价的平均值' },
    'ma_60': { label: 'MA60 均线(60天)', desc: '过去60个交易日(约3个月)收盘价的平均值' },
    'ema_12': { label: 'EMA12 指数均线(12天)', desc: '12日指数移动平均线，对近期价格更敏感' },
    'ema_26': { label: 'EMA26 指数均线(26天)', desc: '26日指数移动平均线，反映中期趋势' },
    'macd': { label: 'MACD 差值(DIF)', desc: '快速线与慢速线的差值，判断趋势强度' },
    'macd_signal': { label: 'MACD 信号线(DEA)', desc: 'DIF的9日均线，确认趋势方向' },
    'macd_histogram': { label: 'MACD 柱状图', desc: 'DIF与DEA的差值乘以2，柱越长趋势越强' },
    'rsi': { label: 'RSI 相对强弱(14天)', desc: '衡量近期涨跌力度，>70超买，<30超卖' },
    'k': { label: 'K值(快线)', desc: 'KDJ指标的快线，反应最灵敏' },
    'd': { label: 'D值(慢线)', desc: 'KDJ指标的慢线，K值的3日平均' },
    'j': { label: 'J值(最快线)', desc: 'KDJ指标的最快线，K和D的差值放大' },
    'boll_upper': { label: '布林上轨(压力位)', desc: '价格上方的压力线，触碰后可能回调' },
    'boll_mid': { label: '布林中轨(均线)', desc: '布林通道的中线，即20日均线' },
    'boll_lower': { label: '布林下轨(支撑位)', desc: '价格下方的支撑线，触碰后可能反弹' },
    'atr': { label: 'ATR 平均波幅', desc: '平均真实波幅，衡量价格波动的大小' },
    'obv': { label: 'OBV 能量潮', desc: '通过成交量来验证价格趋势的可靠性' },
    'volume_avg': { label: '平均成交量', desc: '最近交易日的平均成交量' },
  };
  var ts = props.report.technical_summary;
  var items = [];
  for (var key in map) {
    if (ts[key] != null && ts[key] !== '' && ts[key] !== '--') {
      var v = ts[key];
      var val = '';
      if (typeof v === 'number') {
        if (['volume_avg', 'obv'].indexOf(key) >= 0) {
          val = Math.abs(v) >= 1e4 ? (v / 1e4).toFixed(2) + '万' : v.toFixed(0);
        } else {
          val = v.toFixed(2);
        }
      } else {
        val = String(v).slice(0, 30);
      }
      items.push({ label: map[key].label, value: val, desc: map[key].desc });
    }
  }
  return items;
});

var riskItems = computed(function() {
  if (!props.report?.risk_summary) return [];
  var rs = props.report.risk_summary;
  var items = [];
  var riskMap = {
    'concentration': { label: '持股集中度', desc: '前十大股东持股比例' },
    'pe_basis': { label: '市盈率水平', desc: '当前PE与行业平均PE的比较' },
    'price_volatility': { label: '价格波动性', desc: '近期股价的波动幅度' },
    'volume_trend': { label: '成交量趋势', desc: '近期成交量相比之前的增减情况' },
  };
  for (var key in riskMap) {
    if (rs[key] != null && rs[key] !== '') {
      var info = riskMap[key];
      var v = rs[key];
      var val = '';
      if (typeof v === 'number') {
        if (key === 'concentration' || key === 'pe_basis') {
          val = v.toFixed(1) + '%';
        } else {
          val = v.toFixed(2);
        }
      } else {
        val = String(v).slice(0, 30);
      }
      var level_val = 'info';
      if (typeof v === 'number') {
        if (Math.abs(v) > 0.5) level_val = 'high';
        else if (Math.abs(v) > 0.15) level_val = 'mid';
      }
      items.push({ label: info.label, value: val, desc: info.desc, level: level_val });
    }
  }
  var off = rs['official_disclosure'];
  if (off && typeof off === 'object' && off.status !== 'disabled') {
    if (off.status === 'unavailable') {
      items.push({ label: '官方公告风险', value: '不可用', desc: '官方公告风险数据暂时无法获取', level: 'info' });
    } else if (off.signals && Array.isArray(off.signals)) {
      for (var j = 0; j < off.signals.length; j++) {
        var s = off.signals[j];
        items.push({
          label: '官方公告提示',
          value: s.type || '--',
          desc: s.detail || '',
          level: s.severity === 'high' ? 'high' : 'mid'
        });
      }
    }
  }
  return items;
});

var renderedHtml = computed(function() {
  if (!props.report?.report_markdown) return '<p style="color:#999;text-align:center;padding:40px 0">暂无分析数据</p>';
  var md = props.report.report_markdown;
  
  var TERM_MAP = {
    'MACD': '指数平滑异同移动平均线，用于判断趋势强弱和买卖时机',
    'RSI': '相对强弱指标（0-100），衡量近期涨跌力度，>70超买风险，<30超卖机会',
    'KDJ': '随机指标，通过K快线、D慢线和J最快线判断短期买卖信号',
    'BOLL': '布林通道（布林带），由上轨（压力位）、中轨（均线）、下轨（支撑位）组成',
    'MA5': '5日均线（5日移动平均线），过去5个交易日的平均价格，反映超短期趋势',
    'MA10': '10日均线，过去10个交易日（约2周）的平均价格',
    'MA20': '20日均线，过去20个交易日（约1个月）的平均价格，中期趋势参考',
    'MA60': '60日均线，过去60个交易日（约3个月）的平均价格，中长期趋势参考',
    'EMA': '指数移动平均线，对近期价格变化更敏感',
    'ATR': '平均真实波幅（Average True Range），衡量价格波动幅度，数值越大波动越剧烈',
    'OBV': '能量潮（On-Balance Volume），通过成交量变化验证价格趋势的可靠性',
    'DIF': '差离值（快线），EMA12与EMA26的差值，反映短期与长期趋势的差距',
    'DEA': '信号线（慢线），DIF的9日指数平均线，确认趋势方向',
    'PE': '市盈率（Price-to-Earnings Ratio），股价与每股盈利比值，衡量估值高低',
    'PB': '市净率（Price-to-Book Ratio），股价与每股净资产的比值',
    'ROE': '净资产收益率（Return on Equity），净利润/净资产，衡量公司盈利能力',
    'ROA': '总资产收益率（Return on Assets），净利润/总资产，衡量资产利用效率',
    'EPS': '每股收益（Earnings Per Share），公司每股股票能分到的利润金额',
    'PEG': '市盈率相对盈利增长比率，PE除以盈利增长率，衡量估值是否合理',
    'TTM': '滚动12个月（Trailing Twelve Months），最近连续12个月的财务数据',
    '毛利率': '毛利润占营收的比例，越高说明产品越有竞争力',
    '净利率': '净利润占营收的比例，越高说明盈利能力越强',
    '资产负债率': '总负债占总资产的比例，越高财务风险越大',
    '流动比率': '流动资产与流动负债的比值，衡量短期偿债能力',
    '速动比率': '速动资产与流动负债的比值，更严格的短期偿债能力指标',
    '股息率': '每股分红与股价的比例，衡量现金回报水平',
    '质押比例': '大股东质押股份占其持股的比例，越高平仓风险越大',
    '商誉': '收购价格超过净资产的部分，若减值会影响利润',
    '现金流': '公司经营活动中产生的现金净流量，真金白银的盈利能力',
    '支撑位': '股价下跌时可能遇到买盘的价格区间',
    '压力位': '股价上涨时可能遇到卖盘的价格区间',
    '趋势线': '连接股价高低点的斜线，显示价格运行方向',
    '金叉': '短期均线上穿长期均线，通常为买入信号',
    '死叉': '短期均线下穿长期均线，通常为卖出信号',
    '超买': '买入过多人气过高，股价可能回调下跌',
    '超卖': '卖出过多人气过低，股价可能反弹上涨',
  };
  
  for (var t in TERM_MAP) {
    if (md.indexOf(t) >= 0) {
      var escapedTerm = t.replace(/[.*+?^|()[\]\\\\]/g, '\\\\$&');
      md = md.replace(escapedTerm, t + '<sup class="term-note" title="' + TERM_MAP[t] + '">?</sup>');
    }
  }
  
  var html = md
    .replace(/### (.+)/g, '<h3 class="report-h3">$1</h3>')
    .replace(/## (.+)/g, '<h2 class="report-h2">$1</h2>')
    .replace(/# (.+)/g, '<h1 class="report-h1">$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong class="report-strong">$1</strong>')
    .replace(/\*(.+?)\*/g, '<em class="report-em">$1</em>')
    .replace(/^- (.+)$/gm, '<li class="report-li">$1</li>')
    .replace(/\n{2,}/g, '</p><p class="report-p">')
    .replace(/\n/g, '<br/>');
  
  return '<div class="report-body"><p class="report-p">' + html + '</p></div>';
});

var resizeHandler = null;
onMounted(function() {
  nextTick(function() { renderChart(); });
  resizeHandler = function() { if (chartInstance) chartInstance.resize(); };
  window.addEventListener('resize', resizeHandler);
});
watch(function() { return props.klineData; }, function() {
  nextTick(function() { renderChart(); });
}, { deep: true });
onUnmounted(function() {
  if (chartInstance) { chartInstance.dispose(); chartInstance = null; }
  if (resizeHandler) { window.removeEventListener('resize', resizeHandler); }
});
</script>

<style scoped>
.analysis-report { max-width: 100%; }
.report-card { border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.04); }
.chart-container { width: 100%; height: 420px; }
.chart-note { font-size: 12px; color: #999; margin-top: 8px; line-height: 1.6; }

.indicator-card {
  border-radius: 8px;
  padding: 10px 12px;
  transition: all 0.2s;
  border-left: 3px solid #e8e8e8;
  background: #fafafa;
}
.indicator-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.indicator-0 { border-left-color: #1890ff; background: #f0f7ff; }
.indicator-1 { border-left-color: #52c41a; background: #f0fff0; }
.indicator-2 { border-left-color: #fa8c16; background: #fff7f0; }
.indicator-3 { border-left-color: #8a2be2; background: #f8f0ff; }
.indicator-4 { border-left-color: #f5222d; background: #fff0f0; }
.indicator-5 { border-left-color: #13c2c2; background: #f0ffff; }

.indicator-label { font-size: 11px; font-weight: 600; color: #888; margin-bottom: 3px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.indicator-value { font-size: 18px; font-weight: 700; color: #333; line-height: 1.3; }
.indicator-value.value-up { color: #f5222d; }
.indicator-value.value-down { color: #52c41a; }
.indicator-desc { font-size: 10px; color: #aaa; margin-top: 2px; line-height: 1.3; }
.indicator-note { font-size: 12px; color: #bbb; margin-top: 12px; }

.risk-card { border-radius: 8px; padding: 10px 12px; border: 1px solid #eee; transition: all 0.2s; }
.risk-card:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.risk-high { border-left: 3px solid #f5222d; background: #fff2f0; }
.risk-mid { border-left: 3px solid #fa8c16; background: #fffbe6; }
.risk-default { border-left: 3px solid #1890ff; background: #f0f7ff; }
.risk-label { font-size: 12px; font-weight: 600; color: #666; margin-bottom: 4px; display: flex; align-items: center; gap: 6px; }
.risk-tag { flex-shrink: 0; }
.risk-value { font-size: 16px; font-weight: 700; color: #333; }
.risk-desc { font-size: 11px; color: #999; margin-top: 2px; }

.report-content { font-size: 14px; line-height: 1.9; color: #444; }
.report-body { padding: 4px 0; }
.report-p { margin: 0 0 12px; line-height: 1.9; }
.report-h1 { font-size: 20px; color: #111; border-bottom: 2px solid #1890ff; padding-bottom: 8px; margin: 28px 0 14px; }
.report-h2 { font-size: 17px; color: #222; border-bottom: 1px solid #e0e0e0; padding-bottom: 6px; margin: 24px 0 12px; }
.report-h3 { font-size: 15px; color: #333; border-left: 3px solid #1890ff; padding-left: 10px; margin: 20px 0 10px; }
.report-strong { color: #1890ff; font-weight: 600; }
.report-em { color: #666; font-style: italic; }
.report-li { list-style: disc; margin-left: 20px; margin-bottom: 4px; line-height: 1.8; }
:deep(.term-note) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #1890ff;
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  cursor: help;
  margin-left: 2px;
  vertical-align: super;
  line-height: 1;
}
:deep(.term-note:hover) { background: #096dd9; }

@media (max-width: 768px) {
  .chart-container { height: 300px; }
  .indicator-card { padding: 8px 10px; }
  .indicator-value { font-size: 15px; }
  .risk-card { padding: 8px 10px; }
  .report-content { font-size: 13px; }
  .report-h1 { font-size: 18px; }
  .report-h2 { font-size: 16px; }
  .report-h3 { font-size: 14px; }
}
@media (max-width: 480px) {
  .chart-container { height: 240px; }
  .indicator-value { font-size: 14px; }
  .indicator-label { font-size: 10px; }
  .report-content { font-size: 12px; }
  .report-h1 { font-size: 16px; }
  .report-h2 { font-size: 15px; }
  .report-h3 { font-size: 13px; }
}
</style>
