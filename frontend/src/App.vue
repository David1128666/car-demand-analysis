<template>
  <div v-if="route.name === 'Login'" class="login-page"><router-view /></div>
  <div v-else>
    <aside class="sidebar">
      <div class="logo">🚗 汽车需求分析</div>
      <nav>
        <router-link to="/"><span class="nav-icon">📊</span><span>数据大屏</span></router-link>
        <router-link to="/analysis"><span class="nav-icon">📈</span><span>数据分析</span></router-link>
        <router-link to="/market"><span class="nav-icon">🔍</span><span>市场洞察</span></router-link>
        <router-link to="/cars"><span class="nav-icon">🚙</span><span>车型查询</span></router-link>
        <router-link to="/recommendations"><span class="nav-icon">🎯</span><span>智能推荐</span></router-link>
        <router-link v-if="auth.user?.role === 'admin'" to="/admin"><span class="nav-icon">⚙️</span><span>后台管理</span></router-link>
      </nav>
      <div class="user-bar">
        <div class="name">{{ auth.user?.nickname || auth.user?.username }}</div>
        <div class="role">{{ auth.user?.role }}</div>
        <button @click="auth.logout()">退出</button>
      </div>
    </aside>
    <div class="main">
      <div class="main-inner"><router-view /></div>
    </div>
  </div>
</template>

<script setup>
import { useRoute } from "vue-router";
import { useAuthStore } from "./stores/auth";
const route = useRoute();
const auth = useAuthStore();
</script>
