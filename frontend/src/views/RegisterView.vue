<template>
  <div class="auth-container">
    <n-card title="注册" style="width:400px;margin:0 auto">
      <n-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleRegister">
        <n-form-item label="用户名" path="username">
          <n-input v-model:value="form.username" placeholder="3-64位字符" />
        </n-form-item>
        <n-form-item label="邮箱" path="email">
          <n-input v-model:value="form.email" placeholder="邮箱地址" />
        </n-form-item>
        <n-form-item label="密码" path="password">
          <n-input v-model:value="form.password" type="password" show-password-on="click" placeholder="至少8位" />
        </n-form-item>
        <n-form-item label="姓名（选填）" path="fullName">
          <n-input v-model:value="form.fullName" placeholder="可选" />
        </n-form-item>
        <n-button type="primary" block attr-type="submit" :loading="loading">注册</n-button>
      </n-form>
      <p class="auth-footer">已有账号？<router-link :to="{ name: 'login' }">立即登录</router-link></p>
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
const form = reactive({ username: "", email: "", password: "", fullName: "" });
const rules: FormRules = {
  username: { required: true, min: 3, max: 64, message: "请输入3-64位用户名", trigger: "blur" },
  email: { required: true, type: "email" as const, message: "请输入有效邮箱", trigger: "blur" },
  password: { required: true, min: 8, message: "密码至少8位", trigger: "blur" },
};
async function handleRegister() {
  try {
    await formRef.value?.validate();
    loading.value = true;
    const res = await authStore.register(form.username, form.email, form.password, form.fullName || undefined);
    if (res.code === 0) { message.success("注册成功，请登录"); router.push({ name: "login" }); }
    else { message.error(res.message || "注册失败"); }
  } catch { /* validation error */ }
  finally { loading.value = false; }
}
</script>
<style scoped>
.auth-container { display: flex; align-items: center; justify-content: center; min-height: calc(100vh - 100px); }
.auth-footer { text-align: center; margin-top: 16px; }
</style>
