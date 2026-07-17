<template>
  <div>
    <div class="page-header flex-between"><h2>投资组合</h2><n-space><n-button :loading="refreshing" ghost @click="refreshPrices">刷新行情</n-button><n-button type="primary" ghost @click="showAdd = true">添加持仓</n-button></n-space></div>

    <!-- Add/Edit Dialog -->
    <n-modal v-model:show="showAdd" title="添加持仓" preset="card" style="width:420px">
      <n-form>
        <n-form-item label="股票代码"><n-input v-model:value="form.symbol" placeholder="如 000001" /></n-form-item>
        <n-form-item label="股票名称"><n-input v-model:value="form.name" placeholder="如 平安银行" /></n-form-item>
        <n-form-item label="持仓数量"><n-input-number v-model:value="form.quantity" :min="0" style="width:100%" /></n-form-item>
        <n-form-item label="成本价"><n-input-number v-model:value="form.averageCost" :min="0" :precision="2" style="width:100%" /></n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showAdd = false">取消</n-button>
          <n-button type="primary" @click="saveHolding">保存</n-button>
        </n-space>
      </template>
    </n-modal>

    <n-card size="small" class="mb-24">
      <n-grid :cols="3" :x-gap="16">
        <n-grid-item><n-statistic label="持仓数量" :value="portfolioStore.holdings.length" :tabular-nums="true" /></n-grid-item>
        <n-grid-item><n-statistic label="总市值" :value="totalValue.toFixed(2)" :tabular-nums="true" /></n-grid-item>
        <n-grid-item><n-statistic label="总盈亏" :value="totalPnl.toFixed(2)" :tabular-nums="true" :style="totalPnl >= 0 ? 'color:var(--up-color)' : 'color:var(--down-color)'" /></n-grid-item>
      </n-grid>
    </n-card>
    <n-data-table v-if="portfolioStore.holdings.length > 0" :columns="columns" :data="portfolioStore.holdings" :bordered="false" size="small" />
    <n-empty v-else description="暂无持仓数据，点击上方添加持仓" style="margin-top:60px" />
  </div>
</template>
<script setup lang="ts">
import { ref, computed, reactive, h, watch } from 'vue';
import { NButton, NDataTable, NModal, NForm, NFormItem, NInput, NInputNumber, NSpace, NCard, NGrid, NGridItem, NStatistic, NEmpty } from 'naive-ui';
import type { DataTableColumn } from 'naive-ui';
import { usePortfolioStore } from '../stores/portfolio';
import { searchStocks } from '../api';
import { useMessage } from 'naive-ui';
const portfolioStore = usePortfolioStore();
const message = useMessage();
const showAdd = ref(false);
const refreshing = ref(false);

async function refreshPrices() {
  refreshing.value = true;
  var holdingsList = portfolioStore.holdings;
  if (!holdingsList.length) { refreshing.value = false; return; }
  var total = holdingsList.length;
  var done = 0;
  for (var i = 0; i < total; i++) {
    var h = holdingsList[i];
    try {
      var res = await (await import("../api")).getQuote(h.symbol, "A");
      if (res && res.code === 0 && res.data) {
        var price = Number(res.data.price);
        if (price > 0) {
          h.marketValue = h.quantity * price;
          h.pnl = h.marketValue - h.quantity * h.averageCost;
        }
      }
    } catch(e) {}
    done++;
  }
  refreshing.value = false;
}
const form = reactive({ symbol: '', name: '', quantity: 0, averageCost: 0 });
let _nameTimer: any = null;
watch(function() { return form.symbol; }, function(val) {
  if (_nameTimer) clearTimeout(_nameTimer);
  if (val && val.length >= 3) {
    _nameTimer = setTimeout(async function() {
      try {
        _nameTimer = null;
        var res = await searchStocks(val, 'A');
        if (res && res.code === 0 && res.data) {
          var match = res.data.find(function(s) { return s.symbol === val; });
          if (match) form.name = match.name;
        }
      } catch(e) {}
    }, 500);
  }
});

const totalValue = computed(function() {
  return portfolioStore.holdings.reduce(function(s, h) { return s + h.marketValue; }, 0);
});
const totalPnl = computed(function() {
  return portfolioStore.holdings.reduce(function(s, h) { return s + h.pnl; }, 0);
});

function editHolding(row: any) {
  form.symbol = row.symbol;
  form.name = row.name;
  form.quantity = row.quantity;
  form.averageCost = row.averageCost;
  showAdd.value = true;
}

function saveHolding() {
  if (!form.symbol.trim() || !form.name.trim() || form.quantity <= 0 || form.averageCost <= 0) {
    message.warning("请填写完整信息");
    return;
  }
  portfolioStore.addOrUpdate({
    symbol: form.symbol.trim(),
    name: form.name.trim(),
    quantity: form.quantity,
    averageCost: form.averageCost,
    marketValue: form.quantity * form.averageCost,
    pnl: 0
  });
  message.success("添加成功");
  showAdd.value = false;
  form.symbol = ''; form.name = ''; form.quantity = 0; form.averageCost = 0;
}

const columns: DataTableColumn<any>[] = [
  { title: '代码', key: 'symbol', width: 90, sortable: true },
  { title: '名称', key: 'name', width: 130, ellipsis: true },
  { title: '持仓', key: 'quantity', width: 70, sortable: true },
  { title: '成本价', key: 'averageCost', width: 90 },
  { title: '现价', key: 'currentPrice', width: 80, render: function(row) { var p = row.marketValue && row.quantity ? (row.marketValue / row.quantity).toFixed(2) : '-'; return p; } },
  { title: '市值', key: 'marketValue', width: 100, sortable: true, render: function(row) { return row.marketValue.toFixed(2); } },
  { title: '盈亏', key: 'pnl', width: 140, sortable: true, render: function(row) {
    var pct = row.averageCost > 0 ? (row.pnl / (row.quantity * row.averageCost) * 100) : 0;
    return h('span', { style: { color: row.pnl >= 0 ? 'var(--up-color)' : 'var(--down-color)' } }, row.pnl.toFixed(2) + ' (' + pct.toFixed(2) + '%)');
  } },
  { title: '操作', width: 120, render: function(row) {
    return h('span', null, [
      h(NButton, { size: 'tiny', quaternary: true, onClick: function() { editHolding(row); } }, function() { return '编辑'; }),
      h(NButton, { size: 'tiny', quaternary: true, style: { color: 'red' }, onClick: function() { portfolioStore.remove(row.symbol); } }, function() { return '删除'; }),
    ]);
  } },
];
</script>