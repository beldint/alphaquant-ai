<template>
  <div ref="chartRef" class="chart-container"></div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue';
import * as echarts from 'echarts';
import type { KlineRecord } from '../stores/stock';

const props = defineProps<{ data: KlineRecord[] }>();
const chartRef = ref<HTMLElement>();
let chartInstance: echarts.ECharts | null = null;
let resizeHandler: (() => void) | null = null;

function renderChart(): void {
  if (!chartRef.value || !props.data.length) return;
  if (!chartInstance) chartInstance = echarts.init(chartRef.value);

  const dates = props.data.map((item) => item.trade_date.slice(5, 10));
  const ohlc = props.data.map((item) => [item.open_price, item.close_price, item.low_price, item.high_price]);
  const volume = props.data.map((item) => item.volume);
  const ma5 = calcMA(props.data, 5);
  const ma10 = calcMA(props.data, 10);
  const ma20 = calcMA(props.data, 20);

  chartInstance.setOption({
    backgroundColor: 'transparent',
    animation: false,
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross', lineStyle: { color: '#64748b' } },
      backgroundColor: 'rgba(15, 23, 42, 0.94)',
      borderColor: '#334155',
      textStyle: { color: '#e5e7eb' },
      valueFormatter: (value: unknown) => formatTooltipValue(value),
    },
    legend: {
      top: 10,
      data: ['K线', 'MA5', 'MA10', 'MA20', '成交量'],
      textStyle: { color: '#9ca3af' },
      itemGap: 18,
    },
    axisPointer: {
      link: [{ xAxisIndex: [0, 1] }],
    },
    grid: [
      { left: 76, right: 28, top: 60, height: 230 },
      { left: 76, right: 28, top: 315, height: 72 },
    ],
    xAxis: [
      {
        type: 'category',
        data: dates,
        boundaryGap: true,
        axisLine: { lineStyle: { color: '#334155' } },
        axisTick: { lineStyle: { color: '#334155' } },
        axisLabel: { color: '#9ca3af', hideOverlap: true },
        gridIndex: 0,
      },
      {
        type: 'category',
        data: dates,
        boundaryGap: true,
        axisLine: { lineStyle: { color: '#334155' } },
        axisTick: { show: false },
        axisLabel: { show: false },
        gridIndex: 1,
      },
    ],
    yAxis: [
      {
        scale: true,
        splitNumber: 4,
        splitLine: { lineStyle: { color: '#242832' } },
        axisLabel: { color: '#9ca3af', formatter: (value: number) => formatPriceAxis(value) },
        gridIndex: 0,
      },
      {
        scale: true,
        splitNumber: 2,
        splitLine: { show: false },
        axisLabel: {
          color: '#9ca3af',
          margin: 8,
          formatter: (value: number) => formatVolumeAxis(value),
        },
        gridIndex: 1,
      },
    ],
    dataZoom: [
      { type: 'inside', xAxisIndex: [0, 1], start: 0, end: 100, zoomOnMouseWheel: true, moveOnMouseMove: true },
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: ohlc,
        itemStyle: {
          color: '#00c853',
          color0: '#ff1744',
          borderColor: '#00c853',
          borderColor0: '#ff1744',
        },
      },
      { name: 'MA5', type: 'line', data: ma5, smooth: true, lineStyle: { width: 1, color: '#fdd835' }, symbol: 'none' },
      { name: 'MA10', type: 'line', data: ma10, smooth: true, lineStyle: { width: 1, color: '#42a5f5' }, symbol: 'none' },
      { name: 'MA20', type: 'line', data: ma20, smooth: true, lineStyle: { width: 1, color: '#ab47bc' }, symbol: 'none' },
      {
        name: '成交量',
        type: 'bar',
        data: volume,
        xAxisIndex: 1,
        yAxisIndex: 1,
        barMaxWidth: 28,
        itemStyle: {
          color: (params: { dataIndex: number }) => {
            const item = props.data[params.dataIndex];
            return item && item.close_price >= item.open_price ? '#00c853' : '#ff1744';
          },
        },
      },
    ],
  });
}

function calcMA(data: KlineRecord[], days: number): Array<number | string> {
  return data.map((_, index) => {
    if (index < days - 1) return '-';
    const slice = data.slice(index - days + 1, index + 1);
    return round2(slice.reduce((sum, item) => sum + item.close_price, 0) / days);
  });
}

function formatPriceAxis(value: number): string {
  if (!Number.isFinite(value)) return '';
  return value.toFixed(2);
}

function formatVolumeAxis(value: number): string {
  if (!Number.isFinite(value) || value === 0) return '0';
  if (Math.abs(value) >= 100000000) return `${round2(value / 100000000)}亿`;
  if (Math.abs(value) >= 10000) return `${round2(value / 10000)}万`;
  return String(Math.round(value));
}

function formatTooltipValue(value: unknown): string {
  if (Array.isArray(value)) return value.map((item) => formatTooltipValue(item)).join(', ');
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return String(value);
  return numeric >= 10000 ? formatVolumeAxis(numeric) : numeric.toFixed(2);
}

function round2(value: number): number {
  return Math.round(value * 100) / 100;
}

watch(() => props.data, renderChart, { deep: true });

onMounted(() => {
  renderChart();
  resizeHandler = () => chartInstance?.resize();
  window.addEventListener('resize', resizeHandler);
});

onBeforeUnmount(() => {
  if (resizeHandler) window.removeEventListener('resize', resizeHandler);
  chartInstance?.dispose();
  chartInstance = null;
});
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 420px;
}
</style>
