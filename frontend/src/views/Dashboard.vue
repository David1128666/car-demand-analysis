<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">📊 数据大屏</h1>
      <span class="refresh-badge">刷新 {{ countdown }}s</span>
    </div>
    <div v-if="loading" class="loading">⏳ 加载中...</div>
    <div v-if="ok">
      <div class="stat-grid">
        <div class="stat-card"><div class="label">总访问量 PV</div><div class="value">{{ ov.total_pv }}</div></div>
        <div class="stat-card"><div class="label">独立访客 UV</div><div class="value">{{ ov.total_uv }}</div></div>
        <div class="stat-card"><div class="label">搜索次数</div><div class="value">{{ ov.search_count }}</div></div>
        <div class="stat-card"><div class="label">咨询次数</div><div class="value">{{ ov.consult_count }}</div></div>
        <div class="stat-card"><div class="label">收藏次数</div><div class="value">{{ ov.collect_count }}</div></div>
        <div class="stat-card"><div class="label">在售车型</div><div class="value">{{ ov.car_count }}</div></div>
        <div class="stat-card"><div class="label">贷款均价(万)</div><div class="value">{{ fin.avg_car_price?.toFixed(1) }}</div></div>
        <div class="stat-card"><div class="label">平均利率(%)</div><div class="value">{{ fin.avg_rate?.toFixed(2) }}</div></div>
      </div>
      <div class="chart-row">
        <div class="card chart-box"><div class="card-title">📈 实时访问趋势</div><div id="c1" style="height:300px"></div></div>
        <div class="card chart-box"><div class="card-title">🍩 行为类型分布</div><div id="c2" style="height:300px"></div></div>
      </div>
      <div class="card"><div class="card-title">💰 品牌报价分析</div>
        <div class="table-wrap"><table><thead><tr><th>品牌</th><th>车型</th><th>指导价(万)</th><th>成交价(万)</th><th>优惠</th><th>询价量</th><th>促销活动</th></tr></thead>
        <tbody><tr v-for="(r,i) in prices.slice(0,10)" :key="i">
          <td><strong>{{ r.brand_name }}</strong></td>
          <td>{{ r.car_type }}</td>
          <td>{{ r.avg_original_price }}</td>
          <td>{{ r.avg_quoted_price }}</td>
          <td><span class="tag tag-green">-{{ r.discount_pct }}%</span></td>
          <td>{{ r.quote_count }}</td>
          <td style="max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--warning)">{{ r.top_promotion || '暂无优惠' }}</td>
        </tr></tbody></table></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import api from "../api";
const ov = ref({}); const fin = ref({}); const prices = ref([]);
const countdown = ref(7);
const loading = ref(true); const ok = ref(false);

const CN = { search: "搜索", consult: "咨询", beh_browse: "浏览", beh_collect: "收藏", beh_consult: "咨询", beh_search: "搜索" };

let _timer = null;

async function fetchData() {
  const safeGet = (url, params) => api.get(url, params).then(r => r.data).catch(() => null);

  const [d1, d2, d3, d4] = await Promise.all([
    safeGet("/dashboard/overview"), safeGet("/dashboard/finance-summary"),
    safeGet("/dashboard/price-stats"), safeGet("/dashboard/realtime-stats"),
  ]);
  ov.value = d1 || {}; fin.value = d2 || {}; prices.value = d3 || [];
  const rtData = d4 || [];
  ok.value = true;
  if (rtData && rtData.length) setTimeout(() => drawCharts(rtData), 300);
  loading.value = false;
}

let _cdTimer = null;
onMounted(() => {
  fetchData();
  _cdTimer = setInterval(() => {
    countdown.value = countdown.value <= 1 ? 7 : countdown.value - 1;
  }, 1000);
  _timer = setInterval(fetchData, 7000);
});
onUnmounted(() => {
  if (_timer) clearInterval(_timer);
  if (_cdTimer) clearInterval(_cdTimer);
});

function drawCharts(data) {
  const ec = window.echarts; if (!ec) return;
  const c1El = document.getElementById("c1");
  if (c1El) {
    ec.dispose(c1El);
    const grouped = {}; data.forEach(r => { const parts = (r.stats_minute && r.stats_minute.includes(':')) ? r.stats_minute.split(':') : ['00','00']; const totalSec = parseInt(parts[0]) * 60 + parseInt(parts[1]); const bucket30s = Math.floor(totalSec / 30) * 30; const bucketMin = String(Math.floor(bucket30s / 60)).padStart(2,"0"); const bucketSec = String(bucket30s % 60).padStart(2,"0"); const tm = String(r.stats_hour||0).padStart(2,"0") + ":" + bucketMin + ":" + bucketSec; const label = r.stats_date + " " + tm; grouped[label] = (grouped[label]||0) + r.pv; });
    const allKeys = Object.keys(grouped).sort(); const dates = allKeys.slice(-5);
    ec.init(c1El).setOption({
      tooltip: { trigger: "axis" }, toolbox: { right: 10, feature: { saveAsImage: { title: "保存", pixelRatio: 2, backgroundColor: "#0a0e17" } } },
      grid: { left: 40, right: 15, top: 15, bottom: 30 },
      xAxis: { data: dates, axisLabel: { color: "#94a3b8", fontSize: 10 } },
      yAxis: { axisLabel: { color: "#94a3b8" }, splitLine: { lineStyle: { color: "#1e293b" } } },
      animationDuration: 500, animationDurationUpdate: 600,
      series: [{ type: "line", data: dates.map(d => grouped[d]), smooth: true, lineStyle: { color: "#3b82f6", width: 2 }, areaStyle: { color: "rgba(59,130,246,0.12)" } }]
    });
  }
  const c2El = document.getElementById("c2");
  if (c2El) {
    ec.dispose(c2El);
    const merged = {};
    data.forEach(r => { const label = CN[r.stats_type] || r.stats_type; merged[label] = (merged[label]||0) + r.pv; });
    ec.init(c2El).setOption({
      tooltip: { trigger: "item" }, toolbox: { right: 10, feature: { saveAsImage: { title: "保存", pixelRatio: 2, backgroundColor: "#0a0e17" } } },
      animationDuration: 500, animationDurationUpdate: 600,
      series: [{ type: "pie", radius: ["40%","65%"], data: Object.entries(merged).map(([k,v]) => ({ name: k, value: v })), label: { color: "#94a3b8", fontSize: 11 }, itemStyle: { borderColor: "#0a0e17", borderWidth: 2 } }]
    });
  }
}
</script>