<template>
  <div>
    <n-grid :cols="2" :x-gap="12" :y-gap="8" responsive="screen">
      <n-grid-item v-for="item in items" :key="item.label">
        <n-statistic :label="item.label" :value="fmtVal(item.value)" :tabular-nums="true" />
      </n-grid-item>
    </n-grid>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue';
import { NGrid, NGridItem, NStatistic } from 'naive-ui';
import type { KlineRecord } from '../stores/stock';
const props = defineProps<{ data: KlineRecord[] }>();
function sma(arr: number[], period: number): (number | null)[] {
  const result: (number | null)[] = [];
  for (let i = 0; i < arr.length; i++) { if (i < period - 1) { result.push(null); continue; } let sum = 0; for (let j = i - period + 1; j <= i; j++) sum += arr[j]; result.push(sum / period); }
  return result;
}
const items = computed(() => {
  if (props.data.length < 20) return [];
  const closes = props.data.map(d => d.close_price);
  const ma5 = sma(closes, 5); const ma10 = sma(closes, 10); const ma20 = sma(closes, 20); const ma60 = sma(closes, 60);
  const last = closes[closes.length - 1];
  const ma5v = ma5[ma5.length - 1]; const ma10v = ma10[ma10.length - 1]; const ma20v = ma20[ma20.length - 1]; const ma60v = ma60[ma60.length - 1];
  const high14 = Math.max(...props.data.slice(-14).map(d => d.high_price));
  const low14 = Math.min(...props.data.slice(-14).map(d => d.low_price));
  const rsi = high14 !== low14 ? ((last - low14) / (high14 - low14)) * 100 : 50;
  function macdLine() {
    const ema12fn = (arr: number[], n: number) => { const k = 2 / (n + 1); const result: number[] = [arr[0]]; for (let i = 1; i < arr.length; i++) result.push(arr[i] * k + result[i - 1] * (1 - k)); return result; };
    const ema12 = ema12fn(closes, 12); const ema26 = ema12fn(closes, 26); const dif = ema12.map((v, i) => v - ema26[i]); const dea = ema12fn(dif, 9); const macd = dif.map((v, i) => 2 * (v - dea[i]));
    return { dif: dif[dif.length - 1], dea: dea[dea.length - 1], macd: macd[macd.length - 1] };
  }
  const macd = macdLine();
  const highest = Math.max(...closes.slice(-20)); const lowest = Math.min(...closes.slice(-20));
  const mid = (highest + lowest) / 2;
  const k = (last - lowest) / (highest - lowest) * 100; const d = ((closes.slice(-3).reduce((s, c) => s + (c - lowest) / (highest - lowest), 0)) / 3) * 100; const j = 3 * k - 2 * d;
  return [
    { label: 'MA5', value: ma5v }, { label: 'MA10', value: ma10v }, { label: 'MA20', value: ma20v },
    { label: 'MA60', value: ma60v }, { label: 'MACD DIF', value: macd.dif }, { label: 'MACD DEA', value: macd.dea },
    { label: 'MACD', value: macd.macd }, { label: 'RSI(14)', value: rsi }, { label: 'KDJ K', value: k },
    { label: 'KDJ D', value: d }, { label: 'KDJ J', value: j },
  ];
});
function fmtVal(value: number | null): string { return value == null ? '--' : value.toFixed(2); }
</script>