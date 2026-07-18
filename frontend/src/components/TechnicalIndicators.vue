<template>
  <n-card v-if="data.length > 0" :title="title" size="small">
    <n-grid :cols="4" :x-gap="12" :y-gap="12">
      <n-grid-item v-for="item in indicatorList" :key="item.label">
        <n-statistic :label="item.label" :value="item.value" :tabular-nums="true" />
      </n-grid-item>
    </n-grid>
  </n-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { KlineRecord } from '../stores/stock';

type IndicatorItem = {
  label: string;
  value: string;
};

const props = defineProps<{
  data: KlineRecord[];
  title?: string;
}>();

const indicatorList = computed<IndicatorItem[]>(() => {
  if (!props.data.length) return [];

  const closes = props.data.map((item) => item.close_price);
  const last = props.data[props.data.length - 1];
  const prev = props.data.length > 1 ? props.data[props.data.length - 2] : null;
  const maxPrice = Math.max(...closes);
  const minPrice = Math.min(...closes);
  const change = prev ? last.close_price - prev.close_price : 0;
  const pct = prev && prev.close_price !== 0 ? (change / prev.close_price) * 100 : 0;

  return [
    { label: '最新价', value: last.close_price.toFixed(2) },
    { label: '涨跌幅', value: `${change >= 0 ? '+' : ''}${pct.toFixed(2)}%` },
    { label: '区间高点', value: maxPrice.toFixed(2) },
    { label: '区间低点', value: minPrice.toFixed(2) },
    { label: 'MA5', value: average(closes.slice(-5)).toFixed(2) },
    { label: 'MA10', value: average(closes.slice(-10)).toFixed(2) },
    { label: 'MA20', value: average(closes.slice(-20)).toFixed(2) },
    {
      label: '区间振幅',
      value: minPrice > 0 ? `${(((maxPrice - minPrice) / minPrice) * 100).toFixed(2)}%` : '0.00%',
    },
  ];
});

function average(values: number[]): number {
  if (!values.length) return 0;
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}
</script>
