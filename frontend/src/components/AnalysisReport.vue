<template>
  <div v-if="report">
    <n-card title="价格趋势" size="small" class="mb-24">
      <div ref="chartRef" style="width:100%;height:400px"></div>
    </n-card>

    <n-card title="技术指标摘要" size="small" class="mb-24">
      <n-grid :cols="4" :x-gap="12" :y-gap="12" responsive="screen">
        <n-grid-item v-for="(val, key) in techItems" :key="key">
          <n-statistic :label="key" :value="val" />
        </n-grid-item>
      </n-grid>
    </n-card>

    <n-card v-if="riskItems.length > 0" title="风险提示" size="small" class="mb-24">
      <n-timeline>
        <n-timeline-item v-for="(item, i) in riskItems" :key="i" :type="item.type" :content="item.text" :time="item.time" />
      </n-timeline>
    </n-card>

    <n-card title="AI 投资分析报告" size="small" class="mb-24">
      <n-spin :show="loading">
        <div class="report-content" v-html="renderedHtml"></div>
      </n-spin>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, watch, nextTick } from "vue";
import * as echarts from "echarts";
import type { AnalysisReport, KlineRecord, Quote } from "../stores/stock";

const props = defineProps<{ report: AnalysisReport | null; klineData?: KlineRecord[]; quote?: Quote | null; loading?: boolean }>();
const chartRef = ref<HTMLDivElement>();

function renderChart() {
  if (!chartRef.value || !props.klineData || props.klineData.length === 0) return;
  const chart = echarts.init(chartRef.value);
  const dates = props.klineData.map(k => k.trade_date.slice(5));
  const closes = props.klineData.map(k => k.close_price);
  const volumes = props.klineData.map(k => k.volume);
  chart.setOption({
    tooltip: { trigger: "axis", axisPointer: { type: "cross" } },
    grid: [{ left: 60, right: 20, top: 30, height: "55%" }, { left: 60, right: 20, top: "75%", height: "15%" }],
    xAxis: [
      { type: "category", data: dates, axisLine: { onZero: false }, axisLabel: { rotate: 45, fontSize: 10 } },
      { type: "category", gridIndex: 1, data: dates, axisLabel: { show: false } }
    ],
    yAxis: [
      { type: "value", scale: true, splitLine: { show: true } },
      { type: "value", gridIndex: 1, splitLine: { show: false }, axisLabel: { show: true } }
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
        itemStyle: { color: (p: any) => p.dataIndex > 0 && p.data < volumes[p.dataIndex - 1] ? "#52c41a" : "#f5222d" }
      }
    ]
  });
}

const techItems = computed(() => {
  const ts = props.report?.technical_summary || {};
  const items: Record<string, string> = {};
  for (const [k, v] of Object.entries(ts)) {
    items[k] = String(v).slice(0, 30);
  }
  if (Object.keys(items).length === 0) { items["MA"] = "--"; items["MACD"] = "--"; items["RSI"] = "--"; items["KDJ"] = "--"; }
  return items;
});

const riskItems = computed(() => {
  const rs = props.report?.risk_summary || {};
  const items: { type: "warning" | "error" | "info"; text: string; time: string }[] = [];
  for (const [k, v] of Object.entries(rs)) {
    items.push({ type: "warning", text: k + ": " + String(v).slice(0, 120), time: props.report?.data_timestamp?.slice(0, 10) || "" });
  }
  return items;
});

const renderedHtml = computed(() => {
  if (!props.report?.report_markdown) return "<p style=\"color:#999\">暂无分析数据</p>";
  let html = props.report.report_markdown
    .replace(/### (.+)/g, "<h3 style=\"color:#333;margin:20px 0 10px;border-left:3px solid #1890ff;padding-left:10px\">$1</h3>")
    .replace(/## (.+)/g, "<h2 style=\"color:#222;margin:24px 0 12px;border-bottom:2px solid #e8e8e8;padding-bottom:6px\">$1</h2>")
    .replace(/# (.+)/g, "<h1 style=\"color:#111;margin:28px 0 14px;font-size:20px\">$1</h1>")
    .replace(/\*\*(.+?)\*\*/g, "<strong style=\"color:#1890ff\">$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/^- (.+)$/gm, "<li style=\"list-style:disc;margin-left:20px;line-height:1.8\">$1</li>")
    .replace(/\n/g, "<br/>");
  return "<div style=\"line-height:1.8;font-size:14px;color:#444\">" + html + "</div>";
});

onMounted(() => { nextTick(renderChart); });
watch(() => props.klineData, () => { nextTick(renderChart); });
</script>

<style scoped>
.report-content { line-height: 1.8; font-size: 14px; }
.report-content :deep(h1),
.report-content :deep(h2),
.report-content :deep(h3) { margin: 16px 0 8px; }
.report-content :deep(li) { margin-left: 20px; }
.mb-24 { margin-bottom: 24px; }
</style>
