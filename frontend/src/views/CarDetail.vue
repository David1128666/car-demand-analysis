<template>
  <div>
    <button class="btn btn-secondary btn-sm" @click="$router.back()">
      {{ t("carDetail.back") }}
    </button>
    <div v-if="loading" class="loading">{{ t("carDetail.loading") }}</div>
    <div v-else-if="car">
      <h1 class="page-title" style="margin-top:16px">{{ car.model_name }}</h1>
      <div class="stat-grid">
        <div class="stat-card">
          <div class="label">{{ t("carDetail.brand") }}</div>
          <div class="value detail-value">{{ car.brand_name }}</div>
        </div>
        <div class="stat-card">
          <div class="label">{{ t("carDetail.series") }}</div>
          <div class="value detail-value">{{ car.series_name }}</div>
        </div>
        <div class="stat-card">
          <div class="label">{{ t("carDetail.price") }}</div>
          <div class="value">
            {{ car.price }}<span class="detail-unit">{{ t("common.unitWan") }}</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="label">{{ t("carDetail.type") }}</div>
          <div class="value detail-value">{{ valueLabel(car.car_type) }}</div>
        </div>
        <div class="stat-card">
          <div class="label">{{ t("carDetail.fuel") }}</div>
          <div class="value detail-value">{{ valueLabel(car.fuel_type) }}</div>
        </div>
      </div>
      <div class="card" style="margin-top:12px">
        <div class="card-title">{{ t("carDetail.basicInfo") }}</div>
        <table>
          <tbody>
            <tr>
              <td class="detail-label">{{ t("carDetail.launchDate") }}</td>
              <td>{{ car.launch_date }}</td>
            </tr>
            <tr>
              <td class="detail-label">{{ t("carDetail.country") }}</td>
              <td>{{ car.country || "-" }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";

import api from "../api";
import { t, valueLabel } from "../i18n";

const route = useRoute();
const car = ref(null);
const loading = ref(true);

onMounted(async () => {
  try {
    const response = await api.get("/cars/" + route.params.id);
    car.value = response.data;
  } catch (error) {
    console.error(error);
  }
  loading.value = false;
});
</script>

<style scoped>
.detail-value {
  font-size: 20px;
}
.detail-unit {
  font-size: 14px;
  margin-left: 3px;
}
.detail-label {
  color: var(--text-secondary);
  width: 110px;
}
</style>
