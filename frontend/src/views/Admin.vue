<template>
  <div>
    <h1 class="page-title">⚙️ 后台管理</h1>

    <div class="admin-tabs">
      <button v-for="t in tabs" :key="t.key" :class="['tab-btn', { active: activeTab === t.key }]" @click="switchTab(t.key)">{{ t.label }}</button>
    </div>

    <div v-if="tabLoading" class="loading">⏳ 加载中...</div>
    <div v-if="tabError" class="error-msg">❌ {{ tabError }}</div>

    <!-- Tab 1: 用户管理 -->
    <div v-if="activeTab === 'users' && !tabLoading">
      <div class="card"><div class="card-title">👥 用户列表 ({{ users.length }}人)</div>
        <div class="table-wrap"><table><thead><tr>
          <th>ID</th><th>用户名</th><th>昵称</th><th>角色</th><th>状态</th><th>邮箱</th><th>手机</th><th>最后登录</th><th>操作</th>
        </tr></thead>
        <tbody><tr v-for="u in users" :key="u.user_id">
          <td>{{ u.user_id }}</td>
          <td><strong>{{ u.username }}</strong></td>
          <td>{{ u.nickname }}</td>
          <td>
            <select :value="u.role" @change="changeRole(u, $event.target.value)" class="inline-select">
              <option value="admin">admin</option>
              <option value="user">user</option>
            </select>
          </td>
          <td><span :class="u.status === 1 ? 'tag tag-green' : 'tag tag-red'" style="cursor:pointer" @click="toggleStatus(u)">{{ u.status === 1 ? '正常' : '禁用' }}</span></td>
          <td>{{ u.email || '-' }}</td>
          <td>{{ u.phone || '-' }}</td>
          <td>{{ fmtTime(u.last_login) }}</td>
          <td>
            <button class="btn btn-sm btn-primary" @click="showResetPwd(u)" style="margin-right:4px">重置密码</button>
            <button class="btn btn-sm btn-danger" @click="delUser(u)">删除</button>
          </td>
        </tr></tbody></table></div>
      </div>

      <div class="card" style="margin-top:16px"><div class="card-title">➕ 新增用户</div>
        <div class="form-row">
          <input v-model="newUser.username" placeholder="用户名" class="form-input" />
          <input v-model="newUser.password" placeholder="密码" type="password" class="form-input" />
          <input v-model="newUser.nickname" placeholder="昵称" class="form-input" />
          <select v-model="newUser.role" class="form-input"><option value="user">user</option><option value="admin">admin</option></select>
          <input v-model="newUser.email" placeholder="邮箱(可选)" class="form-input" />
          <input v-model="newUser.phone" placeholder="手机(可选)" class="form-input" />
          <button class="btn btn-primary" @click="createUser">创建</button>
        </div>
        <div v-if="createMsg" :class="createOk ? 'success-msg' : 'error-msg'" style="margin-top:8px">{{ createMsg }}</div>
      </div>

      <!-- Reset Password Modal -->
      <div v-if="resetTarget" class="modal-overlay" @click.self="resetTarget = null">
        <div class="modal-box">
          <h3>重置密码 - {{ resetTarget.username }}</h3>
          <input v-model="resetPwd" type="text" placeholder="输入新密码" class="form-input" style="width:100%;margin:12px 0" />
          <div style="text-align:right"><button class="btn btn-sm" @click="resetTarget = null" style="margin-right:8px">取消</button><button class="btn btn-sm btn-primary" @click="doResetPwd">确认重置</button></div>
        </div>
      </div>
    </div>

    <!-- Tab 2: 系统监控 -->
    <div v-if="activeTab === 'monitor' && !tabLoading">
      <div class="stat-grid">
        <div class="stat-card" v-for="s in recSummary" :key="s.label"><div class="label">{{ s.label }}</div><div class="value">{{ s.value }}</div></div>
      </div>

      <div class="card" style="margin-top:16px"><div class="card-title">🗄️ 数据库表统计</div>
        <div class="table-wrap"><table><thead><tr><th>表名</th><th>行数</th><th>大小(KB)</th><th>最后更新</th></tr></thead>
        <tbody><tr v-for="t in dbStats" :key="t.table_name"><td><strong>{{ t.table_name }}</strong></td><td>{{ fmtNum(t.row_count) }}</td><td>{{ t.size_kb }}</td><td>{{ t.last_update || '-' }}</td></tr></tbody></table></div>
      </div>

      <div class="card" style="margin-top:16px"><div class="card-title">🕐 数据新鲜度</div>
        <div class="table-wrap"><table><thead><tr><th>表名</th><th>类型</th><th>最新记录时间</th><th>状态</th></tr></thead>
        <tbody><tr v-for="f in freshness" :key="f.table_name"><td>{{ f.table_name }}</td><td><span :class="typeTag(f.table_type)">{{ typeLabel(f.table_type) }}</span></td><td>{{ f.latest_record || '-' }}</td><td><span :class="freshTag(f)">{{ freshLabel(f) }}</span></td></tr></tbody></table></div>
      </div>
    </div>

    <!-- Tab 3: 系统配置 -->
    <div v-if="activeTab === 'config' && !tabLoading">
      <div class="card"><div class="card-title">🔧 系统配置参数</div>
        <div class="table-wrap"><table><thead><tr><th>配置键</th><th>当前值</th><th>类型</th><th>分组</th><th>生效范围</th><th>操作</th></tr></thead>
        <tbody><tr v-for="c in configs" :key="c.config_key">
          <td><code>{{ c.config_key }}</code></td>
          <td>
            <span v-if="c._editing">
              <input v-model="c._newVal" class="inline-input" />
            </span>
            <strong v-else>{{ c.config_value }}</strong>
          </td>
          <td><span class="tag tag-blue">{{ c.config_type }}</span></td>
          <td>{{ c.config_group }}</td>
          <td><span :class="scopeTag(c.config_group)">{{ scopeLabel(c.config_group) }}</span></td>
          <td>
            <span v-if="c._editing">
              <button class="btn btn-sm btn-primary" @click="saveConfig(c)" style="margin-right:4px">保存</button>
              <button class="btn btn-sm" @click="c._editing = false">取消</button>
            </span>
            <button v-else class="btn btn-sm" @click="editConfig(c)">编辑</button>
          </td>
        </tr></tbody></table></div>
      </div>
    </div>

    <!-- Tab 4: 操作日志 -->
    <div v-if="activeTab === 'logs' && !tabLoading">
      <div class="card">
        <div class="card-title">📋 操作日志 (共 {{ logTotal }} 条)</div>
        <div class="filter-row">
          <select v-model="logFilter.module" @change="loadLogs(1)" class="form-input" style="width:140px">
            <option value="">全部模块</option>
            <option value="auth">auth</option>
            <option value="dashboard">dashboard</option>
            <option value="analysis">analysis</option>
            <option value="market">market</option>
            <option value="cars">cars</option>
            <option value="recommendation">recommendation</option>
          </select>
          <select v-model="logFilter.type" @change="loadLogs(1)" class="form-input" style="width:140px">
            <option value="">全部类型</option>
            <option value="GET">GET</option>
            <option value="POST">POST</option>
            <option value="PUT">PUT</option>
            <option value="DELETE">DELETE</option>
          </select>
          <span style="font-size:12px;color:var(--text-secondary);margin-left:8px">第 {{ logPage }} 页 / 共 {{ logTotalPages }} 页</span>
          <div style="margin-left:auto">
            <button class="btn btn-sm" :disabled="logPage <= 1" @click="loadLogs(logPage - 1)">上一页</button>
            <button class="btn btn-sm" :disabled="logPage >= logTotalPages" @click="loadLogs(logPage + 1)" style="margin-left:4px">下一页</button>
          </div>
        </div>
        <div class="table-wrap"><table><thead><tr>
          <th>ID</th><th>操作人</th><th>类型</th><th>模块</th><th>描述</th><th>URL</th><th>状态码</th><th>耗时(ms)</th><th>IP</th><th>时间</th><th>详情</th>
        </tr></thead>
        <tbody><tr v-for="l in logs" :key="l.log_id">
          <td>{{ l.log_id }}</td>
          <td>{{ l.operator_name || '-' }}</td>
          <td><span :class="methodTag(l.request_method)">{{ l.request_method }}</span></td>
          <td>{{ l.operation_module }}</td>
          <td style="max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ l.operation_desc || '-' }}</td>
          <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:11px">{{ l.request_url || '-' }}</td>
          <td><span :class="l.response_code == '200' ? 'tag tag-green' : 'tag tag-red'">{{ l.response_code }}</span></td>
          <td>{{ l.execution_time }}</td>
          <td style="font-size:11px">{{ l.ip_address || '-' }}</td>
          <td style="font-size:11px">{{ fmtTime(l.create_time) }}</td>
          <td><button class="btn btn-sm" @click="showLogDetail(l.log_id)">查看</button></td>
        </tr></tbody></table></div>
      </div>

      <!-- Log Detail Modal -->
      <div v-if="logDetail" class="modal-overlay" @click.self="logDetail = null">
        <div class="modal-box" style="max-width:700px">
          <h3>日志详情 #{{ logDetail.log_id }}</h3>
          <div class="detail-grid" style="margin-top:12px">
            <div><strong>操作人:</strong> {{ logDetail.operator_name || '-' }}</div>
            <div><strong>操作类型:</strong> {{ logDetail.operation_type }}</div>
            <div><strong>模块:</strong> {{ logDetail.operation_module }}</div>
            <div><strong>请求方法:</strong> {{ logDetail.request_method }}</div>
            <div><strong>URL:</strong> {{ logDetail.request_url }}</div>
            <div><strong>状态码:</strong> {{ logDetail.response_code }}</div>
            <div><strong>耗时:</strong> {{ logDetail.execution_time }}ms</div>
            <div><strong>IP:</strong> {{ logDetail.ip_address || '-' }}</div>
            <div><strong>时间:</strong> {{ fmtTime(logDetail.create_time) }}</div>
          </div>
          <div style="margin-top:12px"><strong>请求参数:</strong><pre class="code-block">{{ logDetail.request_params || '-' }}</pre></div>
          <div style="margin-top:8px"><strong>响应信息:</strong><pre class="code-block">{{ logDetail.response_msg || '-' }}</pre></div>
          <div style="text-align:right;margin-top:12px"><button class="btn btn-sm" @click="logDetail = null">关闭</button></div>
        </div>
      </div>
    </div>

    <!-- Tab 5: 车辆管理 -->
    <div v-if="activeTab === 'cars' && !tabLoading">
      <div class="card"><div class="card-title">🚙 车辆管理 ({{ cars.length }}辆)
        <input v-model="carSearch" @input="searchCars" placeholder="搜索品牌/车型..." class="form-input" style="width:200px;margin-left:16px;display:inline-block" />
      </div>
        <div class="table-wrap"><table><thead><tr>
          <th>ID</th><th>品牌</th><th>车系</th><th>车型</th><th>类型</th><th>燃料</th><th>价格(万)</th><th>状态</th><th>上市日期</th><th>来源</th><th>操作</th>
        </tr></thead>
        <tbody><tr v-for="c in cars" :key="c.car_id">
          <td>{{ c.car_id }}</td>
          <td><strong>{{ c.brand_name }}</strong></td>
          <td>{{ c.series_name }}</td>
          <td>{{ c.model_name }}</td>
          <td>{{ c.car_type }}</td>
          <td>{{ c.fuel_type }}</td>
          <td>
            <span v-if="c._editingPrice">
              <input v-model.number="c._newPrice" type="number" step="0.1" class="inline-input" style="width:80px" />万
              <button class="btn btn-sm btn-primary" @click="savePrice(c)" style="margin-left:4px">✓</button>
              <button class="btn btn-sm" @click="c._editingPrice = false">✗</button>
            </span>
            <span v-else @dblclick="editPrice(c)" style="cursor:pointer" :title="'双击编辑价格'">{{ c.price }}万</span>
          </td>
          <td><span :class="c.is_on_sale === 1 ? 'tag tag-green' : 'tag tag-red'" style="cursor:pointer" @click="toggleCarSale(c)">{{ c.is_on_sale === 1 ? '在售' : '下架' }}</span></td>
          <td>{{ c.launch_date || '-' }}</td>
          <td><span :class="c.source === 'manual' ? 'tag tag-orange' : 'tag tag-blue'">{{ c.source === 'manual' ? '手动' : '系统' }}</span></td>
          <td>
            <button class="btn btn-sm" @click="toggleCarSale(c)">{{ c.is_on_sale === 1 ? '下架' : '上架' }}</button>
          </td>
        </tr></tbody></table></div>
      </div>

      <div class="card" style="margin-top:16px"><div class="card-title">➕ 新增车辆</div>
        <div class="form-row">
          <span class="autocomplete-wrap">
            <input v-model="newCar.brand_name" placeholder="品牌 *" class="form-input"
                   @focus="brandFocused = true" @blur="brandFocused = false"
                   @keydown.enter.prevent="brandFocused = false" />
            <ul v-if="brandFocused && filteredBrands.length" class="autocomplete-drop">
              <li v-for="b in filteredBrands" :key="b" @mousedown.prevent="newCar.brand_name = b; brandFocused = false">{{ b }}</li>
            </ul>
          </span>
          <input v-model="newCar.series_name" placeholder="车系 *" class="form-input" />
          <input v-model="newCar.model_name" placeholder="车型 *" class="form-input" />
          <span class="autocomplete-wrap">
            <input v-model="newCar.car_type" placeholder="车辆类型" class="form-input"
                   @focus="typeFocused = true" @blur="typeFocused = false" />
            <ul v-if="typeFocused && filteredTypes.length" class="autocomplete-drop">
              <li v-for="t in filteredTypes" :key="t" @mousedown.prevent="newCar.car_type = t; typeFocused = false">{{ t }}</li>
            </ul>
          </span>
          <span class="autocomplete-wrap">
            <input v-model="newCar.fuel_type" placeholder="燃料类型" class="form-input"
                   @focus="fuelFocused = true" @blur="fuelFocused = false" />
            <ul v-if="fuelFocused && filteredFuels.length" class="autocomplete-drop">
              <li v-for="f in filteredFuels" :key="f" @mousedown.prevent="newCar.fuel_type = f; fuelFocused = false">{{ f }}</li>
            </ul>
          </span>
          <input v-model.number="newCar.price" type="number" step="0.1" placeholder="价格(万)" class="form-input" style="width:100px" />
          <button class="btn btn-primary" @click="addNewCar">添加</button>
        </div>
        <div v-if="carAddMsg" :class="carAddOk ? 'success-msg' : 'error-msg'" style="margin-top:8px">{{ carAddMsg }}</div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import api from "../api";

const activeTab = ref("users");
const tabs = [
  { key: "users", label: "👥 用户管理" },
  { key: "monitor", label: "📊 系统监控" },
  { key: "config", label: "🔧 系统配置" },
  { key: "logs", label: "📋 操作日志" },
  { key: "cars", label: "🚙 车辆管理" },
];

const tabLoading = ref(false);
const tabError = ref("");

async function switchTab(key) {
  activeTab.value = key;
  tabError.value = "";
  tabLoading.value = true;
  try {
    if (key === "users") await loadUsers();
    else if (key === "monitor") await loadMonitor();
    else if (key === "config") await loadConfigs();
    else if (key === "logs") await loadLogs(1);
    else if (key === "cars") await loadCars();
  } catch (e) { tabError.value = e.message || "加载失败"; }
  tabLoading.value = false;
}

// ── Users ──
const users = ref([]);
const newUser = ref({ username: "", password: "", nickname: "", role: "user", email: "", phone: "" });
const createMsg = ref("");
const createOk = ref(false);
const resetTarget = ref(null);
const resetPwd = ref("");

async function loadUsers() {
  const r = await api.get("/admin/users");
  users.value = r.data || [];
}

async function createUser() {
  createMsg.value = "";
  if (!newUser.value.username || !newUser.value.password) {
    createMsg.value = "用户名和密码必填"; createOk.value = false; return;
  }
  try {
    const r = await api.post("/admin/users", newUser.value);
    createOk.value = r.code === 200;
    createMsg.value = r.data?.message || "操作完成";
    if (r.code === 200) {
      newUser.value = { username: "", password: "", nickname: "", role: "user", email: "", phone: "" };
      await loadUsers();
    }
  } catch (e) { createMsg.value = e.message; createOk.value = false; }
}

async function changeRole(u, newRole) {
  await api.put(`/admin/users/${u.user_id}/role`, { role: newRole });
  u.role = newRole;
}

async function toggleStatus(u) {
  const newStatus = u.status === 1 ? 0 : 1;
  await api.put(`/admin/users/${u.user_id}/status`, { status: newStatus });
  u.status = newStatus;
}

async function delUser(u) {
  if (!confirm(`确定删除用户 "${u.username}" 吗？此操作不可撤销。`)) return;
  await api.delete(`/admin/users/${u.user_id}`);
  await loadUsers();
}

function showResetPwd(u) {
  resetTarget.value = u;
  resetPwd.value = "";
}

async function doResetPwd() {
  if (!resetPwd.value) return;
  await api.put(`/admin/users/${resetTarget.value.user_id}/password`, { password: resetPwd.value });
  resetTarget.value = null;
  alert("密码已重置");
}

// ── Monitor ──
const dbStats = ref([]);
const freshness = ref([]);
const recSummary = ref([]);

async function loadMonitor() {
  const [r1, r2, r3] = await Promise.all([
    api.get("/admin/db-stats"),
    api.get("/admin/data-freshness"),
    api.get("/admin/rec-pipeline"),
  ]);
  dbStats.value = r1.data || [];
  freshness.value = r2.data || [];
  const s = r3.data?.summary || {};
  recSummary.value = [
    { label: "推荐总数", value: s.total || 0 },
    { label: "已曝光", value: s.exposed || 0 },
    { label: "已点击", value: s.clicked || 0 },
    { label: "已转化", value: s.converted || 0 },
  ];
}

function parseFreshDate(val) {
  if (!val) return null;
  if (/^≈\d/.test(val) || /rows$/.test(val)) return null;
  const d = new Date(val);
  return isNaN(d.getTime()) ? null : d;
}

function typeTag(t) {
  if (t === "realtime") return "tag tag-green";
  if (t === "offline") return "tag tag-blue";
  return "tag tag-orange";
}
function typeLabel(t) {
  if (t === "realtime") return "实时";
  if (t === "offline") return "离线";
  return "统计";
}

function freshTag(f) {
  const t = f.table_type || "realtime";
  if (t === "count_only") return "tag tag-blue";
  const d = parseFreshDate(f.latest_record);
  if (!d) {
    // 无时间戳 → 回退：有记录数显示蓝色，否则红色
    return f.latest_record ? "tag tag-blue" : "tag tag-red";
  }
  const diffH = (Date.now() - d.getTime()) / 3600000;
  // 离线表按天级宽容（24h 内正常，48h 延迟），实时表保持不变
  if (t === "offline") {
    if (diffH < 25) return "tag tag-green";
    if (diffH < 49) return "tag tag-orange";
    return "tag tag-red";
  }
  if (diffH < 1) return "tag tag-green";
  if (diffH < 24) return "tag tag-orange";
  return "tag tag-red";
}

function freshLabel(f) {
  const t = f.table_type || "realtime";
  if (t === "count_only") return "统计";
  const d = parseFreshDate(f.latest_record);
  if (!d) {
    return f.latest_record ? "统计" : "无数据";
  }
  const diffH = (Date.now() - d.getTime()) / 3600000;
  if (t === "offline") {
    if (diffH < 25) return "正常";
    if (diffH < 49) return "延迟";
    return "异常";
  }
  if (diffH < 1) return "正常";
  if (diffH < 24) return "延迟";
  return "异常";
}

// ── Config ──
const configs = ref([]);

async function loadConfigs() {
  const r = await api.get("/admin/config");
  configs.value = (r.data || []).map(c => ({ ...c, _editing: false, _newVal: c.config_value }));
}

function editConfig(c) {
  c._newVal = c.config_value;
  c._editing = true;
}

async function saveConfig(c) {
  await api.put(`/admin/config/${c.config_key}`, { config_value: c._newVal });
  c.config_value = c._newVal;
  c._editing = false;
}

// ── Logs ──
const logs = ref([]);
const logTotal = ref(0);
const logPage = ref(1);
const logPageSize = 20;
const logTotalPages = computed(() => Math.max(1, Math.ceil(logTotal.value / logPageSize)));
const logFilter = ref({ module: "", type: "" });
const logDetail = ref(null);

async function loadLogs(page) {
  logPage.value = page;
  const params = { page, page_size: logPageSize };
  if (logFilter.value.module) params.op_module = logFilter.value.module;
  if (logFilter.value.type) params.op_type = logFilter.value.type;
  const r = await api.get("/admin/operation-logs", params);
  logTotal.value = r.data?.total || 0;
  logs.value = r.data?.rows || [];
}

async function showLogDetail(logId) {
  const r = await api.get(`/admin/operation-logs/${logId}`);
  logDetail.value = r.data;
}

// ── Cars ──
const cars = ref([]);
const carSearch = ref("");
let carSearchTimer = null;

const newCar = ref({ brand_name: "", series_name: "", model_name: "", car_type: "", fuel_type: "", price: null });
const carAddMsg = ref("");
const carAddOk = ref(false);
const brandSuggest = ref([]);
const typeSuggest = ["轿车", "SUV", "MPV", "跑车", "皮卡", "新能源"];
const fuelSuggest = ["纯电", "混动", "增程", "汽油", "柴油", "氢能"];

const brandFocused = ref(false);
const typeFocused = ref(false);
const fuelFocused = ref(false);

const filteredBrands = computed(() => {
  const kw = (newCar.value.brand_name || "").trim().toLowerCase();
  if (!kw) return brandSuggest.value;
  return brandSuggest.value.filter(b => b.toLowerCase().includes(kw));
});
const filteredTypes = computed(() => {
  const kw = (newCar.value.car_type || "").trim().toLowerCase();
  if (!kw) return typeSuggest;
  return typeSuggest.filter(t => t.toLowerCase().includes(kw));
});
const filteredFuels = computed(() => {
  const kw = (newCar.value.fuel_type || "").trim().toLowerCase();
  if (!kw) return fuelSuggest;
  return fuelSuggest.filter(f => f.toLowerCase().includes(kw));
});

async function loadCars() {
  const params = carSearch.value ? { search: carSearch.value } : {};
  const r = await api.get("/admin/cars", params);
  cars.value = (r.data || []).map(c => ({ ...c, _editingPrice: false, _newPrice: c.price }));
  // Collect brand suggestions from car list
  const brands = [...new Set((r.data || []).map(c => c.brand_name).filter(Boolean))];
  brandSuggest.value = brands.sort();
}

function searchCars() {
  clearTimeout(carSearchTimer);
  carSearchTimer = setTimeout(loadCars, 300);
}

async function addNewCar() {
  carAddMsg.value = "";
  const nc = newCar.value;
  if (!nc.brand_name || !nc.series_name || !nc.model_name || !nc.car_type || !nc.fuel_type || !nc.price) {
    carAddMsg.value = "请填写所有字段";
    carAddOk.value = false;
    return;
  }
  try {
    const r = await api.post("/admin/cars", nc);
    carAddOk.value = r.code === 200;
    carAddMsg.value = r.data?.message || "操作完成";
    if (r.code === 200) {
      newCar.value = { brand_name: "", series_name: "", model_name: "", car_type: "", fuel_type: "", price: null };
      await loadCars();
    }
  } catch (e) { carAddMsg.value = e.message; carAddOk.value = false; }
}

async function toggleCarSale(c) {
  const r = await api.put(`/admin/cars/${c.car_id}/toggle-sale`);
  c.is_on_sale = r.data?.is_on_sale;
}

function editPrice(c) {
  c._newPrice = c.price;
  c._editingPrice = true;
}

async function savePrice(c) {
  await api.put(`/admin/cars/${c.car_id}/price`, { price: c._newPrice });
  c.price = c._newPrice;
  c._editingPrice = false;
}

// ── Helpers ──
function scopeTag(group) {
  if (group === "recommend" || group === "cache") return "tag tag-green";
  return "tag tag-orange";
}
function scopeLabel(group) {
  if (group === "recommend" || group === "cache") return "后端即时生效";
  if (group === "streaming") return "Spark Streaming";
  return "Spark 离线任务";
}
function fmtNum(n) { return n ? Number(n).toLocaleString() : "0"; }
function fmtTime(t) {
  if (!t) return "-";
  return String(t).slice(0, 19).replace("T", " ");
}
function methodTag(m) {
  if (m === "GET") return "tag tag-blue";
  if (m === "POST") return "tag tag-green";
  if (m === "PUT") return "tag tag-orange";
  if (m === "DELETE") return "tag tag-red";
  return "tag";
}

// Init
onMounted(() => switchTab("users"));
onUnmounted(() => { if (carSearchTimer) clearTimeout(carSearchTimer); });
</script>

<style scoped>
.admin-tabs {
  display: flex; gap: 2px; margin-bottom: 20px;
  background: var(--bg-card, #111827); border-radius: 8px; padding: 4px;
}
.tab-btn {
  flex: 1; padding: 10px 16px; border: none; border-radius: 6px;
  background: transparent; color: var(--text-secondary, #94a3b8);
  font-size: 14px; cursor: pointer; transition: all .2s;
}
.tab-btn:hover { color: var(--text-primary, #e2e8f0); background: rgba(255,255,255,0.05); }
.tab-btn.active { background: var(--primary, #3b82f6); color: #fff; font-weight: 600; }

.form-row { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
.form-input { padding: 6px 10px; border: 1px solid var(--border, #334155); border-radius: 6px; background: var(--bg-input, #1e293b); color: var(--text-primary, #e2e8f0); font-size: 13px; }
.inline-select { padding: 2px 6px; border: 1px solid var(--border, #334155); border-radius: 4px; background: var(--bg-input, #1e293b); color: var(--text-primary, #e2e8f0); font-size: 12px; }
.inline-input { padding: 2px 6px; border: 1px solid var(--primary, #3b82f6); border-radius: 4px; background: var(--bg-input, #1e293b); color: var(--text-primary, #e2e8f0); font-size: 12px; width: 120px; }

.filter-row { display: flex; gap: 8px; align-items: center; margin-bottom: 12px; flex-wrap: wrap; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-box { background: var(--bg-card, #1a2332); border: 1px solid var(--border, #334155); border-radius: 12px; padding: 24px; min-width: 380px; max-width: 90vw; max-height: 80vh; overflow-y: auto; }
.modal-box h3 { margin: 0 0 4px; font-size: 16px; }

.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; font-size: 13px; }
.code-block { background: #0d1117; color: #c9d1d9; padding: 10px; border-radius: 6px; font-size: 12px; max-height: 200px; overflow: auto; white-space: pre-wrap; word-break: break-all; }

.success-msg { color: #10b981; font-size: 13px; }
.error-msg { color: #ef4444; font-size: 13px; }

.btn-sm { padding: 4px 10px; font-size: 12px; }
.btn-primary { background: var(--primary, #3b82f6); color: #fff; border: none; border-radius: 6px; padding: 8px 16px; cursor: pointer; font-size: 13px; }
.btn-primary:hover { opacity: 0.85; }
.btn-danger { background: #ef4444; color: #fff; border: none; border-radius: 6px; padding: 8px 16px; cursor: pointer; font-size: 13px; }
.btn-danger:hover { opacity: 0.85; }
.btn { background: var(--bg-input, #1e293b); color: var(--text-primary, #e2e8f0); border: 1px solid var(--border, #334155); border-radius: 6px; padding: 8px 16px; cursor: pointer; font-size: 13px; }
.btn:hover { opacity: 0.85; }
.btn:disabled { opacity: 0.4; cursor: not-allowed; }

.autocomplete-wrap { position: relative; display: inline-block; }
.autocomplete-wrap .form-input { width: 130px; }
.autocomplete-drop {
  position: absolute; top: 100%; left: 0; right: 0;
  margin: 2px 0 0 0; padding: 0;
  background: var(--bg-card, #1a2332);
  border: 1px solid var(--border, #334155);
  border-radius: 6px;
  list-style: none; z-index: 100;
  max-height: 160px; overflow-y: auto;
}
.autocomplete-drop li {
  padding: 6px 10px; font-size: 13px;
  color: var(--text-primary, #e2e8f0);
  cursor: pointer;
}
.autocomplete-drop li:hover { background: rgba(59,130,246,0.2); }
</style>
