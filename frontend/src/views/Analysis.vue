<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">📈 数据分析</h1>
      <span class="refresh-badge">刷新 {{ countdown }}s</span>
    </div>
    <div v-if="loading" class="loading">⏳ 加载中...</div>
    <div v-if="ok">
      <div class="chart-row">
        <div class="card chart-box"><div class="card-title">车型偏好分析</div><div id="c3" style="height:300px"></div></div>
        <div class="card chart-box"><div class="card-title">品牌询价转化率</div><div id="c4" style="height:300px"></div></div>
      </div>
      <div class="card"><div class="card-title">贷款审批率排行</div>
        <div class="table-wrap"><table><thead><tr><th>贷款类型</th><th>审批率%</th><th>申请数</th><th>均额(万)</th><th>月供(元)</th></tr></thead>
        <tbody><tr v-for="r in loanApproval" :key="r.loan_type"><td><span class="tag tag-blue">{{ r.loan_type }}</span></td><td><span :class="r.avg_approval_rate >= 25 ? 'tag tag-green' : 'tag tag-orange'">{{ r.avg_approval_rate }}</span></td><td>{{ r.inquiry_count }}</td><td>{{ r.avg_loan_amount }}</td><td>{{ r.avg_monthly_payment }}</td></tr></tbody></table></div></div>
      <div class="card"><div class="card-title">📅 每日趋势明细</div>
        <div class="table-wrap"><table><thead><tr><th>日期</th><th>类型</th><th>浏览量</th><th>访客数</th><th>搜索</th><th>咨询</th></tr></thead>
        <tbody><tr v-for="t in trends.slice(0,20)" :key="t.stats_date+t.stats_type"><td>{{ t.stats_date }}</td><td><span class="tag tag-blue">{{ cnType(t.stats_type) }}</span></td><td>{{ t.total_pv }}</td><td>{{ t.total_uv }}</td><td>{{ t.total_search }}</td><td>{{ t.total_consult }}</td></tr></tbody></table></div></div>
      <div class="card"><div class="card-title">🎯 推荐效果统计</div>
        <div class="table-wrap"><table><thead><tr><th>推荐类型</th><th>总数</th><th>曝光</th><th>点击</th><th>转化</th></tr></thead>
        <tbody><tr v-for="r in recs" :key="r.rec_type"><td><span class="tag tag-orange">{{ cnRecType(r.rec_type) }}</span></td><td>{{ r.total_count }}</td><td>{{ r.exposure_count }}</td><td>{{ r.click_count }}</td><td>{{ r.convert_count }}</td></tr></tbody></table></div></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from "vue";
import api from "../api";
const carTypes = ref([]); const brandConsult = ref([]); const loanApproval = ref([]); const trends = ref([]); const recs = ref([]);
const countdown = ref(7);
const loading = ref(true); const ok = ref(false);

const TYPE_CN = { search: "搜索", consult: "咨询", beh_browse: "浏览", beh_collect: "收藏", beh_consult: "咨询", beh_search: "搜索" };
const REC_CN = { collaborative: "协同过滤", content_based: "内容推荐", hot: "热门推荐", hybrid: "混合推荐" };
const CAR_COLORS = { "SUV": "#3b82f6", "轿车": "#10b981", "MPV": "#f59e0b", "皮卡": "#ef4444", "猎装车": "#8b5cf6" };
function cnType(t) { return TYPE_CN[t] || t; }
function cnRecType(t) { return REC_CN[t] || t; }

let _timer = null;

async function fetchData() {
  const safeGet = (url, params) => api.get(url, params).then(r => r.data).catch(() => null);

  const [d1, d2, d3, d4, d5] = await Promise.all([
    safeGet("/analysis/car-type-preference"), safeGet("/analysis/brand-consult-rate"),
    safeGet("/analysis/loan-approval-rate"), safeGet("/analysis/trend"),
    safeGet("/analysis/rec-stats")
  ]);
  carTypes.value = d1 || []; brandConsult.value = d2 || [];
  loanApproval.value = d3 || []; trends.value = d4 || []; recs.value = d5 || [];
  ok.value = true;
  loading.value = false;
  await nextTick();
  setTimeout(() => {
    const ec = window.echarts; if (!ec) return;
    drawCarTypeChart(ec);
    drawBrandConsultChart(ec);
  }, 300);
}

function drawCarTypeChart(ec) {
  const el = document.getElementById("c3");
  if (!el || !carTypes.value.length) return;
  ec.dispose(el);
  const c = ec.init(el);
  c.setOption({
    tooltip: { trigger: "item" },
    legend: { bottom: 0, textStyle: { color: "#94a3b8", fontSize: 10 } },
    toolbox: { right: 10, feature: { saveAsImage: { title: "保存", pixelRatio: 2, backgroundColor: "#0a0e17" } } },
    animationDuration: 500, animationDurationUpdate: 600,
    series: [{ type: "pie", radius: ["40%","65%"], center: ["50%","45%"],
      data: carTypes.value.map(r => ({ name: r.car_type, value: r.total_pv, itemStyle: { color: CAR_COLORS[r.car_type] || "#3b82f6" } })),
      label: { color: "#94a3b8", fontSize: 11 }, itemStyle: { borderColor: "#0a0e17", borderWidth: 2 }
    }]
  });
}

function drawBrandConsultChart(ec) {
  const el = document.getElementById("c4");
  if (!el || !brandConsult.value.length) return;
  ec.dispose(el);
  const c = ec.init(el);
  c.setOption({
    tooltip: { trigger: "axis" },
    toolbox: { right: 10, feature: { saveAsImage: { title: "保存", pixelRatio: 2, backgroundColor: "#0a0e17" } } },
    grid: { left: 55, right: 20, top: 10, bottom: 25 },
    xAxis: { type: "category", data: brandConsult.value.map(r => r.brand_name), axisLabel: { color: "#94a3b8", fontSize: 10 } },
    yAxis: { name: "%", axisLabel: { color: "#94a3b8" }, splitLine: { lineStyle: { color: "#1e293b" } } },
    animationDuration: 500, animationDurationUpdate: 600,
    series: [{ type: "bar", data: brandConsult.value.map(r => ({ value: r.consult_rate, itemStyle: { borderRadius: [5,5,0,0], color: "#ef4444" } })), barWidth: 22 }]
  });
}

let _cdTimer = null;
onMounted(() => {
  fetchData();
  _cdTimer = setInterval(() => { countdown.value = countdown.value <= 1 ? 7 : countdown.value - 1; }, 1000);
  _timer = setInterval(fetchData, 7000);
});
onUnmounted(() => {
  if (_timer) clearInterval(_timer);
  if (_cdTimer) clearInterval(_cdTimer);
});
</script>