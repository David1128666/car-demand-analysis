<template>
  <div>
    <h1 class="page-title">{{ t("cars.title") }}</h1>
    <div class="filter-bar">
      <select v-model="filters.brand_id">
        <option value="">{{ t("cars.allBrands") }}</option>
        <option v-for="brand in brandList" :key="brand.brand_id" :value="brand.brand_id">
          {{ brand.brand_name }}
        </option>
      </select>
      <select v-model="filters.car_type">
        <option value="">{{ t("cars.allTypes") }}</option>
        <option value="轿车">{{ t("cars.type.sedan") }}</option>
        <option value="SUV">{{ t("cars.type.suv") }}</option>
        <option value="MPV">{{ t("cars.type.mpv") }}</option>
      </select>
      <select v-model="filters.fuel_type">
        <option value="">{{ t("cars.allFuels") }}</option>
        <option value="汽油">{{ t("cars.fuel.gasoline") }}</option>
        <option value="纯电动">{{ t("cars.fuel.bev") }}</option>
        <option value="混合动力">{{ t("cars.fuel.hybrid") }}</option>
        <option value="插电混动">{{ t("cars.fuel.phev") }}</option>
      </select>
      <button class="btn btn-primary btn-sm" @click="search(1)">
        {{ t("common.filter") }}
      </button>
      <button class="btn btn-secondary btn-sm" @click="resetFilters">
        {{ t("common.reset") }}
      </button>
    </div>
    <div v-if="loading" class="loading">{{ t("common.loading") }}</div>
    <div v-else>
      <div class="table-wrap card">
        <table>
          <thead>
            <tr>
              <th>{{ t("cars.table.brand") }}</th>
              <th>{{ t("cars.table.series") }}</th>
              <th>{{ t("cars.table.model") }}</th>
              <th>{{ t("cars.table.type") }}</th>
              <th>{{ t("cars.table.fuel") }}</th>
              <th>{{ t("cars.table.price") }}</th>
              <th>{{ t("cars.table.actions") }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="car in list" :key="car.car_id">
              <td>{{ car.brand_name }}</td>
              <td>{{ car.series_name }}</td>
              <td>{{ car.model_name }}</td>
              <td><span class="tag tag-blue">{{ valueLabel(car.car_type) }}</span></td>
              <td><span class="tag tag-green">{{ valueLabel(car.fuel_type) }}</span></td>
              <td>{{ car.price }} {{ t("common.unitWan") }}</td>
              <td>
                <button
                  class="btn btn-sm btn-primary"
                  @click="$router.push('/cars/' + car.car_id)"
                >
                  {{ t("cars.details") }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="pagination">
        <button :disabled="page <= 1" @click="search(page - 1)">
          {{ t("common.previous") }}
        </button>
        <button class="active">{{ page }}</button>
        <button @click="search(page + 1)">{{ t("common.next") }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";

import api from "../api";
import { t, valueLabel } from "../i18n";

const list = ref([]);
const brandList = ref([]);
const page = ref(1);
const loading = ref(true);
const filters = reactive({ brand_id: "", car_type: "", fuel_type: "" });

function resetFilters() {
  filters.brand_id = "";
  filters.car_type = "";
  filters.fuel_type = "";
  search(1);
}

async function search(nextPage = 1) {
  page.value = nextPage;
  loading.value = true;
  const params = { page: nextPage, size: 10 };
  if (filters.brand_id !== "" && filters.brand_id != null) {
    params.brand_id = filters.brand_id;
  }
  if (filters.car_type !== "" && filters.car_type != null) {
    params.car_type = filters.car_type;
  }
  if (filters.fuel_type !== "" && filters.fuel_type != null) {
    params.fuel_type = filters.fuel_type;
  }
  try {
    const response = await api.get("/cars", params);
    list.value = response.data?.list || [];
  } catch (error) {
    console.error(error);
  }
  loading.value = false;
}

onMounted(async () => {
  try {
    const response = await api.get("/cars/meta/brands");
    brandList.value = response.data || [];
  } catch (error) {
    console.error(error);
  }
  search();
});
</script>
