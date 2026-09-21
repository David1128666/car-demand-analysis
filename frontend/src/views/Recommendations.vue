<template>
  <div>
    <h1 class="page-title">{{ t("rec.title") }}</h1>
    <div v-if="loading" class="loading">{{ t("rec.loading") }}</div>

    <div v-if="isAdmin && !loading">
      <div class="stat-grid">
        <div class="stat-card">
          <div class="label">{{ t("rec.totalRecommendations") }}</div>
          <div class="value">{{ summary.total.toLocaleString() }}</div>
        </div>
        <div class="stat-card">
          <div class="label">{{ t("rec.coveredUsers") }}</div>
          <div class="value">{{ summary.user_count }}</div>
        </div>
        <div class="stat-card" v-for="item in summary.by_type" :key="item.rec_type">
          <div class="label">{{ valueLabel(item.rec_type) }}</div>
          <div class="value">{{ item.cnt.toLocaleString() }}</div>
        </div>
      </div>

      <div class="chart-row" style="margin-top:16px">
        <div class="card chart-box">
          <div class="card-title">{{ t("rec.sourceDistribution") }}</div>
          <div id="rc1" style="height:260px"></div>
        </div>
        <div class="card chart-box">
          <div class="card-title">{{ t("rec.topRecommended") }}</div>
          <div id="rc2" style="height:260px"></div>
        </div>
      </div>

      <div class="card" style="margin-top:16px">
        <div class="card-title user-rec-title">
          <span>{{ t("rec.viewUserRecommendations") }}</span>
          <span class="user-rec-filter">
            {{ t("rec.userId") }}:
            <select v-model="uid" @change="loadUserRecs" class="inline-select">
              <option v-for="user in users" :key="user" :value="user">{{ user }}</option>
            </select>
          </span>
        </div>
        <div v-if="recs.length === 0" class="empty-rec">
          {{ t("rec.noUserData") }}
        </div>
        <div v-else class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>{{ t("rec.table.brand") }}</th>
                <th>{{ t("rec.table.model") }}</th>
                <th>{{ t("rec.table.price") }}</th>
                <th>{{ t("rec.table.score") }}</th>
                <th>{{ t("rec.table.source") }}</th>
                <th>{{ t("rec.table.status") }}</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(item, index) in recs"
                :key="index"
                class="clickable-row"
                :title="t('rec.clickToMark')"
                @click="onClick(item)"
              >
                <td>{{ index + 1 }}</td>
                <td><strong>{{ item.brand_name }}</strong></td>
                <td>{{ item.model_name }}</td>
                <td>{{ item.price }} {{ t("common.unitWan") }}</td>
                <td><span class="tag tag-green">{{ item.score }}</span></td>
                <td><span class="tag tag-orange">{{ valueLabel(item.rec_type) }}</span></td>
                <td><span :class="statusTag(item.status)">{{ statusLabel(item.status) }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="card" style="margin-top:16px">
        <div class="card-title">{{ t("rec.mostRecommendedCars") }}</div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>{{ t("rec.table.brand") }}</th>
                <th>{{ t("rec.table.model") }}</th>
                <th>{{ t("rec.table.type") }}</th>
                <th>{{ t("rec.table.price") }}</th>
                <th>{{ t("rec.table.recommendedCount") }}</th>
                <th>{{ t("rec.table.coveredUsers") }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="car in topCars" :key="car.car_id">
                <td><strong>{{ car.brand_name }}</strong></td>
                <td>{{ car.model_name }}</td>
                <td>{{ valueLabel(car.car_type) }}</td>
                <td>{{ car.price }} {{ t("common.unitWan") }}</td>
                <td>{{ car.rec_count.toLocaleString() }}</td>
                <td>{{ car.user_count }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-if="!isAdmin && !loading">
      <div class="filter-bar user-summary">
        {{ t("rec.currentUser") }}: <strong>{{ uid }}</strong>
        <span class="divider">|</span>
        {{ t("rec.forYou") }}
      </div>

      <div class="card">
        <div class="card-title">{{ t("rec.results", { count: recs.length }) }}</div>
        <div v-if="recs.length === 0" class="empty-rec">
          {{ t("rec.noPersonalized") }}
        </div>
        <div v-else class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>{{ t("rec.table.brand") }}</th>
                <th>{{ t("rec.table.model") }}</th>
                <th>{{ t("rec.table.price") }}</th>
                <th>{{ t("rec.table.score") }}</th>
                <th>{{ t("rec.table.source") }}</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(item, index) in recs"
                :key="index"
                class="clickable-row"
                :title="t('rec.clickToView')"
                @click="onClick(item)"
              >
                <td>{{ index + 1 }}</td>
                <td><strong>{{ item.brand_name }}</strong></td>
                <td>{{ item.model_name }}</td>
                <td>{{ item.price }} {{ t("common.unitWan") }}</td>
                <td><span class="tag tag-green">{{ item.score }}</span></td>
                <td><span class="tag tag-orange">{{ valueLabel(item.rec_type) }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="card" style="margin-top:16px">
        <div class="card-title">{{ t("rec.hotCars", { count: hot.length }) }}</div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>{{ t("rec.table.brand") }}</th>
                <th>{{ t("rec.table.model") }}</th>
                <th>{{ t("rec.table.price") }}</th>
                <th>{{ t("rec.table.views") }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="car in hot" :key="car.car_id">
                <td><strong>{{ car.brand_name }}</strong></td>
                <td>{{ car.model_name }}</td>
                <td>{{ car.price }} {{ t("common.unitWan") }}</td>
                <td>{{ car.view_count }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from "vue";

import api from "../api";
import { locale, t, valueLabel } from "../i18n";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const isAdmin = computed(() => auth.user?.role === "admin");
const uid = ref("user_0001");
const users = ref([]);
const recs = ref([]);
const hot = ref([]);
const topCars = ref([]);
const summary = ref({ total: 0, user_count: 0, by_type: [], by_status: [] });
const loading = ref(true);

function statusTag(status) {
  if (status === 0) return "tag";
  if (status === 1) return "tag tag-blue";
  if (status === 2) return "tag tag-green";
  return "tag tag-orange";
}

function statusLabel(status) {
  if (status === 0) return t("enum.recStatus.pending");
  if (status === 1) return t("enum.recStatus.exposed");
  if (status === 2) return t("enum.recStatus.clicked");
  return t("enum.recStatus.converted");
}

async function onClick(item) {
  try {
    await api.post("/rec/click", { user_id: uid.value, car_id: item.car_id });
    item.status = 2;
    item._clicked = true;
  } catch (error) {
    console.error(error);
  }
}

async function loadUserRecs() {
  try {
    const response = await api.get("/rec/home", { user_id: uid.value });
    recs.value = response.data || [];
  } catch (error) {
    console.error(error);
  }
}

onMounted(async () => {
  if (isAdmin.value) {
    try {
      const [summaryResponse, topCarsResponse, usersResponse, hotResponse] =
        await Promise.all([
          api.get("/rec/summary"),
          api.get("/rec/top-cars", { limit: 10 }),
          api.get("/rec/users"),
          api.get("/rec/hot"),
        ]);
      summary.value =
        summaryResponse.data ||
        { total: 0, user_count: 0, by_type: [], by_status: [] };
      topCars.value = topCarsResponse.data || [];
      users.value = usersResponse.data || [];
      hot.value = hotResponse.data || [];
      if (users.value.length > 0) uid.value = users.value[0];
    } catch (error) {
      console.error(error);
    }
    await loadUserRecs();
  } else {
    const username = auth.user?.username || "";
    const match = username.match(/\d+/);
    uid.value = match ? "user_" + match[0].padStart(4, "0") : "user_0001";
    try {
      const [hotResponse, usersResponse] = await Promise.all([
        api.get("/rec/hot"),
        api.get("/rec/users"),
      ]);
      hot.value = hotResponse.data || [];
      users.value = usersResponse.data || [];
    } catch (error) {
      console.error(error);
    }
    await loadUserRecs();
  }
  loading.value = false;

  if (isAdmin.value) {
    await nextTick();
    setTimeout(drawRecCharts, 200);
  }
});

watch(locale, () => {
  if (isAdmin.value && !loading.value) {
    drawRecCharts();
  }
});

function drawRecCharts() {
  const ec = window.echarts;
  if (!ec) return;
  const distributionElement = document.getElementById("rc1");
  if (
    distributionElement &&
    summary.value.by_type &&
    summary.value.by_type.length
  ) {
    ec.dispose(distributionElement);
    ec.init(distributionElement).setOption({
      tooltip: {
        trigger: "item",
        formatter: (item) => `${item.name}: ${item.value} (${item.percent}%)`,
      },
      legend: { bottom: 0, textStyle: { color: "#94a3b8", fontSize: 10 } },
      toolbox: {
        right: 10,
        feature: {
          saveAsImage: {
            title: t("common.saveImage"),
            pixelRatio: 2,
            backgroundColor: "#0a0e17",
          },
        },
      },
      animationDuration: 500,
      series: [
        {
          type: "pie",
          radius: ["40%", "65%"],
          center: ["50%", "45%"],
          data: summary.value.by_type.map((item) => ({
            name: valueLabel(item.rec_type),
            value: item.cnt,
          })),
          label: { color: "#94a3b8", fontSize: 11 },
          itemStyle: { borderColor: "#0a0e17", borderWidth: 2 },
        },
      ],
    });
  }

  const topCarsElement = document.getElementById("rc2");
  if (topCarsElement && topCars.value.length) {
    ec.dispose(topCarsElement);
    const topEight = topCars.value.slice(0, 8).reverse();
    ec.init(topCarsElement).setOption({
      tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
      toolbox: {
        right: 10,
        feature: {
          saveAsImage: {
            title: t("common.saveImage"),
            pixelRatio: 2,
            backgroundColor: "#0a0e17",
          },
        },
      },
      grid: { left: 100, right: 30, top: 5, bottom: 15 },
      xAxis: {
        type: "value",
        axisLabel: { color: "#94a3b8", fontSize: 9 },
        splitLine: { lineStyle: { color: "#1e293b" } },
      },
      yAxis: {
        type: "category",
        data: topEight.map((item) => `${item.brand_name} ${item.model_name}`),
        axisLabel: { color: "#94a3b8", fontSize: 9 },
      },
      animationDuration: 500,
      series: [
        {
          type: "bar",
          data: topEight.map((item) => ({
            value: item.rec_count,
            itemStyle: { borderRadius: [0, 4, 4, 0], color: "#8b5cf6" },
          })),
          barWidth: 12,
        },
      ],
    });
  }
}
</script>

<style scoped>
.user-rec-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.user-rec-filter {
  font-weight: normal;
  font-size: 12px;
}
.inline-select {
  width: 160px;
  padding: 4px 8px;
  border: 1px solid var(--border, #334155);
  border-radius: 4px;
  background: var(--bg-input, #1e293b);
  color: var(--text-primary, #e2e8f0);
  font-size: 13px;
}
.empty-rec {
  text-align: center;
  padding: 20px;
  color: var(--text-secondary);
}
.clickable-row {
  cursor: pointer;
}
.user-summary {
  margin-bottom: 12px;
  color: var(--text-secondary);
  font-size: 13px;
}
.divider {
  margin: 0 6px;
}
</style>
