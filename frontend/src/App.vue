<template>
  <n-config-provider :theme="darkTheme" class="h-full">
    <n-message-provider>
      <n-dialog-provider>
        <div class="app-layout">
          <Sidebar />
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
import { darkTheme, NConfigProvider, NMessageProvider, NDialogProvider } from "naive-ui";
import Sidebar from "./components/Sidebar.vue";
import Header from "./components/Header.vue";
</script>
