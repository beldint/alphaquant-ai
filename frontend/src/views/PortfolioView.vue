<template>
  <div>
    <div class="page-header flex-between">
      <h2>投资组合</h2>
      <n-space>
        <n-button :loading="refreshing" ghost @click="refreshPrices">刷新行情</n-button>
        <n-button type="primary" ghost @click="openAdd">添加持仓</n-button>
      </n-space>
    </div>

    <n-modal v-model:show="showAdd" :title="isEditing ? '编辑持仓' : '添加持仓'" preset="card" style="width:420px;max-width:95vw">
      <n-form>
        <n-form-item label="股票代码">
          <n-input v-model:value="form.symbol" placeholder="如 000001" :disabled="isEditing" />
        </n-form-item>
        <n-form-item label="股票名称">
          <n-input v-model:value="form.name" placeholder="如 平安银行" :disabled="isEditing" />
        </n-form-item>
        <n-form-item label="持仓数量">
          <n-input-number v-model:value="form.quantity" :min="0" style="width:100%" />
        </n-form-item>
        <n-form-item label="成本价">
          <n-input-number v-model:value="form.averageCost" :min="0" :precision="2" style="width:100%" />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showAdd = false">取消</n-button>
          <n-button type="primary" @click="saveHolding">保存</n-button>
        </n-space>
      </template>
    </n-modal>

    <n-card size="small" class="mb-24">
      <n-grid :cols="3" :x-gap="16" responsive="screen">
        <n-grid-item>
          <n-statistic label="持仓数量" :value="portfolioStore.holdings.length" :tabular-nums="true" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic label="总市值" :value="totalValue.toFixed(2)" :tabular-nums="true" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic
            label="总盈亏"
            :value="totalPnl.toFixed(2)"
            :tabular-nums="true"
            :style="totalPnl >= 0 ? 'color:var(--up-color)' : 'color:var(--down-color)'"
          />
        </n-grid-item>
      </n-grid>
    </n-card>

    <div class="overflow-table">
    <n-data-table
      v-if="portfolioStore.holdings.length > 0"
      :columns="columns"
      :data="portfolioStore.holdings"
      :bordered="false"
      size="small"
    />
    </div>
    <n-empty v-if="portfolioStore.holdings.length === 0" description="暂无持仓数据，点击上方添加持仓" style="margin-top:60px" />
  </div>
</template>

<script setup lang="ts">
import { computed, h, reactive, ref, watch } from 'vue';
import { NButton, NCard, NDataTable, NEmpty, NForm, NFormItem, NGrid, NGridItem, NInput, NInputNumber, NModal, NSpace, NStatistic, useMessage } from 'naive-ui';
import type { DataTableColumn } from 'naive-ui';
import { getQuote, searchStocks } from '../api';
import { usePortfolioStore, type PortfolioHolding } from '../stores/portfolio';

const portfolioStore = usePortfolioStore();
const message = useMessage();
const showAdd = ref(false);
const isEditing = ref(false);
const refreshing = ref(false);
const form = reactive({ symbol: '', name: '', quantity: 0, averageCost: 0 });
let nameTimer: ReturnType<typeof setTimeout> | null = null;
let codeTimer: ReturnType<typeof setTimeout> | null = null;

const totalValue = computed(() => portfolioStore.holdings.reduce((sum, holding) => sum + holding.marketValue, 0));
const totalPnl = computed(() => portfolioStore.holdings.reduce((sum, holding) => sum + holding.pnl, 0));

watch(() => form.symbol, (value) => {
  if (nameTimer) clearTimeout(nameTimer);
  if (!value || value.length < 3) return;
  nameTimer = setTimeout(async () => {
    nameTimer = null;
    try {
      const response = await searchStocks(value, 'A');
      const match = response.code === 0 && response.data ? response.data.find((stock) => stock.symbol === value) : null;
      if (match) form.name = match.name;
    } catch {
      // Name autofill is optional.
    }
  }, 500);
});

watch(() => form.name, (value) => {
  if (codeTimer) clearTimeout(codeTimer);
  if (!value || value.length < 2) return;
  codeTimer = setTimeout(async () => {
    codeTimer = null;
    try {
      const response = await searchStocks(value, 'A');
      if (response.code === 0 && response.data && response.data.length > 0) {
        // Auto-fill code when name is entered (always update)
        form.symbol = response.data[0].symbol;
      }
    } catch {
      // Code autofill is optional.
    }
  }, 500);
});

function openAdd(): void {
  resetForm();
  isEditing.value = false;
  showAdd.value = true;
}

async function refreshPrices(): Promise<void> {
  refreshing.value = true;
  try {
    for (const holding of portfolioStore.holdings) {
      try {
        const response = await getQuote(holding.symbol, 'A');
        if (response.code === 0 && response.data) {
          const price = Number(response.data.price);
          if (price > 0) {
            holding.marketValue = holding.quantity * price;
            holding.pnl = holding.marketValue - holding.quantity * holding.averageCost;
          }
        }
      } catch {
        // Keep the existing holding value if a single quote fails.
      }
    }
  } finally {
    refreshing.value = false;
  }
}

function editHolding(row: PortfolioHolding): void {
  isEditing.value = true;
  form.symbol = row.symbol;
  form.name = row.name;
  form.quantity = row.quantity;
  form.averageCost = row.averageCost;
  showAdd.value = true;
}

function saveHolding(): void {
  if (!form.symbol.trim() || !form.name.trim() || form.quantity <= 0 || form.averageCost <= 0) {
    message.warning('请填写完整持仓信息');
    return;
  }
  // Check for duplicate stock when adding
  if (!isEditing.value && portfolioStore.holdings.some(function(h) { return h.symbol === form.symbol.trim(); })) {
    message.warning('股票已添加');
    return;
  }
  portfolioStore.addOrUpdate({
    symbol: form.symbol.trim(),
    name: form.name.trim(),
    quantity: form.quantity,
    averageCost: form.averageCost,
    marketValue: form.quantity * form.averageCost,
    pnl: 0,
  });
  message.success('保存成功');
  showAdd.value = false;
  resetForm();
}

function resetForm(): void {
  form.symbol = '';
  form.name = '';
  form.quantity = 0;
  form.averageCost = 0;
}

const columns: DataTableColumn<PortfolioHolding>[] = [
  { title: '代码', key: 'symbol', width: 90, sorter: 'default' },
  { title: '名称', key: 'name', width: 130, ellipsis: true },
  { title: '持仓', key: 'quantity', width: 70, sorter: 'default' },
  { title: '成本价', key: 'averageCost', width: 90, render: (row) => row.averageCost.toFixed(2) },
  { title: '现价', key: 'currentPrice', width: 80, render: (row) => (row.marketValue && row.quantity ? (row.marketValue / row.quantity).toFixed(2) : '-') },
  { title: '市值', key: 'marketValue', width: 100, sorter: 'default', render: (row) => row.marketValue.toFixed(2) },
  {
    title: '盈亏',
    key: 'pnl',
    width: 140,
    sorter: 'default',
    render: (row) => {
      const pct = row.averageCost > 0 ? (row.pnl / (row.quantity * row.averageCost)) * 100 : 0;
      return h('span', { style: { color: row.pnl >= 0 ? 'var(--up-color)' : 'var(--down-color)' } }, `${row.pnl.toFixed(2)} (${pct.toFixed(2)}%)`);
    },
  },
  {
    title: '操作',
    key: 'actions',
    width: 120,
    render: (row) => [
      h(NButton, { size: 'tiny', quaternary: true, onClick: () => editHolding(row) }, () => '编辑'),
      h(NButton, { size: 'tiny', quaternary: true, style: { color: 'red' }, onClick: () => portfolioStore.remove(row.symbol) }, () => '删除'),
    ],
  },
];
</script>
