<template>
  <div v-if="route.name === 'Login'" class="login-page">
    <button
      class="language-floating"
      type="button"
      :title="t('app.languageSwitch')"
      @click="toggleLocale"
    >
      <Languages :size="15" />
      {{ localeLabel }}
    </button>
    <router-view />
  </div>
  <div v-else>
    <aside class="sidebar">
      <div class="logo">
        <CarFront :size="17" />
        <span>{{ t("app.logo") }}</span>
      </div>
      <nav>
        <router-link to="/">
          <LayoutDashboard :size="15" />
          <span>{{ t("nav.dashboard") }}</span>
        </router-link>
        <router-link to="/analysis">
          <ChartLine :size="15" />
          <span>{{ t("nav.analysis") }}</span>
        </router-link>
        <router-link to="/market">
          <Search :size="15" />
          <span>{{ t("nav.market") }}</span>
        </router-link>
        <router-link to="/cars">
          <Car :size="15" />
          <span>{{ t("nav.cars") }}</span>
        </router-link>
        <router-link to="/recommendations">
          <Target :size="15" />
          <span>{{ t("nav.recommendations") }}</span>
        </router-link>
        <router-link v-if="auth.user?.role === 'admin'" to="/admin">
          <Settings :size="15" />
          <span>{{ t("nav.admin") }}</span>
        </router-link>
      </nav>
      <div class="user-bar">
        <div class="name">{{ auth.user?.nickname || auth.user?.username }}</div>
        <div class="role">{{ roleLabel }}</div>
        <div class="user-actions">
          <button type="button" :title="t('app.languageSwitch')" @click="toggleLocale">
            <Languages :size="13" />
            {{ localeLabel }}
          </button>
          <button type="button" @click="auth.logout()">
            <LogOut :size="13" />
            {{ t("app.logout") }}
          </button>
        </div>
      </div>
    </aside>
    <div class="main">
      <div class="main-inner"><router-view /></div>
    </div>
  </div>
</template>

<script setup>
import {
  Car,
  CarFront,
  ChartLine,
  Languages,
  LayoutDashboard,
  LogOut,
  Search,
  Settings,
  Target,
} from "@lucide/vue";
import { computed } from "vue";
import { useRoute } from "vue-router";

import { localeLabel, t, toggleLocale } from "./i18n";
import { useAuthStore } from "./stores/auth";

const route = useRoute();
const auth = useAuthStore();
const roleLabel = computed(() =>
  auth.user?.role === "admin" ? t("app.role.admin") : t("app.role.user"),
);
</script>
