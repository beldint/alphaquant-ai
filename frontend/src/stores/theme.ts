import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { GlobalThemeOverrides } from 'naive-ui';

export type ThemeMode = 'day' | 'night' | 'eyeCare';

const THEME_KEY = 'app_theme';
const THEME_VERSION_KEY = 'app_theme_v';
const THEME_VERSION = 2;

/** Naive UI theme overrides for 黑夜 (Night) — lighter dark with better contrast. */
const nightOverrides: GlobalThemeOverrides = {
  common: {
    bodyColor: '#5a5a74',
    cardColor: '#727290',
    modalColor: '#727290',
    popoverColor: '#727290',
    tableColor: '#727290',
    actionColor: '#5a5a74',
    inputColor: '#8080a0',
    inputColorDisabled: '#8080a0',
    tagColor: '#8686a4',
    dividerColor: '#8686a4',
    borderColor: '#8686a4',
    tableborderColor: '#8686a4',
    hoverColor: '#7a7a9a',
    primaryColor: '#72b8ff',
    primaryColorHover: '#90ccff',
    primaryColorPressed: '#5098e0',
    textColor1: '#ffffff',
    textColor2: '#e0e0f0',
    textColor3: '#c8c8dd',
    placeholderColor: '#9898b4',
    closeColor: '#dcdcf0',
    closeColorHover: '#ffffff',
    closeColorPressed: '#ffffff',
    progressRailcolor: '#585a78',
    railcolor: '#585a78',
    trackcolor: '#585a78',
    iconColor: '#dcdcf0',
    iconColorHover: '#ffffff',
    iconColorPressed: '#ffffff',
  },
  Card: { color: '#727290', borderColor: '#8686a4' },
  Menu: {
    itemColor: 'transparent', itemColorHover: '#7a7a9a', itemColorActive: '#8686a4',
    itemTextColor: '#e0e0f0', itemTextColorHover: '#ffffff', itemTextColorActive: '#ffffff',
    arrowColor: '#dcdcf0',
  },
  Layout: { siderColor: '#727290', siderborderColor: '#8686a4', headerColor: '#727290' },
  Button: {
    color: '#585a78', colorHover: '#3e4060', colorPressed: '#2d2e47',
    border: '#5a5a7a', borderHover: '#6a6a8a', borderPressed: '#4a4a6a',
    textColor: '#e8e9f0', textColorHover: '#ffffff', textColorPressed: '#e0e0ee',
  },
  DataTable: { tdColor: '#727290', thColor: '#5a5a74', thTextColor: '#ffffff', tdTextColor: '#e0e0f0', borderColor: '#8686a4' },
  Table: { tdColor: '#727290', thColor: '#5a5a74', thTextColor: '#ffffff', tdTextColor: '#e0e0f0' },
  Tag: { color: '#585a78', textColor: '#e8e9f0', border: '#5a5a7a' },
  Input: { color: '#1e1f32', border: '#363854', borderHover: '#4a4c6c' },
  Switch: { railcolor: '#585a78', railColorActive: '#4098fc' },
  Slider: { railcolor: '#585a78', fillColor: '#4098fc' },
  Collapse: { titleTextColor: '#e8e9f0', titleFontWeight: '600' },
  Breadcrumb: { itemTextColor: '#dcdcf0', itemTextColorHover: '#ffffff', separatorColor: '#7a7c98' },
  Alert: { color: '#505070', border: '#363854' },
  Dialog: { color: '#727290' },
  Drawer: { color: '#727290' },
  Empty: { textColor: '#9d9fb8', iconColor: '#7a7c98' },
  Statistic: { labelTextColor: '#9d9fb8', valueTextColor: '#e8e9f0' },
  LoadingBar: { colorLoading: '#4098fc' },
  Notification: { color: '#727290' },
  Select: { menuColor: '#727290' },
};

/** Naive UI theme overrides for 白天 (Day) — clean light. */
const dayOverrides: GlobalThemeOverrides = {
  common: {
    bodyColor: '#f0f2f5',
    cardColor: '#ffffff',
    modalColor: '#ffffff',
    popoverColor: '#ffffff',
    tableColor: '#ffffff',
    inputColor: '#f8f9fa',
    tagColor: '#e5e7eb',
    dividerColor: '#d9dde3',
    borderColor: '#d9dde3',
    tableBorderColor: '#d9dde3',
    hoverColor: '#f3f4f6',
    primaryColor: '#2080f0',
    primaryColorHover: '#4098fc',
    primaryColorPressed: '#1060c0',
    textColor1: '#111111',
    textColor2: '#333355',
    textColor3: '#555577',
  },
  Card: { color: '#ffffff', borderColor: '#d9dde3' },
  Menu: {
    itemColor: 'transparent', itemColorHover: '#f3f4f6', itemColorActive: '#e8f0fe',
    itemTextColor: '#4a4d6a', itemTextColorHover: '#1a1b26', itemTextColorActive: '#2080f0',
    arrowColor: '#6b7280',
  },
  Layout: { siderColor: '#ffffff', siderBorderColor: '#d9dde3', headerColor: '#ffffff' },
  Statistic: { labelTextColor: '#6b7280', valueTextColor: '#1a1b26' },
  Breadcrumb: { itemTextColor: '#6b7280', itemTextColorHover: '#1a1b26', separatorColor: '#9ca3af' },
  Collapse: { titleTextColor: '#1a1b26', titleFontWeight: '600' },
};

/** Naive UI theme overrides for 护眼 mode — soft green base. */
const eyeCareOverrides: GlobalThemeOverrides = {
  common: {
    bodyColor: '#a0d0a8',
    cardColor: '#cce8d0',
    modalColor: '#cce8d0',
    popoverColor: '#cce8d0',
    tableColor: '#cce8d0',
    actionColor: '#a0d0a8',
    inputColor: '#d8ecd8',
    inputColorDisabled: '#c0dcc4',
    tagColor: '#6aaa78',
    dividerColor: '#6aaa78',
    borderColor: '#6aaa78',
    tableBorderColor: '#6aaa78',
    hoverColor: '#b8d8bc',
    primaryColor: '#2080f0',
    primaryColorHover: '#4098fc',
    primaryColorPressed: '#1060c0',
    textColor1: '#111111',
    textColor2: '#2d4a2d',
    textColor3: '#3a6a3a',
    placeholderColor: '#5a7a5a',
    closeColor: '#2d4a2d',
    closeColorHover: '#1a1a2e',
    closeColorPressed: '#000000',
    progressRailColor: '#a8d8b0',
    railColor: '#a8d8b0',
    trackColor: '#a8d8b0',
    iconColor: '#2d4a2d',
    iconColorHover: '#1a1a2e',
    iconColorPressed: '#000000',
  },
  Card: { color: '#cce8d0', borderColor: '#6aaa78' },
  Menu: {
    itemColor: 'transparent', itemColorHover: '#b8d8bc', itemColorActive: '#a0cca8',
    itemTextColor: '#3a3d5c', itemTextColorHover: '#1a1a2e', itemTextColorActive: '#1a1a2e',
    arrowColor: '#4a5568',
  },
  Layout: { siderColor: '#cce8d0', siderBorderColor: '#6aaa78', headerColor: '#cce8d0' },
  Button: {
    color: '#a0d0a8', colorHover: '#c0e4c8', colorPressed: '#b0d8b8',
    border: '#6aaa78', borderHover: '#5a9a66', borderPressed: '#4a8a56',
    textColor: '#1a1a2e', textColorHover: '#000000', textColorPressed: '#000000',
  },
  DataTable: { tdColor: '#cce8d0', thColor: '#a0d0a8', thTextColor: '#1a1a2e', tdTextColor: '#2d4a2d', borderColor: '#6aaa78' },
  Table: { tdColor: '#cce8d0', thColor: '#a0d0a8', thTextColor: '#1a1a2e', tdTextColor: '#2d4a2d' },
  Tag: { color: '#6aaa78', textColor: '#1a1a2e', border: '#98c8a0' },
  Input: { color: '#d8ecd8', border: '#6aaa78', borderHover: '#5a9a66' },
  Switch: { railColor: '#a8d8b0', railColorActive: '#66BB6A' },
  Slider: { railColor: '#a8d8b0', fillColor: '#66BB6A' },
  Collapse: { titleTextColor: '#1a1a2e', titleFontWeight: '600' },
  Breadcrumb: { itemTextColor: '#2d4a2d', itemTextColorHover: '#1a1a2e', separatorColor: '#4a5568' },
  Alert: { color: '#d8ecd8', border: '#6aaa78' },
  Dialog: { color: '#cce8d0' },
  Drawer: { color: '#cce8d0' },
  Empty: { textColor: '#4a5568', iconColor: '#7a8c7a' },
  Statistic: { labelTextColor: '#3a3d5c', valueTextColor: '#1a1a2e' },
  LoadingBar: { colorLoading: '#66BB6A' },
  Notification: { color: '#cce8d0' },
  Select: { menuColor: '#cce8d0' },
};

export const useThemeStore = defineStore('theme', () => {
  const mode = ref<ThemeMode>('day');

  function init(): void {
    const saved = localStorage.getItem(THEME_KEY);
    if (saved === 'day' || saved === 'night' || saved === 'eyeCare') {
      mode.value = saved;
    }
    applyThemeClass(saved || 'day');
  }

  function setMode(m: ThemeMode): void {
    mode.value = m;
    localStorage.setItem(THEME_KEY, m);
    applyThemeClass(m);
  }

  function toggle(): void {
    const order: ThemeMode[] = ['day', 'night', 'eyeCare'];
    const idx = order.indexOf(mode.value);
    setMode(order[(idx + 1) % order.length]);
  }

  function applyThemeClass(m: ThemeMode): void {
    const root = document.documentElement;
    root.classList.remove('theme-day', 'theme-night', 'theme-eye-care');
    root.classList.add('theme-' + m);
  }

  const label = (m: ThemeMode) => ({ day: '白天', night: '黑夜', eyeCare: '护眼' }[m]);

  init();

  return { mode, init, setMode, toggle, label, applyThemeClass, nightOverrides, dayOverrides, eyeCareOverrides };
});