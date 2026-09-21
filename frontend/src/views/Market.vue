<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">市场洞察</h1>
      <span class="refresh-badge">刷新 {{ countdown }}s</span>
    </div>
    <div v-if="loading" class="loading">正在拉取市场数据...</div>

    <div v-if="ok">
      <div class="chart-row">
        <div class="card chart-box">
          <div class="card-title">品牌偏好排行 Top5</div>
          <div id="mc1" style="height:300px"></div>
        </div>
        <div class="card chart-box">
          <div class="card-title">品牌市占率变化</div>
          <div class="brand-filters">
            <button v-for="b in brandList" :key="b" :class="['btn btn-xs', selectedBrand === b ? 'btn-primary' : 'btn-secondary']" @click="selectBrand(b)">{{ b }}</button>
          </div>
          <div id="mc2" style="height:300px"></div>
        </div>
      </div>

      <div class="chart-row">
        <div class="card chart-box">
          <div class="card-title">热门搜索关键词 Top15</div>
          <div id="mc3" style="height:280px"></div>
        </div>
        <div class="card chart-box">
          <div class="card-title">燃油类型趋势</div>
          <div id="mc4" style="height:280px"></div>
        </div>
      </div>

      <div class="chart-row">
        <div class="card chart-box">
          <div class="card-title">价格变动原因统计</div>
          <div id="mc5" style="height:280px"></div>
        </div>
        <div class="card chart-box">
          <div class="card-title">价格战监测</div>
          <div id="mc6" style="height:280px"></div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">新车关注度排行</div>
        <div class="table-wrap"><table><thead><tr>
          <th>排名</th><th>品牌</th><th>车系</th><th>车型</th>
          <th>类型</th><th>燃油</th><th>价格(万)</th><th>热度分</th>
          <th>浏览量</th><th>访客数</th><th>收藏</th><th>咨询</th>
        </tr></thead><tbody>
          <tr v-for="(r,i) in trending" :key="r.car_id">
            <td><span class="tag tag-blue">{{ i + 1 }}</span></td>
            <td><strong>{{ r.brand_name }}</strong></td>
            <td>{{ r.series_name }}</td><td>{{ r.model_name }}</td>
            <td>{{ r.car_type }}</td><td>{{ r.fuel_type }}</td>
            <td>{{ r.price }}</td>
            <td><span :class="r.hot_score >= 80 ? 'tag tag-orange' : 'tag tag-green'">{{ r.hot_score }}</span></td>
            <td>{{ r.total_pv }}</td><td>{{ r.total_uv }}</td>
            <td>{{ r.total_collect }}</td><td>{{ r.total_consult }}</td>
          </tr>
        </tbody></table></div>
      </div>

      <div class="chart-row">
        <div class="card chart-box">
          <div class="card-title">优惠活动效果 Top10</div>
          <div id="mc7" style="height:280px"></div>
        </div>
        <div class="card chart-box">
          <div class="card-title">品牌收藏率排行</div>
          <div id="mc8" style="height:280px"></div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">价格折扣分层</div>
        <div class="table-wrap"><table><thead><tr>
          <th>折扣档位</th><th>报价数</th><th>平均折扣%</th><th>涉及品牌</th>
        </tr></thead><tbody>
          <tr v-for="r in discountTiers" :key="r.discount_range">
            <td><span :class="r.avg_discount_pct >= 15 ? 'tag tag-orange' : 'tag tag-green'">{{ r.discount_range }}</span></td>
            <td>{{ r.quote_count }}</td><td>{{ r.avg_discount_pct }}</td><td>{{ r.brand_count }}</td>
          </tr>
        </tbody></table></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from "vue";
import api from "../api";

const keywords = ref([]);
const brandCollect = ref([]);
const discountTiers = ref([]);
const promotionEffect = ref([]);
const priceWar = ref([]);
const priceReasons = ref([]);
const fuelTrend = ref([]);
const trending = ref([]);
const countdown = ref(7);
const loading = ref(true);
const ok = ref(false);

const ALERT_COLORS = { high: "#ef4444", medium: "#f59e0b", normal: "#10b981" };
const brandRank = ref([]);
const marketShare = ref([]);
const selectedBrand = ref("");
const brandList = ref([]);

let _timer = null;
let _cdTimer = null;

async function fetchData() {
  const safeGet = (url, params) => api.get(url, params).then(r => r.data).catch(() => null);
  const msParams = selectedBrand.value ? { brand_name: selectedBrand.value } : undefined;

  const [d1,d2,d3,d4,d5,d6,d7,d8,d9,d10] = await Promise.all([
    safeGet("/market/brand-rank"), safeGet("/market/realtime-market-share", msParams),
    safeGet("/market/keyword-cloud"), safeGet("/market/price-war"),
    safeGet("/market/price-reasons"), safeGet("/market/fuel-trend"),
    safeGet("/market/new-trending"),
    safeGet("/market/brand-collect-rate"), safeGet("/market/promotion-effect"),
    safeGet("/market/discount-tiers"),
  ]);
  brandRank.value = d1 || []; marketShare.value = d2 || [];
  keywords.value = d3 || []; priceWar.value = d4 || [];
  priceReasons.value = d5 || []; fuelTrend.value = d6 || [];
  trending.value = d7 || [];
  brandCollect.value = d8 || []; promotionEffect.value = d9 || [];
  discountTiers.value = d10 || [];

  if (!selectedBrand.value && marketShare.value.length) {
    const seen = new Set();
    brandList.value = marketShare.value
      .map(r => r.brand_name)
      .filter(b => b && !seen.has(b) && seen.add(b));
    if (brandList.value.length) {
      selectedBrand.value = brandList.value[0];
      fetchData();  // 跳过"全部",直接用第一个品牌重新拉
      return;
    }
  }

  ok.value = true;
  loading.value = false;
  await nextTick();
  setTimeout(function(){drawAllCharts();},100);
}

function selectBrand(brand) {
  selectedBrand.value = brand;
  fetchData();
}

onMounted(() => {
  fetchData();
  _cdTimer = setInterval(() => { countdown.value = countdown.value <= 1 ? 7 : countdown.value - 1; }, 1000);
  _timer = setInterval(fetchData, 7000);
});

onUnmounted(() => {
  if (_timer) clearInterval(_timer);
  if (_cdTimer) clearInterval(_cdTimer);
});

var _brandCharts = []; // mc1, mc2, mc6, mc8 instances for cross-linking

function brandHighlight(brandName) {
  _brandCharts.forEach(function(c) {
    if (!c || c.isDisposed()) return;
    c.dispatchAction({ type: "downplay" });
    try {
      var opt = c.getOption();
      // category xAxis bars (mc1, mc8)
      if (opt.xAxis && opt.xAxis[0] && Array.isArray(opt.xAxis[0].data)) {
        var xi = opt.xAxis[0].data.indexOf(brandName);
        if (xi >= 0) (opt.series||[]).forEach(function(_,si){ c.dispatchAction({type:"highlight",seriesIndex:si,dataIndex:xi}); });
      }
      // line chart where series name = brand (mc2)
      (opt.series||[]).forEach(function(s,si){ if(s.name===brandName) c.dispatchAction({type:"highlight",seriesIndex:si}); });
      // horizontal yAxis bars (mc6)
      if (opt.yAxis && opt.yAxis[0] && Array.isArray(opt.yAxis[0].data)) {
        opt.yAxis[0].data.forEach(function(d,di){ if(String(d).indexOf(brandName)===0) c.dispatchAction({type:"highlight",seriesIndex:0,dataIndex:di}); });
      }
    } catch(e){}
  });
}

function drawAllCharts(){
  var ec=window.echarts; if(!ec) return;
  _brandCharts = [];
  drawBrandRank(ec);drawMarketShare(ec);drawKeywordBar(ec);
  drawFuelTrend(ec);drawPriceReasons(ec);drawPriceWar(ec);
  drawPromotionEffect(ec);drawBrandCollectChart(ec);
  // group: connect tooltips across brand charts
  _brandCharts.forEach(function(c){ if(c&&!c.isDisposed()) c.group = "market-brand"; });
}

function drawBrandRank(ec){
  var el=document.getElementById("mc1"); if(!el||!brandRank.value.length)return;
  ec.dispose(el);var c=ec.init(el); var names=[],seen={};
  brandRank.value.forEach(function(r){if(!seen[r.brand_name]){seen[r.brand_name]=true;names.push(r.brand_name);}});
  c.setOption({tooltip:{trigger:"axis"},legend:{bottom:0,textStyle:{color:"#94a3b8",fontSize:10},data:["浏览量","访客数"]},toolbox:{right:10,feature:{saveAsImage:{title:"保存",pixelRatio:2,backgroundColor:"#0a0e17"}}},grid:{left:45,right:15,top:10,bottom:48},xAxis:{type:"category",data:names,axisLabel:{color:"#94a3b8",fontSize:10}},yAxis:{axisLabel:{color:"#94a3b8"},splitLine:{lineStyle:{color:"#1e293b"}}},animationDuration:500,animationDurationUpdate:600,series:[{name:"浏览量",type:"bar",data:names.map(function(b){var r=brandRank.value.find(function(x){return x.brand_name===b});return r?r.pv:0;}),itemStyle:{borderRadius:[5,5,0,0],color:"#3b82f6"},markLine:{silent:true,data:[{type:"average",name:"平均",lineStyle:{color:"#f59e0b",type:"dashed"}}],label:{formatter:function(v){return "均"+Math.round(v.value);},fontSize:9,color:"#f59e0b"},symbol:"none"}},{name:"访客数",type:"bar",data:names.map(function(b){var r=brandRank.value.find(function(x){return x.brand_name===b});return r?r.uv:0;}),itemStyle:{borderRadius:[5,5,0,0],color:"#8b5cf6"}}]});
  c.on("click",function(p){if(p.name) brandHighlight(p.name);});
  _brandCharts.push(c);
}

function drawMarketShare(ec){
  var el=document.getElementById("mc2"); if(!el||!marketShare.value.length)return; ec.dispose(el);var c=ec.init(el);
  var dates=[],sd={};marketShare.value.forEach(function(r){var tm = String(r.stats_hour||0).padStart(2,'0') + ':' + (r.stats_minute || '00:00');var label = r.stats_date + ' ' + tm; if(!sd[label]){sd[label]=true;dates.push(label);}});dates.sort();
  var brands=[],sb={};marketShare.value.forEach(function(r){if(!sb[r.brand_name]){sb[r.brand_name]=true;brands.push(r.brand_name);}});
  var isSingle = brands.length === 1;
  var colors = ["#3b82f6","#10b981","#f59e0b","#ef4444","#8b5cf6"];
  c.setOption({tooltip:{trigger:"axis"},legend:{bottom:0,textStyle:{color:"#94a3b8",fontSize:9},data:brands},toolbox:{right:10,feature:{saveAsImage:{title:"保存",pixelRatio:2,backgroundColor:"#0a0e17"}}},grid:{left:45,right:15,top:10,bottom:isSingle?30:40},xAxis:{type:"category",data:dates,axisLabel:{color:"#94a3b8",fontSize:10,interval:0,rotate:30,formatter:function(v){var p=v.split(' ');return p.length>1?p[1]:v;}}},yAxis:{name:"%",axisLabel:{color:"#94a3b8"},splitLine:{lineStyle:{color:"#1e293b"}}},animationDuration:500,animationDurationUpdate:600,series:brands.map(function(b,i){var cl=colors[i];return{name:b,type:"line",smooth:true,symbol:"circle",symbolSize:isSingle?7:5,emphasis:{focus:"series"},data:dates.map(function(d){var r=marketShare.value.find(function(x){var tm = String(x.stats_hour||0).padStart(2,'0') + ':' + (x.stats_minute || '00:00');var xl=x.stats_date+' '+tm;return x.brand_name===b&&xl===d});return r?r.share_pct:null;}),lineStyle:{width:isSingle?3:2,color:cl},areaStyle:isSingle?{color:{type:"linear",x:0,y:0,x2:0,y2:1,colorStops:[{offset:0,color:cl+"40"},{offset:1,color:cl+"05"}]}}:undefined,itemStyle:{color:cl}};})});
  c.on("click",function(p){if(p.seriesName) brandHighlight(p.seriesName);});
  _brandCharts.push(c);
}

function drawKeywordBar(ec){
  var el=document.getElementById("mc3"); if(!el||!keywords.value.length)return; ec.dispose(el);var c=ec.init(el);
  var top15=keywords.value.slice(0,15).reverse();
  c.setOption({tooltip:{trigger:"axis",axisPointer:{type:"shadow"}},toolbox:{right:10,feature:{saveAsImage:{title:"保存",pixelRatio:2,backgroundColor:"#0a0e17"}}},grid:{left:85,right:45,top:5,bottom:25},xAxis:{type:"value",axisLabel:{color:"#94a3b8",fontSize:10},splitLine:{lineStyle:{color:"#1e293b"}}},yAxis:{type:"category",data:top15.map(function(r){return r.keyword;}),axisLabel:{color:"#94a3b8",fontSize:10}},animationDuration:500,animationDurationUpdate:600,series:[{type:"bar",data:top15.map(function(r){return{value:r.search_count,itemStyle:{borderRadius:[0,4,4,0],color:"#3b82f6"}};}),barWidth:14}]});
}

function drawFuelTrend(ec){
  var el=document.getElementById("mc4"); if(!el||!fuelTrend.value.length)return; ec.dispose(el);var c=ec.init(el);
  c.setOption({tooltip:{trigger:"item",formatter:function(p){return p.name+": "+p.value+" PV ("+p.percent+"%)";}},legend:{bottom:0,textStyle:{color:"#94a3b8",fontSize:10}},toolbox:{right:10,feature:{saveAsImage:{title:"保存",pixelRatio:2,backgroundColor:"#0a0e17"}}},animationDuration:500,animationDurationUpdate:600,series:[{type:"pie",radius:["45%","72%"],center:["50%","45%"],roseType:"area",itemStyle:{borderRadius:4,borderColor:"#0a0e17",borderWidth:2},label:{color:"#94a3b8",fontSize:11},data:fuelTrend.value.map(function(r){return{name:r.fuel_type,value:r.total_pv};})}]});
}

function drawPriceReasons(ec){
  var el=document.getElementById("mc5"); if(!el||!priceReasons.value.length)return; ec.dispose(el);var c=ec.init(el);
  var data=priceReasons.value.slice(0,8).map(function(r){return{name:r.price_change_reason,value:r.occurrence_count};});
  c.setOption({tooltip:{trigger:"item",formatter:function(p){return p.name+": "+p.value+"次 ("+p.percent+"%)";}},legend:{bottom:0,textStyle:{color:"#94a3b8",fontSize:10}},toolbox:{right:10,feature:{saveAsImage:{title:"保存",pixelRatio:2,backgroundColor:"#0a0e17"}}},animationDuration:500,animationDurationUpdate:600,series:[{type:"pie",radius:["40%","65%"],center:["50%","38%"],label:{color:"#94a3b8",fontSize:10},itemStyle:{borderColor:"#0a0e17",borderWidth:2},data:data}]});
}

function drawPriceWar(ec){
  var el=document.getElementById("mc6"); if(!el||!priceWar.value.length)return; ec.dispose(el);var c=ec.init(el);
  var top10=priceWar.value.slice(0,10);
  var LEVEL_CN = { high: "高", medium: "中", normal: "低" };
  c.setOption({tooltip:{trigger:"axis",axisPointer:{type:"shadow"},formatter:function(ps){var d=ps[0];var r=top10.find(function(x){return(x.brand_name+" "+x.car_type)===d.name;});return d.name+"<br/>折扣率: "+(r?r.avg_discount_pct:"-")+"%<br/>监测等级: "+(r&&LEVEL_CN[r.alert_level]?LEVEL_CN[r.alert_level]:r?r.alert_level:"-");}},toolbox:{right:10,feature:{saveAsImage:{title:"保存",pixelRatio:2,backgroundColor:"#0a0e17"}}},grid:{left:100,right:25,top:10,bottom:20},xAxis:{type:"value",name:"折扣率%",axisLabel:{color:"#94a3b8",fontSize:9},splitLine:{lineStyle:{color:"#1e293b"}}},yAxis:{type:"category",data:top10.map(function(r){return r.brand_name+" "+r.car_type;}).reverse(),axisLabel:{color:"#94a3b8",fontSize:9}},animationDuration:500,animationDurationUpdate:600,series:[{type:"bar",data:top10.map(function(r){return{value:r.avg_discount_pct||0,itemStyle:{borderRadius:[0,4,4,0],color:ALERT_COLORS[r.alert_level]||"#3b82f6"}};}).reverse()}]});
  c.on("click",function(p){if(p.name){var bn=p.name.split(" ")[0];brandHighlight(bn);}});
  _brandCharts.push(c);
}

function drawPromotionEffect(ec){
  var el=document.getElementById("mc7"); if(!el||!promotionEffect.value.length)return;
  ec.dispose(el);var c=ec.init(el);
  var top10=promotionEffect.value.slice(0,10).reverse();
  c.setOption({tooltip:{trigger:"axis",axisPointer:{type:"shadow"}},toolbox:{right:10,feature:{saveAsImage:{title:"保存",pixelRatio:2,backgroundColor:"#0a0e17"}}},grid:{left:110,right:20,top:5,bottom:15},xAxis:{type:"value",axisLabel:{color:"#94a3b8",fontSize:9},splitLine:{lineStyle:{color:"#1e293b"}}},yAxis:{type:"category",data:top10.map(function(r){return r.promotion_name;}),axisLabel:{color:"#94a3b8",fontSize:9}},animationDuration:500,animationDurationUpdate:600,series:[{type:"bar",data:top10.map(function(r){return{value:r.quote_count,itemStyle:{borderRadius:[0,4,4,0],color:"#f59e0b"}};}),barWidth:14}]});
}

function drawBrandCollectChart(ec){
  var el=document.getElementById("mc8"); if(!el||!brandCollect.value.length)return;
  ec.dispose(el);var c=ec.init(el);
  c.setOption({tooltip:{trigger:"axis"},toolbox:{right:10,feature:{saveAsImage:{title:"保存",pixelRatio:2,backgroundColor:"#0a0e17"}}},grid:{left:55,right:20,top:10,bottom:20},xAxis:{type:"category",data:brandCollect.value.map(function(r){return r.brand_name;}),axisLabel:{color:"#94a3b8",fontSize:10}},yAxis:{name:"%",axisLabel:{color:"#94a3b8"},splitLine:{lineStyle:{color:"#1e293b"}}},animationDuration:500,animationDurationUpdate:600,series:[{type:"bar",data:brandCollect.value.map(function(r){return{value:r.collect_rate||0,itemStyle:{borderRadius:[5,5,0,0],color:"#10b981"}};}),barWidth:20}]});
  c.on("click",function(p){if(p.name) brandHighlight(p.name);});
  _brandCharts.push(c);
}
</script>