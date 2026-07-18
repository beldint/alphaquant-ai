import { createRouter, createWebHistory } from 'vue-router';

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'dashboard', component: () => import('../views/DashboardView.vue') },
    { path: '/market', name: 'market', component: () => import('../views/MarketView.vue') },
    { path: '/stock/:symbol', name: 'stockDetail', component: () => import('../views/StockDetailView.vue') },
    { path: '/financials/:symbol', name: 'financials', component: () => import('../views/FinancialView.vue'), props: true },
    { path: '/analysis', name: 'analysis', component: () => import('../views/AnalysisView.vue') },
    { path: '/watchlist', name: 'watchlist', component: () => import('../views/WatchlistView.vue') },
    { path: '/portfolio', name: 'portfolio', component: () => import('../views/PortfolioView.vue') },
  ],
});
