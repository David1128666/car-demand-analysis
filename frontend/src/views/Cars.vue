<template>
  <div>
    <h1 class="page-title">🚙 车型查询</h1>
    <div class="filter-bar">
      <select v-model="f.brand_id"><option value="">全部品牌</option><option v-for="b in brandList" :key="b.brand_id" :value="b.brand_id">{{ b.brand_name }}</option></select>
      <select v-model="f.car_type"><option value="">全部车型</option><option>轿车</option><option>SUV</option><option>MPV</option></select>
      <select v-model="f.fuel_type"><option value="">全部燃料</option><option>汽油</option><option>纯电动</option><option>混合动力</option><option>插电混动</option></select>
      <button class="btn btn-primary btn-sm" @click="search(1)">筛选</button>
      <button class="btn btn-secondary btn-sm" @click="resetFilters">重置</button>
    </div>
    <div v-if="loading" class="loading">⏳ 加载中...</div>
    <div v-else>
      <div class="table-wrap card"><table><thead><tr><th>品牌</th><th>车系</th><th>车型</th><th>类型</th><th>燃料</th><th>价格</th><th>操作</th></tr></thead>
      <tbody><tr v-for="c in list" :key="c.car_id"><td>{{ c.brand_name }}</td><td>{{ c.series_name }}</td><td>{{ c.model_name }}</td><td><span class="tag tag-blue">{{ c.car_type }}</span></td><td><span class="tag tag-green">{{ c.fuel_type }}</span></td><td>{{ c.price }}万</td><td><button class="btn btn-sm btn-primary" @click="$router.push('/cars/'+c.car_id)">详情</button></td></tr></tbody></table></div>
      <div class="pagination"><button :disabled="page<=1" @click="search(page-1)">上一页</button><button class="active">{{ page }}</button><button @click="search(page+1)">下一页</button></div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import api from "../api";
const list = ref([]); const brandList = ref([]); const page = ref(1); const loading = ref(true);
const f = reactive({ brand_id: "", car_type: "", fuel_type: "" });

function resetFilters() {
  f.brand_id = "";
  f.car_type = "";
  f.fuel_type = "";
  search(1);
}

async function search(p=1) {
  page.value = p; loading.value = true;
  const params = { page: p, size: 10 };
  if (f.brand_id !== "" && f.brand_id != null) params.brand_id = f.brand_id;
  if (f.car_type !== "" && f.car_type != null) params.car_type = f.car_type;
  if (f.fuel_type !== "" && f.fuel_type != null) params.fuel_type = f.fuel_type;
  try { const r = await api.get("/cars", params); list.value = r.data?.list || []; } catch (e) { console.error(e); }
  loading.value = false;
}

onMounted(async () => {
  try { const r = await api.get("/cars/meta/brands"); brandList.value = r.data || []; } catch (e) { console.error(e); }
  search();
});
</script>