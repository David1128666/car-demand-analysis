<template>
  <div>
    <h1 class="page-title">{{ t("admin.title") }}</h1>

    <div class="admin-tabs">
      <button v-for="t in tabs" :key="t.key" :class="['tab-btn', { active: activeTab === t.key }]" @click="switchTab(t.key)">{{ t.label }}</button>
    </div>

    <div v-if="tabLoading" class="loading">{{ t("common.loading") }}</div>
    <div v-if="tabError" class="error-msg">❌ {{ tabError }}</div>

    <!-- Tab 1: 用户管理 -->
    <div v-if="activeTab === 'users' && !tabLoading">
      <div class="card"><div class="card-title">{{ t("admin.users.title", { count: users.length }) }}</div>
        <div class="table-wrap"><table><thead><tr>
          <th>{{ t("admin.users.id") }}</th><th>{{ t("admin.users.username") }}</th><th>{{ t("admin.users.nickname") }}</th><th>{{ t("admin.users.role") }}</th><th>{{ t("admin.users.status") }}</th><th>{{ t("admin.users.email") }}</th><th>{{ t("admin.users.phone") }}</th><th>{{ t("admin.users.lastLogin") }}</th><th>{{ t("admin.users.actions") }}</th>
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
          <td><span :class="u.status === 1 ? 'tag tag-green' : 'tag tag-red'" style="cursor:pointer" @click="toggleStatus(u)">{{ u.status === 1 ? t("admin.users.active") : t("admin.users.disabled") }}</span></td>
          <td>{{ u.email || '-' }}</td>
          <td>{{ u.phone || '-' }}</td>
          <td>{{ fmtTime(u.last_login) }}</td>
          <td>
            <button class="btn btn-sm btn-primary" @click="showResetPwd(u)" style="margin-right:4px">{{ t("admin.users.resetPassword") }}</button>
            <button class="btn btn-sm btn-danger" @click="delUser(u)">{{ t("admin.users.delete") }}</button>
          </td>
        </tr></tbody></table></div>
      </div>

      <div class="card" style="margin-top:16px"><div class="card-title">{{ t("admin.users.createTitle") }}</div>
        <div class="form-row">
          <input v-model="newUser.username" :placeholder="t('admin.users.usernamePlaceholder')" class="form-input" />
          <input v-model="newUser.password" :placeholder="t('admin.users.passwordPlaceholder')" type="password" class="form-input" />
          <input v-model="newUser.nickname" :placeholder="t('admin.users.nicknamePlaceholder')" class="form-input" />
          <select v-model="newUser.role" class="form-input"><option value="user">user</option><option value="admin">admin</option></select>
          <input v-model="newUser.email" :placeholder="t('admin.users.emailPlaceholder')" class="form-input" />
          <input v-model="newUser.phone" :placeholder="t('admin.users.phonePlaceholder')" class="form-input" />
          <button class="btn btn-primary" @click="createUser">{{ t("admin.users.create") }}</button>
        </div>
        <div v-if="createMsg" :class="createOk ? 'success-msg' : 'error-msg'" style="margin-top:8px">{{ createMsg }}</div>
      </div>

      <!-- Reset Password Modal -->
      <div v-if="resetTarget" class="modal-overlay" @click.self="resetTarget = null">
        <div class="modal-box">
          <h3>{{ t("admin.users.resetTitle", { username: resetTarget.username }) }}</h3>
          <input v-model="resetPwd" type="text" :placeholder="t('admin.users.newPassword')" class="form-input" style="width:100%;margin:12px 0" />
          <div style="text-align:right"><button class="btn btn-sm" @click="resetTarget = null" style="margin-right:8px">{{ t("common.cancel") }}</button><button class="btn btn-sm btn-primary" @click="doResetPwd">{{ t("admin.users.confirmReset") }}</button></div>
        </div>
      </div>
    </div>

    <!-- Tab 2: 系统监控 -->
    <div v-if="activeTab === 'monitor' && !tabLoading">
      <div class="stat-grid">
        <div class="stat-card" v-for="s in recSummary" :key="s.label"><div class="label">{{ s.label }}</div><div class="value">{{ s.value }}</div></div>
      </div>

      <div class="card" style="margin-top:16px"><div class="card-title">{{ t("admin.monitor.dbStats") }}</div>
        <div class="table-wrap"><table><thead><tr><th>{{ t("admin.monitor.tableName") }}</th><th>{{ t("admin.monitor.rows") }}</th><th>{{ t("admin.monitor.sizeKb") }}</th><th>{{ t("admin.monitor.lastUpdate") }}</th></tr></thead>
        <tbody><tr v-for="t in dbStats" :key="t.table_name"><td><strong>{{ t.table_name }}</strong></td><td>{{ fmtNum(t.row_count) }}</td><td>{{ t.size_kb }}</td><td>{{ t.last_update || '-' }}</td></tr></tbody></table></div>
      </div>

      <div class="card" style="margin-top:16px"><div class="card-title">{{ t("admin.monitor.freshness") }}</div>
        <div class="table-wrap"><table><thead><tr><th>{{ t("admin.monitor.tableName") }}</th><th>{{ t("admin.monitor.tableType") }}</th><th>{{ t("admin.monitor.latestRecord") }}</th><th>{{ t("admin.monitor.status") }}</th></tr></thead>
        <tbody><tr v-for="f in freshness" :key="f.table_name"><td>{{ f.table_name }}</td><td><span :class="typeTag(f.table_type)">{{ typeLabel(f.table_type) }}</span></td><td>{{ f.latest_record || '-' }}</td><td><span :class="freshTag(f)">{{ freshLabel(f) }}</span></td></tr></tbody></table></div>
      </div>
    </div>

    <!-- Tab 3: 系统配置 -->
    <div v-if="activeTab === 'config' && !tabLoading">
      <div class="card"><div class="card-title">{{ t("admin.config.title") }}</div>
        <div class="table-wrap"><table><thead><tr><th>{{ t("admin.config.key") }}</th><th>{{ t("admin.config.value") }}</th><th>{{ t("admin.config.type") }}</th><th>{{ t("admin.config.group") }}</th><th>{{ t("admin.config.scope") }}</th><th>{{ t("admin.config.actions") }}</th></tr></thead>
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
              <button class="btn btn-sm btn-primary" @click="saveConfig(c)" style="margin-right:4px">{{ t("common.save") }}</button>
              <button class="btn btn-sm" @click="c._editing = false">{{ t("common.cancel") }}</button>
            </span>
            <button v-else class="btn btn-sm" @click="editConfig(c)">{{ t("common.edit") }}</button>
          </td>
        </tr></tbody></table></div>
      </div>
    </div>

    <!-- Tab 4: 操作日志 -->
    <div v-if="activeTab === 'logs' && !tabLoading">
      <div class="card">
        <div class="card-title">{{ t("admin.logs.title", { count: logTotal }) }}</div>
        <div class="filter-row">
          <select v-model="logFilter.module" @change="loadLogs(1)" class="form-input" style="width:140px">
            <option value="">{{ t("admin.logs.allModules") }}</option>
            <option value="auth">auth</option>
            <option value="dashboard">dashboard</option>
            <option value="analysis">analysis</option>
            <option value="market">market</option>
            <option value="cars">cars</option>
            <option value="recommendation">recommendation</option>
          </select>
          <select v-model="logFilter.type" @change="loadLogs(1)" class="form-input" style="width:140px">
            <option value="">{{ t("admin.logs.allTypes") }}</option>
            <option value="GET">GET</option>
            <option value="POST">POST</option>
            <option value="PUT">PUT</option>
            <option value="DELETE">DELETE</option>
          </select>
          <span style="font-size:12px;color:var(--text-secondary);margin-left:8px">{{ t("admin.logs.page", { page: logPage, total: logTotalPages }) }}</span>
          <div style="margin-left:auto">
            <button class="btn btn-sm" :disabled="logPage <= 1" @click="loadLogs(logPage - 1)">{{ t("common.previous") }}</button>
            <button class="btn btn-sm" :disabled="logPage >= logTotalPages" @click="loadLogs(logPage + 1)" style="margin-left:4px">{{ t("common.next") }}</button>
          </div>
        </div>
        <div class="table-wrap"><table><thead><tr>
          <th>{{ t("admin.logs.id") }}</th><th>{{ t("admin.logs.operator") }}</th><th>{{ t("admin.logs.method") }}</th><th>{{ t("admin.logs.module") }}</th><th>{{ t("admin.logs.description") }}</th><th>URL</th><th>{{ t("admin.logs.statusCode") }}</th><th>{{ t("admin.logs.elapsed") }}</th><th>{{ t("admin.logs.ip") }}</th><th>{{ t("admin.logs.time") }}</th><th>{{ t("admin.logs.details") }}</th>
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
          <td><button class="btn btn-sm" @click="showLogDetail(l.log_id)">{{ t("common.view") }}</button></td>
        </tr></tbody></table></div>
      </div>

      <!-- Log Detail Modal -->
      <div v-if="logDetail" class="modal-overlay" @click.self="logDetail = null">
        <div class="modal-box" style="max-width:700px">
          <h3>{{ t("admin.logs.detailTitle", { id: logDetail.log_id }) }}</h3>
          <div class="detail-grid" style="margin-top:12px">
            <div><strong>{{ t("admin.logs.operator") }}:</strong> {{ logDetail.operator_name || '-' }}</div>
            <div><strong>{{ t("admin.logs.operationType") }}:</strong> {{ logDetail.operation_type }}</div>
            <div><strong>{{ t("admin.logs.module") }}:</strong> {{ logDetail.operation_module }}</div>
            <div><strong>{{ t("admin.logs.requestMethod") }}:</strong> {{ logDetail.request_method }}</div>
            <div><strong>URL:</strong> {{ logDetail.request_url }}</div>
            <div><strong>{{ t("admin.logs.statusCode") }}:</strong> {{ logDetail.response_code }}</div>
            <div><strong>{{ t("admin.logs.elapsed") }}:</strong> {{ logDetail.execution_time }}ms</div>
            <div><strong>IP:</strong> {{ logDetail.ip_address || '-' }}</div>
            <div><strong>{{ t("admin.logs.time") }}:</strong> {{ fmtTime(logDetail.create_time) }}</div>
          </div>
          <div style="margin-top:12px"><strong>{{ t("admin.logs.requestParams") }}:</strong><pre class="code-block">{{ logDetail.request_params || '-' }}</pre></div>
          <div style="margin-top:8px"><strong>{{ t("admin.logs.response") }}:</strong><pre class="code-block">{{ logDetail.response_msg || '-' }}</pre></div>
          <div style="text-align:right;margin-top:12px"><button class="btn btn-sm" @click="logDetail = null">{{ t("common.close") }}</button></div>
        </div>
      </div>
    </div>

    <!-- Tab 5: 车辆管理 -->
    <div v-if="activeTab === 'cars' && !tabLoading">
      <div class="card"><div class="card-title">{{ t("admin.cars.title", { count: cars.length }) }}
        <input v-model="carSearch" @input="searchCars" :placeholder="t('admin.cars.searchPlaceholder')" class="form-input" style="width:200px;margin-left:16px;display:inline-block" />
      </div>
        <div class="table-wrap"><table><thead><tr>
          <th>{{ t("admin.cars.id") }}</th><th>{{ t("admin.cars.brand") }}</th><th>{{ t("admin.cars.series") }}</th><th>{{ t("admin.cars.model") }}</th><th>{{ t("admin.cars.type") }}</th><th>{{ t("admin.cars.fuel") }}</th><th>{{ t("admin.cars.price") }}</th><th>{{ t("admin.cars.status") }}</th><th>{{ t("admin.cars.launchDate") }}</th><th>{{ t("admin.cars.source") }}</th><th>{{ t("admin.cars.actions") }}</th>
        </tr></thead>
        <tbody><tr v-for="c in cars" :key="c.car_id">
          <td>{{ c.car_id }}</td>
          <td><strong>{{ c.brand_name }}</strong></td>
          <td>{{ c.series_name }}</td>
          <td>{{ c.model_name }}</td>
          <td>{{ valueLabel(c.car_type) }}</td>
          <td>{{ valueLabel(c.fuel_type) }}</td>
          <td>
            <span v-if="c._editingPrice">
              <input v-model.number="c._newPrice" type="number" step="0.1" class="inline-input" style="width:80px" />{{ t("common.unitWan") }}
              <button class="btn btn-sm btn-primary" @click="savePrice(c)" style="margin-left:4px">✓</button>
              <button class="btn btn-sm" @click="c._editingPrice = false">✗</button>
            </span>
            <span v-else @dblclick="editPrice(c)" style="cursor:pointer" :title="t('admin.cars.doubleClickPrice')">{{ c.price }}{{ t("common.unitWan") }}</span>
          </td>
          <td><span :class="c.is_on_sale === 1 ? 'tag tag-green' : 'tag tag-red'" style="cursor:pointer" @click="toggleCarSale(c)">{{ c.is_on_sale === 1 ? t("admin.cars.onSale") : t("admin.cars.offSale") }}</span></td>
          <td>{{ c.launch_date || '-' }}</td>
          <td><span :class="c.source === 'manual' ? 'tag tag-orange' : 'tag tag-blue'">{{ c.source === 'manual' ? t("admin.cars.manual") : t("admin.cars.system") }}</span></td>
          <td>
            <button class="btn btn-sm" @click="toggleCarSale(c)">{{ c.is_on_sale === 1 ? t("admin.cars.unlist") : t("admin.cars.list") }}</button>
          </td>
        </tr></tbody></table></div>
      </div>

      <div class="card" style="margin-top:16px"><div class="card-title">{{ t("admin.cars.createTitle") }}</div>
        <div class="form-row">
          <span class="autocomplete-wrap">
            <input v-model="newCar.brand_name" :placeholder="t('admin.cars.brandPlaceholder')" class="form-input"
                   @focus="brandFocused = true" @blur="brandFocused = false"
                   @keydown.enter.prevent="brandFocused = false" />
            <ul v-if="brandFocused && filteredBrands.length" class="autocomplete-drop">
              <li v-for="b in filteredBrands" :key="b" @mousedown.prevent="newCar.brand_name = b; brandFocused = false">{{ b }}</li>
            </ul>
          </span>
          <input v-model="newCar.series_name" :placeholder="t('admin.cars.seriesPlaceholder')" class="form-input" />
          <input v-model="newCar.model_name" :placeholder="t('admin.cars.modelPlaceholder')" class="form-input" />
          <span class="autocomplete-wrap">
            <input v-model="newCar.car_type" :placeholder="t('admin.cars.typePlaceholder')" class="form-input"
                   @focus="typeFocused = true" @blur="typeFocused = false" />
            <ul v-if="typeFocused && filteredTypes.length" class="autocomplete-drop">
              <li v-for="item in filteredTypes" :key="item" @mousedown.prevent="newCar.car_type = item; typeFocused = false">{{ valueLabel(item) }}</li>
            </ul>
          </span>
          <span class="autocomplete-wrap">
            <input v-model="newCar.fuel_type" :placeholder="t('admin.cars.fuelPlaceholder')" class="form-input"
                   @focus="fuelFocused = true" @blur="fuelFocused = false" />
            <ul v-if="fuelFocused && filteredFuels.length" class="autocomplete-drop">
              <li v-for="item in filteredFuels" :key="item" @mousedown.prevent="newCar.fuel_type = item; fuelFocused = false">{{ valueLabel(item) }}</li>
            </ul>
          </span>
          <input v-model.number="newCar.price" type="number" step="0.1" :placeholder="t('admin.cars.pricePlaceholder')" class="form-input" style="width:100px" />
          <button class="btn btn-primary" @click="addNewCar">{{ t("admin.cars.add") }}</button>
        </div>
        <div v-if="carAddMsg" :class="carAddOk ? 'success-msg' : 'error-msg'" style="margin-top:8px">{{ carAddMsg }}</div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import api from "../api";
import { apiMessage, t, valueLabel } from "../i18n";

const activeTab = ref("users");
const tabs = computed(() => [
  { key: "users", label: t("admin.tab.users") },
  { key: "monitor", label: t("admin.tab.monitor") },
  { key: "config", label: t("admin.tab.config") },
  { key: "logs", label: t("admin.tab.logs") },
  { key: "cars", label: t("admin.tab.cars") },
]);

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
  } catch (e) { tabError.value = apiMessage(e.message, "admin.loadFailed"); }
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
    createMsg.value = t("admin.users.required"); createOk.value = false; return;
  }
  try {
    const r = await api.post("/admin/users", newUser.value);
    createOk.value = r.code === 200;
    createMsg.value = apiMessage(r.data?.message, "admin.cars.operationDone");
    if (r.code === 200) {
      newUser.value = { username: "", password: "", nickname: "", role: "user", email: "", phone: "" };
      await loadUsers();
    }
  } catch (e) { createMsg.value = apiMessage(e.message); createOk.value = false; }
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
  if (!confirm(t("admin.users.deleteConfirm", { username: u.username }))) return;
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
  alert(t("admin.users.resetSuccess"));
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
    { label: t("admin.monitor.recommendations"), value: s.total || 0 },
    { label: t("admin.monitor.exposed"), value: s.exposed || 0 },
    { label: t("admin.monitor.clicked"), value: s.clicked || 0 },
    { label: t("admin.monitor.converted"), value: s.converted || 0 },
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
function typeLabel(type) {
  if (type === "realtime") return t("enum.tableType.realtime");
  if (type === "offline") return t("enum.tableType.offline");
  return t("enum.tableType.stats");
}

function freshTag(f) {
  const tableType = f.table_type || "realtime";
  if (tableType === "count_only") return "tag tag-blue";
  const d = parseFreshDate(f.latest_record);
  if (!d) {
    // 无时间戳 → 回退：有记录数显示蓝色，否则红色
    return f.latest_record ? "tag tag-blue" : "tag tag-red";
  }
  const diffH = (Date.now() - d.getTime()) / 3600000;
  // 离线表按天级宽容（24h 内正常，48h 延迟），实时表保持不变
  if (tableType === "offline") {
    if (diffH < 25) return "tag tag-green";
    if (diffH < 49) return "tag tag-orange";
    return "tag tag-red";
  }
  if (diffH < 1) return "tag tag-green";
  if (diffH < 24) return "tag tag-orange";
  return "tag tag-red";
}

function freshLabel(f) {
  const tableType = f.table_type || "realtime";
  if (tableType === "count_only") return t("enum.tableType.stats");
  const d = parseFreshDate(f.latest_record);
  if (!d) {
    return f.latest_record
      ? t("enum.tableType.stats")
      : t("enum.freshness.noData");
  }
  const diffH = (Date.now() - d.getTime()) / 3600000;
  if (tableType === "offline") {
    if (diffH < 25) return t("enum.freshness.normal");
    if (diffH < 49) return t("enum.freshness.delayed");
    return t("enum.freshness.error");
  }
  if (diffH < 1) return t("enum.freshness.normal");
  if (diffH < 24) return t("enum.freshness.delayed");
  return t("enum.freshness.error");
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
    carAddMsg.value = t("admin.cars.required");
    carAddOk.value = false;
    return;
  }
  try {
    const r = await api.post("/admin/cars", nc);
    carAddOk.value = r.code === 200;
    carAddMsg.value = apiMessage(r.data?.message, "admin.cars.operationDone");
    if (r.code === 200) {
      newCar.value = { brand_name: "", series_name: "", model_name: "", car_type: "", fuel_type: "", price: null };
      await loadCars();
    }
  } catch (e) { carAddMsg.value = apiMessage(e.message); carAddOk.value = false; }
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
  if (group === "recommend" || group === "cache") {
    return t("admin.config.backend");
  }
  if (group === "streaming") return "Spark Streaming";
  return t("admin.config.offline");
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
