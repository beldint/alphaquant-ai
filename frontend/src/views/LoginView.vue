<template>
  <div class="auth-container">
    <n-card title="登录" style="width:400px;margin:0 auto">
      <n-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleLogin">
        <n-form-item label="用户名或邮箱" path="usernameOrEmail">
          <n-input v-model:value="form.usernameOrEmail" placeholder="输入用户名或邮箱" />
        </n-form-item>
        <n-form-item label="密码" path="password">
          <n-input v-model:value="form.password" type="password" show-password-on="click" placeholder="输入密码" />
        </n-form-item>
        <n-button type="primary" block attr-type="submit" :loading="loading">登录</n-button>
      </n-form>
      <p class="auth-footer">还没有账号？<router-link :to="{ name: 'register' }">立即注册</router-link></p>
    </n-card>
  </div>
</template>
<script setup lang="ts">
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { useMessage } from "naive-ui";
import { useAuthStore } from "../stores/auth";
import type { FormInst, FormRules } from "naive-ui";
const router = useRouter();
const authStore = useAuthStore();
const formRef = ref<FormInst | null>(null);
const loading = ref(false);
const message = useMessage();
const form = reactive({ usernameOrEmail: "", password: "" });
const rules: FormRules = { usernameOrEmail: { required: true, message: "请输入用户名或邮箱", trigger: "blur" }, password: { required: true, message: "请输入密码", trigger: "blur" } };
async function handleLogin() {
  try {
    await formRef.value?.validate();
    loading.value = true;
    const res = await authStore.login(form.usernameOrEmail, form.password);
    if (res.code === 0) { message.success("登录成功"); router.push({ name: "dashboard" }); }
    else { message.error(res.message || "登录失败"); }
  } catch { /* validation error */ }
  finally { loading.value = false; }
}
</script>
<style scoped>
.auth-container { display: flex; align-items: center; justify-content: center; min-height: calc(100vh - 100px); }
.auth-footer { text-align: center; margin-top: 16px; }
</style>
