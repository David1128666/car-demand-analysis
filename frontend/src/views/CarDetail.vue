<template>
  <div>
    <button class="btn btn-secondary btn-sm" @click="$router.back()">← 返回</button>
    <div v-if="loading" class="loading">⏳ 加载中...</div>
    <div v-else-if="car">
      <h1 class="page-title" style="margin-top:16px">{{ car.model_name }}</h1>
      <div class="stat-grid">
        <div class="stat-card"><div class="label">品牌</div><div class="value" style="font-size:20px">{{ car.brand_name }}</div></div>
        <div class="stat-card"><div class="label">车系</div><div class="value" style="font-size:20px">{{ car.series_name }}</div></div>
        <div class="stat-card"><div class="label">价格</div><div class="value">{{ car.price }}<span style="font-size:14px">万</span></div></div>
        <div class="stat-card"><div class="label">类型</div><div class="value" style="font-size:20px">{{ car.car_type }}</div></div>
        <div class="stat-card"><div class="label">燃料</div><div class="value" style="font-size:20px">{{ car.fuel_type }}</div></div>
      </div>
      <div class="card" style="margin-top:12px"><div class="card-title">基础信息</div>
        <table><tbody><tr><td style="color:var(--text-secondary);width:80px">上市日期</td><td>{{ car.launch_date }}</td></tr>
        <tr><td style="color:var(--text-secondary)">产地</td><td>{{ car.country || '-' }}</td></tr></tbody></table></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import api from "../api";
const route = useRoute();
const car = ref(null); const loading = ref(true);

onMounted(async () => {
  try { const r = await api.get("/cars/"+route.params.id); car.value = r.data; } catch (e) { console.error(e); }
  loading.value = false;
});
</script>