<template>
  <n-card :title="title" size="small" v-if="data.length > 0">
    <n-grid :cols="4" :x-gap="12" :y-gap="12">
      <n-grid-item v-for="(value, key) in indicators" :key="key">
        <n-statistic :label="key" :value="value" :tabular-nums="true" />
      </n-grid-item>
    </n-grid>
  </n-card>
</template>
<script setup lang="ts">
import { computed } from 'vue';
import type { KlineRecord } from '../stores/stock';
const props = defineProps<{ data: KlineRecord[]; title?: string }>();
const indicators = computed(() => {
  if (!props.data.length) return {};
  const last = props.data[props.data.length - 1];
  const closes = props.data.map(d => d.close_price);
  const n = closes.length;
  const ma5 = n >= 5 ? avg(closes.slice(-5)) : 0;
  const ma10 = n >= 10 ? avg(closes.slice(-10)) : 0;
  const ma20 = n >= 20 ? avg(closes.slice(-20)) : 0;
  const change = n >= 2 ? last.close_price - closes[n-2] : 0;
  const pct = n >= 2 && closes[n-2] ? ((last.close_price - closes[n-2]) / closes[n-2] * 100) : 0;
  const maxP = Math.max(...closes);
  const minP = Math.min(...closes);
  return {
    '最新价': last.close_price.toFixed(2),
    '涨跌幅': `${change > 0 ? '+' : ''}${pct.toFixed(2)}%`,
    '区间最高': maxP.toFixed(2),
    '区间最低': minP.toFixed(2),
    'MA5': ma5.toFixed(2),
    'MA10': ma10.toFixed(2),
    'MA20': ma20.toFixed(2),
    '区间振幅': (maxP - minP > 0 ? ((maxP - minP) / minP * 100).toFixed(2) : '0.00') + '%',
  };
});
function avg(arr: number[]) { return arr.reduce((a,b) => a+b, 0) / arr.length; }
</script>
