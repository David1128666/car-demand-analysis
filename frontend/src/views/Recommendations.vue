<template>
  <div>
    <h1 class="page-title">🎯 智能推荐</h1>
    <div v-if="loading" class="loading">⏳ 加载中...</div>

    <!-- ===== ADMIN VIEW ===== -->
    <div v-if="isAdmin && !loading">
      <!-- Summary Cards -->
      <div class="stat-grid">
        <div class="stat-card"><div class="label">推荐总数</div><div class="value">{{ summary.total.toLocaleString() }}</div></div>
        <div class="stat-card"><div class="label">覆盖用户数</div><div class="value">{{ summary.user_count }}</div></div>
        <div class="stat-card" v-for="t in summary.by_type" :key="t.rec_type">
          <div class="label">{{ cnRec(t.rec_type) }}</div><div class="value">{{ t.cnt.toLocaleString() }}</div>
        </div>
      </div>

      <!-- Admin Charts -->
      <div class="chart-row" style="margin-top:16px">
        <div class="card chart-box"><div class="card-title">推荐来源分布</div><div id="rc1" style="height:260px"></div></div>
        <div class="card chart-box"><div class="card-title">最常推荐车型 Top8</div><div id="rc2" style="height:260px"></div></div>
      </div>

      <!-- User Browser -->
      <div class="card" style="margin-top:16px">
        <div class="card-title" style="display:flex;justify-content:space-between;align-items:center">
          <span>🔍 查看用户推荐</span>
          <span style="font-weight:normal;font-size:12px">
            用户ID：<select v-model="uid" @change="loadUserRecs" class="inline-select" style="width:160px">
              <option v-for="u in users" :key="u" :value="u">{{ u }}</option>
            </select>
          </span>
        </div>
        <div v-if="recs.length === 0" style="text-align:center;padding:20px;color:var(--text-secondary)">该用户暂无推荐数据</div>
        <div v-else class="table-wrap"><table><thead><tr><th>#</th><th>品牌</th><th>车型</th><th>价格</th><th>得分</th><th>来源</th><th>状态</th></tr></thead>
        <tbody><tr v-for="(r,i) in recs" :key="i" @click="onClick(r)" style="cursor:pointer" :title="'点击标记为已点击'">
          <td>{{ i+1 }}</td><td><strong>{{ r.brand_name }}</strong></td><td>{{ r.model_name }}</td>
          <td>{{ r.price }}万</td><td><span class="tag tag-green">{{ r.score }}</span></td>
          <td><span class="tag tag-orange">{{ cnRec(r.rec_type) }}</span></td>
          <td><span :class="statusTag(r.status)">{{ statusLabel(r.status) }}</span></td>
        </tr></tbody></table></div>
      </div>

      <!-- Top Recommended Cars -->
      <div class="card" style="margin-top:16px">
        <div class="card-title">🔥 最常被推荐的车型</div>
        <div class="table-wrap"><table><thead><tr><th>品牌</th><th>车型</th><th>类型</th><th>价格</th><th>被推荐次数</th><th>覆盖用户</th></tr></thead>
        <tbody><tr v-for="c in topCars" :key="c.car_id">
          <td><strong>{{ c.brand_name }}</strong></td><td>{{ c.model_name }}</td>
          <td>{{ c.car_type }}</td><td>{{ c.price }}万</td>
          <td>{{ c.rec_count.toLocaleString() }}</td><td>{{ c.user_count }}</td>
        </tr></tbody></table></div>
      </div>
    </div>

    <!-- ===== USER VIEW ===== -->
    <div v-if="!isAdmin && !loading">
      <div class="filter-bar" style="margin-bottom:12px;color:var(--text-secondary);font-size:13px">
        当前用户：<strong>{{ uid }}</strong> &nbsp;|&nbsp; 为你推荐以下车型
      </div>

      <div class="card"><div class="card-title">📋 推荐结果 ({{ recs.length }}条)</div>
        <div v-if="recs.length === 0" style="text-align:center;padding:20px;color:var(--text-secondary)">
          暂无个性化推荐，以下为你展示热门车型
        </div>
        <div v-else class="table-wrap"><table><thead><tr><th>#</th><th>品牌</th><th>车型</th><th>价格</th><th>得分</th><th>来源</th></tr></thead>
        <tbody><tr v-for="(r,i) in recs" :key="i" @click="onClick(r)" style="cursor:pointer" :title="'点击查看详情'">
          <td>{{ i+1 }}</td><td><strong>{{ r.brand_name }}</strong></td><td>{{ r.model_name }}</td>
          <td>{{ r.price }}万</td><td><span class="tag tag-green">{{ r.score }}</span></td>
          <td><span class="tag tag-orange">{{ cnRec(r.rec_type) }}</span></td>
        </tr></tbody></table></div>
      </div>

      <div class="card" style="margin-top:16px"><div class="card-title">🔥 热门车型 ({{ hot.length }}条)</div>
        <div class="table-wrap"><table><thead><tr><th>品牌</th><th>车型</th><th>价格</th><th>浏览量</th></tr></thead>
        <tbody><tr v-for="h in hot" :key="h.car_id"><td><strong>{{ h.brand_name }}</strong></td><td>{{ h.model_name }}</td><td>{{ h.price }}万</td><td>{{ h.view_count }}</td></tr></tbody></table></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from "vue";
import { useAuthStore } from "../stores/auth";
import api from "../api";

const auth = useAuthStore();
const isAdmin = computed(() => auth.user?.role === "admin");

const uid = ref("user_0001");
const users = ref([]);
const recs = ref([]);
const hot = ref([]);
const topCars = ref([]);
const summary = ref({ total: 0, user_count: 0, by_type: [], by_status: [] });
const loading = ref(true);

const REC_CN = { collaborative: "协同过滤", content_based: "内容推荐", hot: "热门推荐" };
function cnRec(t) { return REC_CN[t] || t; }
function statusTag(s) {
  if (s === 0) return "tag";
  if (s === 1) return "tag tag-blue";
  if (s === 2) return "tag tag-green";
  return "tag tag-orange";
}
function statusLabel(s) {
  if (s === 0) return "待曝光";
  if (s === 1) return "已曝光";
  if (s === 2) return "已点击";
  return "已转化";
}

async function onClick(r) {
  try {
    await api.post("/rec/click", { user_id: uid.value, car_id: r.car_id });
    r.status = 2;
    r._clicked = true;
  } catch (e) { console.error(e); }
}

async function loadUserRecs() {
  try {
    const r = await api.get("/rec/home", { user_id: uid.value });
    recs.value = r.data || [];
  } catch (e) { console.error(e); }
}

onMounted(async () => {
  if (isAdmin.value) {
    // Admin: load summary + top cars + user browser
    try {
      const [s, t, u, h] = await Promise.all([
        api.get("/rec/summary"),
        api.get("/rec/top-cars", { limit: 10 }),
        api.get("/rec/users"),
        api.get("/rec/hot"),
      ]);
      summary.value = s.data || { total: 0, user_count: 0, by_type: [], by_status: [] };
      topCars.value = t.data || [];
      users.value = u.data || [];
      hot.value = h.data || [];
      if (users.value.length > 0) uid.value = users.value[0];
    } catch (e) { console.error(e); }
    await loadUserRecs();
  } else {
    // Regular user: derive rec user_id from username (user001→user_0001)
    const username = auth.user?.username || "";
    const m = username.match(/\d+/);
    uid.value = m ? "user_" + m[0].padStart(4, "0") : "user_0001";
    try {
      const [h, u] = await Promise.all([
        api.get("/rec/hot"),
        api.get("/rec/users"),
      ]);
      hot.value = h.data || [];
      users.value = u.data || [];
    } catch (e) { console.error(e); }
    await loadUserRecs();
  }
  loading.value = false;

  if (isAdmin.value) {
    await nextTick();
    setTimeout(function(){ drawRecCharts(); }, 200);
  }
});

function drawRecCharts() {
  var ec = window.echarts; if (!ec) return;
  // rc1 — rec type distribution donut
  var el1 = document.getElementById("rc1");
  if (el1 && summary.value.by_type && summary.value.by_type.length) {
    ec.dispose(el1);
    var c1 = ec.init(el1);
    c1.setOption({
      tooltip: { trigger: "item", formatter: function(p) { return p.name + ": " + p.value + " (" + p.percent + "%)"; } },
      legend: { bottom: 0, textStyle: { color: "#94a3b8", fontSize: 10 } },
      toolbox: { right: 10, feature: { saveAsImage: { title: "保存", pixelRatio: 2, backgroundColor: "#0a0e17" } } },
      animationDuration: 500,
      series: [{ type: "pie", radius: ["40%", "65%"], center: ["50%", "45%"],
        data: summary.value.by_type.map(function(t) { return { name: cnRec(t.rec_type), value: t.cnt }; }),
        label: { color: "#94a3b8", fontSize: 11 }, itemStyle: { borderColor: "#0a0e17", borderWidth: 2 }
      }]
    });
  }
  // rc2 — top cars horizontal bar
  var el2 = document.getElementById("rc2");
  if (el2 && topCars.value.length) {
    ec.dispose(el2);
    var c2 = ec.init(el2);
    var top8 = topCars.value.slice(0, 8).reverse();
    c2.setOption({
      tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
      toolbox: { right: 10, feature: { saveAsImage: { title: "保存", pixelRatio: 2, backgroundColor: "#0a0e17" } } },
      grid: { left: 100, right: 30, top: 5, bottom: 15 },
      xAxis: { type: "value", axisLabel: { color: "#94a3b8", fontSize: 9 }, splitLine: { lineStyle: { color: "#1e293b" } } },
      yAxis: { type: "category", data: top8.map(function(r) { return r.brand_name + " " + r.model_name; }), axisLabel: { color: "#94a3b8", fontSize: 9 } },
      animationDuration: 500,
      series: [{ type: "bar", data: top8.map(function(r) { return { value: r.rec_count, itemStyle: { borderRadius: [0, 4, 4, 0], color: "#8b5cf6" } }; }), barWidth: 12 }]
    });
  }
}
</script>

<style scoped>
.inline-select { padding: 4px 8px; border: 1px solid var(--border, #334155); border-radius: 4px; background: var(--bg-input, #1e293b); color: var(--text-primary, #e2e8f0); font-size: 13px; }
</style>
