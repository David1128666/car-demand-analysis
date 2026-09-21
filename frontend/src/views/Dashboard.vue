<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">{{ t("dashboard.title") }}</h1>
      <span class="refresh-badge">
        {{ t("common.refreshSeconds", { seconds: countdown }) }}
      </span>
    </div>
    <div v-if="loading" class="loading">{{ t("dashboard.loading") }}</div>
    <div v-if="ok">
      <div class="stat-grid">
        <div class="stat-card">
          <div class="label">{{ t("dashboard.metric.pv") }}</div>
          <div class="value">{{ ov.total_pv }}</div>
        </div>
        <div class="stat-card">
          <div class="label">{{ t("dashboard.metric.uv") }}</div>
          <div class="value">{{ ov.total_uv }}</div>
        </div>
        <div class="stat-card">
          <div class="label">{{ t("dashboard.metric.searches") }}</div>
          <div class="value">{{ ov.search_count }}</div>
        </div>
        <div class="stat-card">
          <div class="label">{{ t("dashboard.metric.consults") }}</div>
          <div class="value">{{ ov.consult_count }}</div>
        </div>
        <div class="stat-card">
          <div class="label">{{ t("dashboard.metric.collects") }}</div>
          <div class="value">{{ ov.collect_count }}</div>
        </div>
        <div class="stat-card">
          <div class="label">{{ t("dashboard.metric.cars") }}</div>
          <div class="value">{{ ov.car_count }}</div>
        </div>
        <div class="stat-card">
          <div class="label">{{ t("dashboard.metric.loanAvgPrice") }}</div>
          <div class="value">{{ fin.avg_car_price?.toFixed(1) }}</div>
        </div>
        <div class="stat-card">
          <div class="label">{{ t("dashboard.metric.avgRate") }}</div>
          <div class="value">{{ fin.avg_rate?.toFixed(2) }}</div>
        </div>
      </div>
      <div class="chart-row">
        <div class="card chart-box">
          <div class="card-title">{{ t("dashboard.chart.realtime") }}</div>
          <div id="c1" style="height:300px"></div>
        </div>
        <div class="card chart-box">
          <div class="card-title">{{ t("dashboard.chart.behavior") }}</div>
          <div id="c2" style="height:300px"></div>
        </div>
      </div>
      <div class="card">
        <div class="card-title">{{ t("dashboard.chart.prices") }}</div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>{{ t("dashboard.table.brand") }}</th>
                <th>{{ t("dashboard.table.model") }}</th>
                <th>{{ t("dashboard.table.msrp") }}</th>
                <th>{{ t("dashboard.table.transaction") }}</th>
                <th>{{ t("dashboard.table.discount") }}</th>
                <th>{{ t("dashboard.table.inquiries") }}</th>
                <th>{{ t("dashboard.table.promotion") }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(r, i) in prices.slice(0, 10)" :key="i">
                <td><strong>{{ r.brand_name }}</strong></td>
                <td>{{ valueLabel(r.car_type) }}</td>
                <td>{{ r.avg_original_price }}</td>
                <td>{{ r.avg_quoted_price }}</td>
                <td><span class="tag tag-green">-{{ r.discount_pct }}%</span></td>
                <td>{{ r.quote_count }}</td>
                <td class="promotion-cell">
                  {{ r.top_promotion ? promotionLabel(r.top_promotion) : t("dashboard.noPromotion") }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref, watch } from "vue";

import api from "../api";
import { locale, promotionLabel, t, valueLabel } from "../i18n";

const ov = ref({});
const fin = ref({});
const prices = ref([]);
const countdown = ref(7);
const loading = ref(true);
const ok = ref(false);

let timer = null;
let countdownTimer = null;
let latestRealtimeData = [];

async function fetchData() {
  const safeGet = (url, params) =>
    api.get(url, params).then((response) => response.data).catch(() => null);

  const [overview, finance, priceStats, realtime] = await Promise.all([
    safeGet("/dashboard/overview"),
    safeGet("/dashboard/finance-summary"),
    safeGet("/dashboard/price-stats"),
    safeGet("/dashboard/realtime-stats"),
  ]);
  ov.value = overview || {};
  fin.value = finance || {};
  prices.value = priceStats || [];
  const realtimeData = realtime || [];
  latestRealtimeData = realtimeData;
  ok.value = true;
  if (realtimeData.length) {
    setTimeout(() => drawCharts(realtimeData), 300);
  }
  loading.value = false;
}

onMounted(() => {
  fetchData();
  countdownTimer = setInterval(() => {
    countdown.value = countdown.value <= 1 ? 7 : countdown.value - 1;
  }, 1000);
  timer = setInterval(fetchData, 7000);
});

onUnmounted(() => {
  if (timer) clearInterval(timer);
  if (countdownTimer) clearInterval(countdownTimer);
});

watch(locale, () => {
  if (latestRealtimeData.length) {
    drawCharts(latestRealtimeData);
  }
});

function drawCharts(data) {
  const ec = window.echarts;
  if (!ec) return;
  const c1El = document.getElementById("c1");
  if (c1El) {
    ec.dispose(c1El);
    const grouped = {};
    data.forEach((row) => {
      const parts =
        row.stats_minute && row.stats_minute.includes(":")
          ? row.stats_minute.split(":")
          : ["00", "00"];
      const totalSeconds = parseInt(parts[0], 10) * 60 + parseInt(parts[1], 10);
      const bucket = Math.floor(totalSeconds / 30) * 30;
      const bucketMinutes = String(Math.floor(bucket / 60)).padStart(2, "0");
      const bucketSeconds = String(bucket % 60).padStart(2, "0");
      const time = `${String(row.stats_hour || 0).padStart(2, "0")}:${bucketMinutes}:${bucketSeconds}`;
      const label = `${row.stats_date} ${time}`;
      grouped[label] = (grouped[label] || 0) + row.pv;
    });
    const dates = Object.keys(grouped).sort().slice(-5);
    ec.init(c1El).setOption({
      tooltip: { trigger: "axis" },
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
      grid: { left: 40, right: 15, top: 15, bottom: 30 },
      xAxis: { data: dates, axisLabel: { color: "#94a3b8", fontSize: 10 } },
      yAxis: {
        axisLabel: { color: "#94a3b8" },
        splitLine: { lineStyle: { color: "#1e293b" } },
      },
      animationDuration: 500,
      animationDurationUpdate: 600,
      series: [
        {
          type: "line",
          data: dates.map((date) => grouped[date]),
          smooth: true,
          lineStyle: { color: "#3b82f6", width: 2 },
          areaStyle: { color: "rgba(59,130,246,0.12)" },
        },
      ],
    });
  }

  const c2El = document.getElementById("c2");
  if (c2El) {
    ec.dispose(c2El);
    const merged = {};
    data.forEach((row) => {
      const label = valueLabel(row.stats_type);
      merged[label] = (merged[label] || 0) + row.pv;
    });
    ec.init(c2El).setOption({
      tooltip: { trigger: "item" },
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
      animationDurationUpdate: 600,
      series: [
        {
          type: "pie",
          radius: ["40%", "65%"],
          data: Object.entries(merged).map(([name, value]) => ({ name, value })),
          label: { color: "#94a3b8", fontSize: 11 },
          itemStyle: { borderColor: "#0a0e17", borderWidth: 2 },
        },
      ],
    });
  }
}
</script>

<style scoped>
.promotion-cell {
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--warning);
}
</style>
