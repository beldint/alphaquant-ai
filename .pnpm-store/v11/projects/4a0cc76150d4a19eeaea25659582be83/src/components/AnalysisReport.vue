<template>
  <div v-if="report">
    <n-card title="价格趋势图" size="small" class="mb-24">
      <div v-if="klineData && klineData.length > 0">
        <div ref="chartRef" style="width:100%;height:400px"></div>
        <n-p depth="3" style="font-size:12px;margin-top:8px;color:#888">
          说明：上图为该股票最新 {{ klineData.length || 0 }} 个交易日收盘价走势（蓝色折线）及成交量（红绿柱）。红色柱表示下跌日，绿色柱表示上涨日。数据来源为公开行情数据，不构成投资建议。
        </n-p>
      </div>
      <n-empty v-else description="暂无实时K线数据，无法显示趋势图" />
    </n-card>

    <n-card title="技术指标摘要" size="small" class="mb-24">
      <n-grid :cols="2" :x-gap="12" :y-gap="12" responsive="screen">
        <n-grid-item v-for="(item, idx) in techItems" :key="idx">
          <div class="indicator-card">
            <div class="indicator-label">{{ item.label }}
              <n-tooltip trigger="hover" placement="top">
                <template #trigger>
                  <span class="info-icon">ⓘ</span>
                </template>
                <span style="font-size:12px">{{ item.desc }}</span>
              </n-tooltip>
            </div>
            <div class="indicator-value">{{ item.value }}</div>
          </div>
        </n-grid-item>
      </n-grid>
    </n-card>

    <n-card v-if="riskItems.length > 0" title="风险指标" size="small" class="mb-24">
      <n-grid :cols="2" :x-gap="12" :y-gap="12" responsive="screen">
        <n-grid-item v-for="(item, i) in riskItems" :key="i">
          <div class="indicator-card">
            <div class="indicator-label">{{ item.label }}</div>
            <div class="indicator-value" :style="{ color: item.level === 'high' ? '#f5222d' : item.level === 'mid' ? '#fa8c16' : '#333' }">{{ item.value }}</div>
            <div class="indicator-desc">{{ item.desc }}</div>
          </div>
        </n-grid-item>
      </n-grid>
    </n-card>

    <n-card title="AI 投资分析报告" size="small" class="mb-24">
      <n-spin :show="loading">
        <div class="report-content" v-html="renderedHtml"></div>
      </n-spin>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, watch, nextTick, onUnmounted } from "vue";
import * as echarts from "echarts";
import type { AnalysisReport, KlineRecord, Quote } from "../stores/stock";

const props = defineProps<{ report: AnalysisReport | null; klineData?: KlineRecord[]; quote?: Quote | null; loading?: boolean }>();
const chartRef = ref<HTMLDivElement>();
let chartInstance: echarts.ECharts | null = null;

function renderChart() {
  if (!chartRef.value || !props.klineData || props.klineData.length === 0) return;
  if (chartInstance) { chartInstance.dispose(); }
  chartInstance = echarts.init(chartRef.value);
  var dates = props.klineData.map(function(k) { return k.trade_date.slice(5); });
  var closes = props.klineData.map(function(k) { return k.close_price; });
  var volumes = props.klineData.map(function(k) { return k.volume; });
  chartInstance.setOption({
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "cross" },
      formatter: function(params) {
        if (!params || params.length === 0) return "";
        var res = "<strong>" + params[0].axisValue + "</strong><br/>";
        for (var p = 0; p < params.length; p++) {
          if (params[p].seriesName === "收盘价") {
            res += "收盘价：<strong>" + params[p].value + "</strong> 元<br/>";
          } else if (params[p].seriesName === "成交量") {
            res += "成交量：" + Number(params[p].value).toLocaleString() + " 手<br/>";
          }
        }
        return res;
      }
    },
    legend: { data: ["收盘价", "成交量"], top: 0, textStyle: { fontSize: 11 } },
    grid: [
      { left: 60, right: 20, top: 40, height: "50%" },
      { left: 60, right: 20, top: "72%", height: "18%" }
    ],
    xAxis: [
      { type: "category", data: dates, axisLine: { onZero: false }, axisLabel: { rotate: 45, fontSize: 10 } },
      { type: "category", gridIndex: 1, data: dates, axisLabel: { show: false } }
    ],
    yAxis: [
      { type: "value", scale: true, splitLine: { show: true }, axisLabel: { formatter: "{value} 元" } },
      { type: "value", gridIndex: 1, splitLine: { show: false }, axisLabel: { show: true, formatter: function(v) { return v >= 10000 ? (v / 10000).toFixed(1) + "万" : v.toFixed(0); } } }
    ],
    dataZoom: [{ type: "inside" }, { type: "slider", height: 20, bottom: 5 }],
    series: [
      {
        name: "收盘价", type: "line", data: closes, smooth: true, symbol: "none",
        lineStyle: { width: 2, color: "#1890ff" },
        areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: "rgba(24,144,255,0.3)" },
          { offset: 1, color: "rgba(24,144,255,0.02)" }
        ]) }
      },
      {
        name: "成交量", type: "bar", xAxisIndex: 1, yAxisIndex: 1, data: volumes,
        itemStyle: { color: function(p) { return p.dataIndex > 0 && p.data < volumes[p.dataIndex - 1] ? "#52c41a" : "#f5222d"; } }
      }
    ]
  });
  chartInstance.resize();
}

var TECH_LABELS = {
  latest_close:   { label: "最新收盘价", desc: "最近一个交易日的收盘价格" },
  ma_5:           { label: "5日均线 (MA5)", desc: "过去5个交易日收盘价的平均值，反映短期走势" },
  ma_20:          { label: "20日均线 (MA20)", desc: "过去20个交易日收盘价的平均值，反映中期走势" },
  ema_12:         { label: "12日指数均线 (EMA12)", desc: "对近期价格赋予更高权重的12日均线，反应更快" },
  macd:           { label: "MACD值", desc: "指数平滑异同移动平均线，判断趋势强弱和方向" },
  macd_signal:    { label: "MACD信号线", desc: "MACD的9日均线，用于确认买卖信号" },
  rsi:            { label: "相对强弱指标 (RSI)", desc: "衡量近期涨跌力度，值>70超买，<30超卖" },
  kdj_k:          { label: "KDJ-K值（快线）", desc: "随机指标的快线，反映短期价格动量" },
  kdj_d:          { label: "KDJ-D值（慢线）", desc: "随机指标的慢线，用于确认趋势" },
  boll_upper:     { label: "布林上轨 (BOLL上)", desc: "压力位，价格触及上轨可能回落" },
  boll_middle:    { label: "布林中轨 (BOLL中)", desc: "20日均线，多空分水岭" },
  boll_lower:     { label: "布林下轨 (BOLL下)", desc: "支撑位，价格触及下轨可能反弹" },
  atr:            { label: "平均真实波幅 (ATR)", desc: "衡量价格波动幅度，值越大波动越剧烈" },
  obv:            { label: "能量潮 (OBV)", desc: "通过成交量验证价格趋势的可信度" },
};

var RISK_LABELS = {
  annualized_volatility:    { label: "年化波动率", desc: "衡量股价年度波动程度，越大风险越高。<30%较低，30-50%中等，>50%较高" },
  max_drawdown:            { label: "最大回撤", desc: "从最高点跌落到最低点的最大跌幅，反映历史最差情况" },
  data_points:              { label: "数据样本", desc: "用于分析的交易日数量" },
  recent_60d_high:          { label: "60日最高价", desc: "近60个交易日的最高价格" },
  recent_60d_low:           { label: "60日最低价", desc: "近60个交易日的最低价格" },
  distance_to_60d_high_pct: { label: "距60日高点距离", desc: "当前价格距离60日最高点的百分比，负值意味着还没超过高点" },
  distance_to_60d_low_pct:  { label: "距60日低点距离", desc: "当前价格距离60日最低点的百分比，正值意味着已经回升" },
};

var techItems = computed(function() {
  var ts = props.report?.technical_summary || {};
  var items = [];
  var keys = Object.keys(ts);
  for (var i = 0; i < keys.length; i++) {
    var k = keys[i];
    var info = TECH_LABELS[k];
    if (!info) continue;
    var v = ts[k];
    var val = "--";
    if (v != null) {
      if (typeof v === "number") {
        val = Math.abs(v) >= 10000 ? v.toFixed(0) : v.toFixed(2);
      } else {
        val = String(v).slice(0, 30);
      }
    }
    items.push({ label: info.label, value: val, desc: info.desc });
  }
  if (items.length === 0) {
    items.push({ label: "暂无数据", value: "--", desc: "技术指标数据不可用" });
  }
  return items;
});

var riskItems = computed(function() {
  var rs = props.report?.risk_summary || {};
  var items = [];
  var keys = Object.keys(rs);
  for (var i = 0; i < keys.length; i++) {
    var k = keys[i];
    var info = RISK_LABELS[k];
    if (!info) continue;
    var v = rs[k];
    var val = "--";
    if (v != null) {
      if (typeof v === "number") {
        if (k.indexOf("_pct") >= 0) {
          val = v.toFixed(2) + "%";
        } else {
          val = Math.abs(v) >= 10000 ? v.toFixed(0) : v.toFixed(2);
        }
      } else {
        val = String(v).slice(0, 30);
      }
    }
    var level = "info";
    if (typeof v === "number") {
      if (Math.abs(v) > 0.5) level = "high";
      else if (Math.abs(v) > 0.15) level = "mid";
    }
    items.push({ label: info.label, value: val, desc: info.desc, level: level });
  }
  var off = rs["official_disclosure"];
  if (off && typeof off === "object" && off.status !== "disabled") {
    if (off.status === "unavailable") {
      items.push({ label: "官方公告风险", value: "不可用", desc: "官方公告风险数据暂时无法获取", level: "info" });
    } else if (off.signals && Array.isArray(off.signals)) {
      for (var j = 0; j < off.signals.length; j++) {
        var s = off.signals[j];
        items.push({ label: "官方公告提示", value: s.type || "--", desc: s.detail || "", level: s.severity === "high" ? "high" : "mid" });
      }
    }
  }
  return items;
});

var renderedHtml = computed(function() {
  if (!props.report?.report_markdown) return '<p style="color:#999">暂无分析数据</p>';
  var md = props.report.report_markdown;
  var TERM_MAP = {
    "MACD": "指数平滑异同移动平均线，用于判断趋势强弱",
    "RSI": "相对强弱指标，用于衡量近期涨跌力度",
    "KDJ": "随机指标，用于判断短期买卖信号",
    "BOLL": "布林通道，用于判断压力位和支撑位",
    "MA5": "5日均线，过去5个交易日的平均价格",
    "MA20": "20日均线，过去20个交易日的平均价格",
    "EMA": "指数移动平均线，对近期价格更敏感",
    "ATR": "平均真实波幅，衡量价格波动幅度",
    "OBV": "能量潮，通过成交量验证趋势",
    "PE": "市盈率，估值指标，衡量股价是否贵",
    "PB": "市净率，估值指标，比较股价与净资产",
    "ROE": "净资产收益率，衡量公司盈利能力",
    "EPS": "每股收益，公司每股股票的盈利金额",
  };
  var termKeys = Object.keys(TERM_MAP);
  for (var t = 0; t < termKeys.length; t++) {
    var term = termKeys[t];
    var explanation = TERM_MAP[term];
    var idx = md.indexOf(term);
    if (idx >= 0) {
      var escTerm = term;
      if (term.indexOf("+") >= 0) { escTerm = term.replace("+", "\\+"); }
      if (term.indexOf(".") >= 0) { escTerm = term.replace(/[.+]/g, "\\$&"); }
      var parts = md.split(escTerm);
      if (parts.length > 1) {
        md = parts.join(term + "（" + explanation + "）");
      }
    }
  }
  var html = md
    .replace(/### (.+)/g, '<h3 style="color:#333;margin:20px 0 10px;border-left:3px solid #1890ff;padding-left:10px">$1</h3>')
    .replace(/## (.+)/g, '<h2 style="color:#222;margin:24px 0 12px;border-bottom:2px solid #e8e8e8;padding-bottom:6px">$1</h2>')
    .replace(/# (.+)/g, '<h1 style="color:#111;margin:28px 0 14px;font-size:20px">$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong style="color:#1890ff">$1</strong>')
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/^- (.+)$/gm, '<li style="list-style:disc;margin-left:20px;line-height:1.8">$1</li>')
    .replace(/\n/g, "<br/>");
  return '<div style="line-height:1.8;font-size:14px;color:#444">' + html + "</div>";
});

var resizeHandler = null;
onMounted(function() {
  nextTick(function() { renderChart(); });
  resizeHandler = function() { if (chartInstance) chartInstance.resize(); };
  window.addEventListener("resize", resizeHandler);
});
watch(function() { return props.klineData; }, function() { nextTick(function() { renderChart(); }); }, { deep: true });
onUnmounted(function() {
  if (chartInstance) { chartInstance.dispose(); chartInstance = null; }
  if (resizeHandler) { window.removeEventListener("resize", resizeHandler); }
});
</script>

<style scoped>
.indicator-card {
  background: #f9f9f9;
  border-radius: 6px;
  padding: 8px 10px;
  transition: background 0.2s;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 52px;
}
.indicator-card:hover {
  background: #f0f5ff;
}
.indicator-label {
  font-size: 11px;
  font-weight: 600;
  color: #888;
  margin-bottom: 2px;
  display: flex;
  align-items: center;
  gap: 3px;
}
.indicator-value {
  font-size: 16px;
  font-weight: 700;
  color: #333;
}
.info-icon {
  cursor: help;
  color: #bbb;
  font-size: 10px;
  line-height: 1;
}
.indicator-desc {
  font-size: 11px;
  color: #999;
  line-height: 1.4;
}
.report-content { line-height: 1.8; font-size: 14px; }
.report-content :deep(h1),
.report-content :deep(h2),
.report-content :deep(h3) { margin: 16px 0 8px; }
.report-content :deep(li) { margin-left: 20px; }
.mb-24 { margin-bottom: 24px; }
@media (max-width: 768px) {
  .indicator-value { font-size: 15px; }
}
@media (max-width: 480px) {
  .indicator-value { font-size: 14px; }
}
</style>
