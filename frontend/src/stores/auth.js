import { defineStore } from "pinia";
import { ref } from "vue";
import api from "../api";

export const useAuthStore = defineStore("auth", () => {
  const user = ref(JSON.parse(localStorage.getItem("user") || "null"));
  const token = ref(localStorage.getItem("token") || "");

  async function login(username, password) {
    try {
      const res = await api.post("/auth/login", { username, password });
      if (res.code === 200 && res.data.success) {
        token.value = res.data.token;
        user.value = res.data.user;
        localStorage.setItem("token", res.data.token);
        localStorage.setItem("user", JSON.stringify(res.data.user));
        return { success: true };
      }
      return { success: false, message: res.data?.message || "登录失败" };
    } catch (e) {
      return { success: false, message: e.message || "网络错误，请检查后端服务" };
    }
  }

  async function register(username, password, nickname) {
    try {
      return await api.post("/auth/register", { username, password, nickname });
    } catch (e) {
      throw new Error(e.message || "注册失败，请检查后端服务");
    }
  }

  function logout() {
    token.value = "";
    user.value = null;
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    window.location.href = "/login";
  }

  return { user, token, login, register, logout };
});