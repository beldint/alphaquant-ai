import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { loginApi, registerApi } from '../api';
export interface User { id: string; username: string; email: string; full_name: string | null; is_active: boolean; is_superuser: boolean; created_at: string; updated_at: string }
export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('access_token'));
  const user = ref<User | null>(null);
  const isLoggedIn = computed(() => !!token.value);
  async function login(usernameOrEmail: string, password: string) {
    const res = await loginApi(usernameOrEmail, password);
    if (res.code === 0 && res.data) { token.value = res.data.access_token; localStorage.setItem('access_token', res.data.access_token); localStorage.setItem('refresh_token', res.data.refresh_token); }
    return res;
  }
  async function register(username: string, email: string, password: string, fullName?: string) {
    const res = await registerApi(username, email, password, fullName);
    if (res.code === 0 && res.data) user.value = res.data;
    return res;
  }
  function logout() { token.value = null; user.value = null; localStorage.removeItem('access_token'); localStorage.removeItem('refresh_token'); }
  return { token, user, isLoggedIn, login, register, logout };
});
