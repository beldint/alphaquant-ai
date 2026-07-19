<template>
  <div>
    <n-grid :cols="2" :x-gap="12" :y-gap="8" responsive="screen">
      <n-grid-item v-for="item in items" :key="item.label">
        <n-statistic :label="item.label" :value="fmtVal(item.value)" :tabular-nums="true" />
      </n-grid-item>
    </n-grid>
  </div>
<n-collapse class="mt-12">
<n-collapse-item title="指标通俗解释（小白也能看懂）">
<n-p style="font-size:13px;line-height:1.8;color:#555">
<b>移动平均线（MA）</b>：将过去N天的收盘价加起来除以N，得到一条平滑的曲线。
MA5表示最近5天的平均价格，MA10是10天，MA20是20天，MA60是60天（约3个月）。
如果短期均线（如MA5）在长期均线（如MA20）上方，说明股价处于上涨趋势；反之则下跌趋势。
<br/><br/>
<b>MACD（指数平滑异同移动平均线）</b>：由DIF线、DEA线和MACD柱组成。
• DIF = 快线（12日EMA）- 慢线（26日EMA），反映短期与长期趋势的差距
• DEA = DIF的9日平均线，是DIF的慢速线
• MACD柱 = (DIF - DEA) × 2，柱子越长，趋势越强
当DIF上穿DEA（金叉）时，是买入信号；下穿DEA（死叉）时，是卖出信号。
<br/><br/>
<b>RSI（相对强弱指标）</b>：衡量近期价格涨跌的力度，取值范围0-100。
• RSI > 70：超买区，股价可能过热，有回调风险
• RSI < 30：超卖区，股价可能过度下跌，有望反弹
• RSI在50附近：市场处于平衡状态
<br/><br/>
<b>KDJ（随机指标）</b>：判断短期买卖信号的指标。
• K值（快线）：反应最灵敏，变化最快
• D值（慢线）：反应最慢，是K值的3日平均
• J值（最快线）：是K和D的差值放大，变化最快
当K线上穿D线（金叉）时，是买入信号；下穿D线（死叉）时，是卖出信号。
通常K值>80考虑卖出，K值<20考虑买入。
</n-p>
</n-collapse-item>
</n-collapse>
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
    { label: 'MA5（5日移动均线）', value: ma5v }, { label: 'MA10（10日移动均线）', value: ma10v }, { label: 'MA20（20日移动均线）', value: ma20v },
    { label: 'MA60（60日移动均线）', value: ma60v }, { label: 'DIF（差离值）', value: macd.dif }, { label: 'DEA（信号线）', value: macd.dea },
    { label: 'MACD柱（柱状图）', value: macd.macd }, { label: 'RSI（相对强弱指数，14日）', value: rsi }, { label: 'K值（快线）', value: k },
    { label: 'D值（慢线）', value: d }, { label: 'J值（最快线）', value: j },
  ];
});
function fmtVal(value: number | null): string { return value == null ? '--' : value.toFixed(2); }
</script>