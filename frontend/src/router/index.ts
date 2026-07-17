import { createRouter, createWebHistory } from 'vue-router';
import PortfolioView from '../views/PortfolioView.vue';
export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'dashboard', component: () => import('../views/DashboardView.vue') },
    { path: '/market', name: 'market', component: () => import('../views/MarketView.vue') },
    { path: '/stock/:symbol', name: 'stockDetail', component: () => import('../views/StockDetailView.vue') },
    { path: '/analysis', name: 'analysis', component: () => import('../views/AnalysisView.vue') },
    { path: '/watchlist', name: 'watchlist', component: () => import('../views/WatchlistView.vue') },
    { path: '/portfolio', name: 'portfolio', component: PortfolioView },
    { path: '/login', name: 'login', component: () => import('../views/LoginView.vue') },
    { path: '/register', name: 'register', component: () => import('../views/RegisterView.vue') },
  ],
});
