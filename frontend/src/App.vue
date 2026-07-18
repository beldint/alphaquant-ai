<template>
  <n-config-provider :theme="darkTheme" class="h-full">
    <n-message-provider>
      <n-dialog-provider>
        <div class="app-layout">
          <div
            class="sidebar-backdrop"
            :class="{ visible: sidebarOpen }"
            @click="sidebarOpen = false"
          />
          <button class="sidebar-toggle" @click="sidebarOpen = !sidebarOpen">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path v-if="!sidebarOpen" d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/>
              <path v-else d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
            </svg>
          </button>
          <Sidebar :open="sidebarOpen" @close="sidebarOpen = false" />
          <div class="app-main">
            <Header />
            <div class="app-content">
              <router-view />
            </div>
          </div>
        </div>
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { darkTheme, NConfigProvider, NMessageProvider, NDialogProvider } from 'naive-ui';
import Sidebar from './components/Sidebar.vue';
import Header from './components/Header.vue';

const sidebarOpen = ref(false);
</script>
