<template>
  <div ref="chartRef" class="kline-chart"></div>
</template>
<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';
import * as echarts from 'echarts';
import type { KlineRecord } from '../stores/stock';
const props = defineProps<{ data: KlineRecord[] }>();
const chartRef = ref<HTMLDivElement | null>(null);
let chart: echarts.ECharts | null = null;
const options = computed(() => {
  const dates = props.data.map(d => d.trade_date.slice(5, 10));
  const ohlc = props.data.map(d => [d.open_price, d.close_price, d.low_price, d.high_price]);
  const volumes = props.data.map(d => d.volume);
  const amounts = props.data.map(d => d.amount);
  return {
    backgroundColor: 'transparent', grid: [{ left: '5%', right: '15%', top: '8%', height: '55%' }, { left: '5%', right: '15%', top: '72%', height: '18%' }],
    xAxis: [{ type: 'category', data: dates, axisLine: { lineStyle: { color: '#333' } }, axisLabel: { color: '#999', fontSize: 10 } }, { type: 'category', gridIndex: 1, data: dates, axisLabel: { show: false } }],
    yAxis: [{ scale: true, splitLine: { lineStyle: { color: '#222' } }, axisLabel: { color: '#999', fontSize: 10 } }, { scale: true, gridIndex: 1, splitLine: { show: false }, axisLabel: { color: '#999', fontSize: 10 }, position: 'right' }],
    series: [
      { type: 'candlestick', data: ohlc, itemStyle: { color: '#00c853', color0: '#ff1744', borderColor: '#00c853', borderColor0: '#ff1744' } },
      { type: 'bar', xAxisIndex: 1, yAxisIndex: 1, data: volumes.map((v, i) => ({ value: v, itemStyle: { color: props.data[i].close_price >= props.data[i].open_price ? '#00c853' : '#ff1744' } })) },
    ],
    tooltip: { trigger: 'axis', axisPointer: { type: 'cross' }, backgroundColor: '#1a1a22', borderColor: '#333', textStyle: { color: '#e5e5e5', fontSize: 11 } },
    dataZoom: [{ type: 'inside', xAxisIndex: [0, 1], start: 0, end: 100 }],
  };
});
function resize(): void { chart?.resize(); }
onMounted(() => { if (chartRef.value) { chart = echarts.init(chartRef.value, undefined, { renderer: 'svg' }); chart.setOption(options.value); window.addEventListener('resize', resize); } });
onUnmounted(() => { window.removeEventListener('resize', resize); chart?.dispose(); });
watch(() => props.data, () => { if (chart) { chart.setOption(options.value, true); } }, { deep: true });
</script>
<style scoped>
.kline-chart { width: 100%; min-height: 260px; height: 400px; }
@media (max-width: 768px) { .kline-chart { height: 300px; min-height: 220px; } }
@media (max-width: 480px) { .kline-chart { height: 260px; min-height: 180px; } }
</style>