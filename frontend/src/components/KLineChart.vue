<template>
  <div ref="chartRef" class="chart-container"></div>
</template>
<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount } from 'vue';
import * as echarts from 'echarts';
import type { KlineRecord } from '../stores/stock';
const props = defineProps<{ data: KlineRecord[] }>();
const chartRef = ref<HTMLElement>();
let chartInstance: echarts.ECharts | null = null;
function renderChart() {
  if (!chartRef.value || !props.data.length) return;
  if (!chartInstance) chartInstance = echarts.init(chartRef.value);
  const dates = props.data.map(d => d.trade_date.slice(5, 10));
  const ohlc = props.data.map(d => [d.open_price, d.close_price, d.low_price, d.high_price]);
  const volume = props.data.map(d => d.volume);
  const ma5 = calcMA(props.data, 5);
  const ma10 = calcMA(props.data, 10);
  const ma20 = calcMA(props.data, 20);
  chartInstance.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
    legend: { data: ['K线', 'MA5', 'MA10', 'MA20', '成交量'], textStyle: { color: '#999' } },
    grid: [{ left: '5%', right: '5%', top: 60, height: '55%' }, { left: '5%', right: '5%', top: '78%', height: '15%' }],
    xAxis: [{ type: 'category', data: dates, axisLine: { lineStyle: { color: '#333' } }, axisLabel: { color: '#999' }, gridIndex: 0 }, { type: 'category', data: dates, axisLine: { lineStyle: { color: '#333' } }, axisLabel: { show: false }, gridIndex: 1 }],
    yAxis: [{ scale: true, splitLine: { lineStyle: { color: '#222' } }, axisLabel: { color: '#999' }, gridIndex: 0 }, { scale: true, splitLine: { show: false }, axisLabel: { color: '#999' }, gridIndex: 1 }],
    series: [
      { name: 'K线', type: 'candlestick', data: ohlc, itemStyle: { color: '#00c853', color0: '#ff1744', borderColor: '#00c853', borderColor0: '#ff1744' } },
      { name: 'MA5', type: 'line', data: ma5, smooth: true, lineStyle: { width: 1, color: '#fdd835' }, symbol: 'none' },
      { name: 'MA10', type: 'line', data: ma10, smooth: true, lineStyle: { width: 1, color: '#42a5f5' }, symbol: 'none' },
      { name: 'MA20', type: 'line', data: ma20, smooth: true, lineStyle: { width: 1, color: '#ab47bc' }, symbol: 'none' },
      { name: '成交量', type: 'bar', data: volume, xAxisIndex: 1, yAxisIndex: 1, itemStyle: { color: (p: any) => { const item = props.data[p.dataIndex]; return item && item.close_price >= item.open_price ? '#00c853' : '#ff1744'; } } },
    ],
  });
}
function calcMA(data: KlineRecord[], days: number) { return data.map((_, i) => { if (i < days - 1) return '-'; const slice = data.slice(i - days + 1, i + 1); return +(slice.reduce((s, d) => s + d.close_price, 0) / days).toFixed(2); }); }
watch(() => props.data, renderChart, { deep: true });
onMounted(() => { renderChart(); window.addEventListener('resize', () => chartInstance?.resize()); });
onBeforeUnmount(() => { chartInstance?.dispose(); chartInstance = null; });
</script>
<style scoped>.chart-container { width: 100%; height: 400px; }</style>
