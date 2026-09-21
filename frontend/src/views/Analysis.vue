<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">{{ t("analysis.title") }}</h1>
      <span class="refresh-badge">
        {{ t("common.refreshSeconds", { seconds: countdown }) }}
      </span>
    </div>
    <div v-if="loading" class="loading">{{ t("analysis.loading") }}</div>
    <div v-if="ok">
      <div class="chart-row">
        <div class="card chart-box">
          <div class="card-title">{{ t("analysis.chart.carPreference") }}</div>
          <div id="c3" style="height:300px"></div>
        </div>
        <div class="card chart-box">
          <div class="card-title">{{ t("analysis.chart.brandConsult") }}</div>
          <div id="c4" style="height:300px"></div>
        </div>
      </div>
      <div class="card">
        <div class="card-title">{{ t("analysis.loanApproval") }}</div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>{{ t("analysis.table.loanType") }}</th>
                <th>{{ t("analysis.table.approvalRate") }}</th>
                <th>{{ t("analysis.table.applications") }}</th>
                <th>{{ t("analysis.table.avgLoan") }}</th>
                <th>{{ t("analysis.table.monthlyPayment") }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in loanApproval" :key="row.loan_type">
                <td><span class="tag tag-blue">{{ valueLabel(row.loan_type) }}</span></td>
                <td>
                  <span
                    :class="row.avg_approval_rate >= 25 ? 'tag tag-green' : 'tag tag-orange'"
                  >
                    {{ row.avg_approval_rate }}
                  </span>
                </td>
                <td>{{ row.inquiry_count }}</td>
                <td>{{ row.avg_loan_amount }}</td>
                <td>{{ row.avg_monthly_payment }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="card">
        <div class="card-title">{{ t("analysis.dailyTrend") }}</div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>{{ t("analysis.table.date") }}</th>
                <th>{{ t("analysis.table.type") }}</th>
                <th>{{ t("analysis.table.pv") }}</th>
                <th>{{ t("analysis.table.uv") }}</th>
                <th>{{ t("analysis.table.searches") }}</th>
                <th>{{ t("analysis.table.consults") }}</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="row in trends.slice(0, 20)"
                :key="row.stats_date + row.stats_type"
              >
                <td>{{ row.stats_date }}</td>
                <td><span class="tag tag-blue">{{ valueLabel(row.stats_type) }}</span></td>
                <td>{{ row.total_pv }}</td>
                <td>{{ row.total_uv }}</td>
                <td>{{ row.total_search }}</td>
                <td>{{ row.total_consult }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="card">
        <div class="card-title">{{ t("analysis.recPerformance") }}</div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>{{ t("analysis.table.recType") }}</th>
                <th>{{ t("analysis.table.total") }}</th>
                <th>{{ t("analysis.table.exposures") }}</th>
                <th>{{ t("analysis.table.clicks") }}</th>
                <th>{{ t("analysis.table.conversions") }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in recs" :key="row.rec_type">
                <td><span class="tag tag-orange">{{ valueLabel(row.rec_type) }}</span></td>
                <td>{{ row.total_count }}</td>
                <td>{{ row.exposure_count }}</td>
                <td>{{ row.click_count }}</td>
                <td>{{ row.convert_count }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { nextTick, onMounted, onUnmounted, ref, watch } from "vue";

import api from "../api";
import { locale, t, valueLabel } from "../i18n";

const carTypes = ref([]);
const brandConsult = ref([]);
const loanApproval = ref([]);
const trends = ref([]);
const recs = ref([]);
const countdown = ref(7);
const loading = ref(true);
const ok = ref(false);
const carColors = {
  "SUV": "#3b82f6",
  "轿车": "#10b981",
  "MPV": "#f59e0b",
  "皮卡": "#ef4444",
  "猎装车": "#8b5cf6",
};

let timer = null;
let countdownTimer = null;

async function fetchData() {
  const safeGet = (url, params) =>
    api.get(url, params).then((response) => response.data).catch(() => null);
  const [types, consultations, loans, dailyTrends, recommendationStats] =
    await Promise.all([
      safeGet("/analysis/car-type-preference"),
      safeGet("/analysis/brand-consult-rate"),
      safeGet("/analysis/loan-approval-rate"),
      safeGet("/analysis/trend"),
      safeGet("/analysis/rec-stats"),
    ]);
  carTypes.value = types || [];
  brandConsult.value = consultations || [];
  loanApproval.value = loans || [];
  trends.value = dailyTrends || [];
  recs.value = recommendationStats || [];
  ok.value = true;
  loading.value = false;
  await nextTick();
  setTimeout(() => {
    const ec = window.echarts;
    if (!ec) return;
    drawCarTypeChart(ec);
    drawBrandConsultChart(ec);
  }, 300);
}

function drawCarTypeChart(ec) {
  const element = document.getElementById("c3");
  if (!element || !carTypes.value.length) return;
  ec.dispose(element);
  ec.init(element).setOption({
    tooltip: { trigger: "item" },
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
    animationDurationUpdate: 600,
    series: [
      {
        type: "pie",
        radius: ["40%", "65%"],
        center: ["50%", "45%"],
        data: carTypes.value.map((row) => ({
          name: valueLabel(row.car_type),
          value: row.total_pv,
          itemStyle: { color: carColors[row.car_type] || "#3b82f6" },
        })),
        label: { color: "#94a3b8", fontSize: 11 },
        itemStyle: { borderColor: "#0a0e17", borderWidth: 2 },
      },
    ],
  });
}

function drawBrandConsultChart(ec) {
  const element = document.getElementById("c4");
  if (!element || !brandConsult.value.length) return;
  ec.dispose(element);
  ec.init(element).setOption({
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
    grid: { left: 55, right: 20, top: 10, bottom: 25 },
    xAxis: {
      type: "category",
      data: brandConsult.value.map((row) => row.brand_name),
      axisLabel: { color: "#94a3b8", fontSize: 10 },
    },
    yAxis: {
      name: "%",
      axisLabel: { color: "#94a3b8" },
      splitLine: { lineStyle: { color: "#1e293b" } },
    },
    animationDuration: 500,
    animationDurationUpdate: 600,
    series: [
      {
        type: "bar",
        data: brandConsult.value.map((row) => ({
          value: row.consult_rate,
          itemStyle: { borderRadius: [5, 5, 0, 0], color: "#ef4444" },
        })),
        barWidth: 22,
      },
    ],
  });
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

watch(locale, async () => {
  await nextTick();
  const ec = window.echarts;
  if (ec) {
    drawCarTypeChart(ec);
    drawBrandConsultChart(ec);
  }
});
</script>
