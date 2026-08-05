<template>
  <el-config-provider>
    <div class="common-layout">
      <el-container>
        <el-header class="header">
          <h1>基于DEA的地区医疗投入与健康效益关联性和可视化系统</h1>
          <p style="font-size: 20px; margin-top: -5px; opacity: 0.8;">Data Envelopment Analysis & Gini Coefficient System</p>
        </el-header>

        <el-main class="main-content">
          <!-- 第一行：全局概览与核心分类 -->
          <el-row :gutter="20">
            <!-- 1. 全国地图 -->
            <el-col :span="8">
              <el-card shadow="always" class="grid-card">
                <template #header>
                  <div class="card-header">
                    <span class="title-bold">全国DEA综合效率空间分布地图</span>
                    <el-select v-model="currentYear" @change="handleGlobalYearChange" size="small" style="width:100px">
                      <el-option v-for="year in yearList" :key="year" :label="year" :value="year" />
                    </el-select>
                  </div>
                </template>
                <div id="map-chart" class="chart-box"></div>
                <div class="map-footer">提示：滚轮缩放，点击省份切换详情</div>
              </el-card>
            </el-col>

            <!-- 3. 投入冗余与不足 (详细分析) -->
            <el-col :span="8">
              <el-card shadow="hover" class="grid-card">
                <template #header><span>{{ currentRegion }} - DEA结果明细 ({{ currentYear }})</span></template>
                <div v-if="regionDetailData" class="waste-panel">
                  <div class="waste-section">
                    <div class="section-title redundancy">● 投入冗余</div>
                    <el-row :gutter="5">
                      <el-col :span="8" v-for="(label, idx) in regionDetailData.waste_analysis.redundancy.labels.slice(0,3)" :key="'r'+idx">
                        <div class="info-box"><span class="label">{{ label.slice(0,4) }}</span><span class="value red">{{ regionDetailData.waste_analysis.redundancy.values[idx] }}</span></div>
                      </el-col>
                    </el-row>
                  </div>
                  <div class="waste-section" style="margin-top: 8px;">
                    <div class="section-title deficit">● 产出不足</div>
                    <el-row :gutter="5">
                      <el-col :span="12" v-for="(label, idx) in regionDetailData.waste_analysis.deficit.labels" :key="'d'+idx">
                        <div class="info-box"><span class="label">{{ label }}</span><span class="value orange">{{ regionDetailData.waste_analysis.deficit.values[idx] }}</span></div>
                      </el-col>
                    </el-row>
                  </div>
                </div>
                <div id="detail-chart" style="width: 100%; height: 250px;"></div>
              </el-card>
            </el-col>

            <!-- 3. 聚类画像 -->
            <el-col :span="8">
              <el-card shadow="hover" class="grid-card">
                <template #header><span>全国医疗卫生配置聚类分布 ({{ currentYear }})</span></template>
                <div id="cluster-scatter-chart" class="chart-box"></div>
              </el-card>
            </el-col>
          </el-row>

          <!-- 第二行：公平性与统计验证 -->
          <el-row :gutter="20" style="margin-top: 20px;">
            <!-- 4. 公平性评价 -->
            <el-col :span="8">
              <el-card shadow="hover" class="grid-card">
                <template #header><span>{{ currentYear }}基尼系数结果</span></template>
                <div id="gini-bar-chart" class="chart-box"></div>
              </el-card>
            </el-col>

            <!-- 5. 基尼趋势 -->
            <el-col :span="8">
              <el-card shadow="hover" class="grid-card">
                <template #header>
                  <div class="card-header">
                    <span>总量和人均基尼系数变化趋势</span>
                    <el-select v-model="currentGiniIndex" @change="loadGiniTrendData" size="small" style="width:140px">
                      <el-option v-for="idx in giniOptions" :key="idx" :label="idx" :value="idx" />
                    </el-select>
                  </div>
                </template>
                <div id="gini-trend-chart" class="chart-box"></div>
              </el-card>
            </el-col>

            <!-- 6. RSR 验证 -->
            <el-col :span="8">
              <el-card shadow="hover" class="grid-card">
                <template #header>
                  <div class="card-header">
                    <span>DEA与RSR相关性验证结果 ({{ currentYear }})</span>
                    <div v-if="rsrSummary" class="rsr-tags">
                      <el-tag type="success" size="small">{{ rsrSummary.correlation }}</el-tag>
                    </div>
                  </div>
                </template>
                <div id="rsr-scatter-chart" class="chart-box"></div>
              </el-card>
            </el-col>
          </el-row>

          <!-- 第三行：时序演变与关联路径 -->
          <el-row :gutter="20" style="margin-top: 20px;">
            <!-- 7. 关联网络图 -->
            <el-col :span="8">
              <el-card shadow="hover" class="grid-card">
                <template #header>“投入-产出-效益”关联路径图谱</template>
                <div id="network-chart" class="chart-box"></div>
              </el-card>
            </el-col>

            <!-- 8. 全国DEA趋势 -->
            <el-col :span="8">
              <el-card shadow="hover" class="grid-card">
                <template #header>全国DEA效率演变趋势(2015-2024)</template>
                <div id="dea-trend-chart" class="chart-box"></div>
              </el-card>
            </el-col>

            <!-- 9. 耦合协调度 -->
            <el-col :span="8">
              <el-card shadow="hover" class="grid-card">
                <template #header>基尼系数公平性与DEA效率关联展示</template>
                <div id="coupling-chart" class="chart-box"></div>
              </el-card>
            </el-col>
          </el-row>
        </el-main>
      </el-container>
    </div>
  </el-config-provider>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';
import * as echarts from 'echarts';
import axios from 'axios';
import { 
  getMapData, getRegionDetail, getRelationNetwork, 
  getGiniData, getGiniTrend, getDeaTrendData,
  getClusterData, getGiniDeaCoupling, getRsrValidation
} from './api/index'; 

const yearList = Array.from({length: 10}, (_, i) => `${2015 + i}年`);
const currentYear = ref('2024年');
const currentRegion = ref('北京市');
const currentGiniIndex = ref('地方财政医疗卫生支出(亿元)');
const giniOptions = ['地方财政医疗卫生支出(亿元)', 
            '医疗卫生机构床位数(万张)', 
            '每万人拥有卫生技术人员数(人)', 
            '医疗卫生机构数(个)',
            '人均财政卫生支出(元)', 
            '每万人医疗卫生机构床位数(张)',
            '每万人医疗卫生机构数(个)'];
const rsrSummary = ref(null);
const regionDetailData = ref(null);

let charts = {};

const initCharts = async () => {
  try {
    const mapRes = await axios.get('https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json');
    echarts.registerMap('china', mapRes.data);
    
    // 初始化
    charts.map = echarts.init(document.getElementById('map-chart'));
    charts.detail = echarts.init(document.getElementById('detail-chart'));
    charts.deaTrend = echarts.init(document.getElementById('dea-trend-chart'));
    charts.giniBar = echarts.init(document.getElementById('gini-bar-chart'));
    charts.giniTrend = echarts.init(document.getElementById('gini-trend-chart'));
    charts.network = echarts.init(document.getElementById('network-chart'));
    charts.rsrScatter = echarts.init(document.getElementById('rsr-scatter-chart'));
    charts.cluster = echarts.init(document.getElementById('cluster-scatter-chart'));
    charts.coupling = echarts.init(document.getElementById('coupling-chart'));

    charts.map.on('click', (params) => {
      currentRegion.value = params.name;
      loadRegionDetailData();
    });
  
    refreshData();
  } catch (e) {
    console.error("初始化失败", e);
  }
};

const refreshData = () => {
  loadMap();
  loadRegionDetailData();
  loadRsrValidation();
  loadGiniData();
  loadCluster();
  if(!charts.deaTrend.getOption()) loadDeaTrend();
  if(!charts.giniTrend.getOption()) loadGiniTrendData();
  if(!charts.network.getOption()) loadNetwork();
  if(!charts.coupling.getOption()) loadCoupling();
};

const handleGlobalYearChange = () => {
  loadMap();
  loadRegionDetailData();
  loadRsrValidation();
  loadGiniData();
  loadCluster();
};

const loadMap = async () => {
  const res = await getMapData(currentYear.value);
  charts.map.setOption({
    tooltip: { trigger: 'item', formatter: '{b}<br/>DEA综合效率: {c}' },
    visualMap: { 
      min: 0.5, max: 1, precision: 2, calculable: true,
      text: ['高效率', '低效率'],
      inRange: { color: ['#e0f3f8', '#0070cc'] }, 
      left: 'left', bottom: '5%'
    },
    series: [{ 
      type: 'map', map: 'china', data: res.data.data, roam: true,
      emphasis: { label: { show: true }, itemStyle: { areaColor: '#f2d643' } }
    }]
  });
};

const loadRegionDetailData = async () => {
  const res = await getRegionDetail(currentYear.value, currentRegion.value);
  regionDetailData.value = res.data;
  charts.detail.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: res.data.efficiency_metrics.labels },
    yAxis: { type: 'value', max: 1.2 },
    series: [{ 
      data: res.data.efficiency_metrics.values, type: 'bar', barWidth: '40%',
      label: { show: true, position: 'top' },
      itemStyle: { color: '#5470c6', borderRadius: [5, 5, 0, 0] }
    }]
  }, true);
};

const loadGiniData = async () => {
  const res = await getGiniData(currentYear.value);
  const chartData = res.data.chart_data;

  // 将数据包装成对象，以便 tooltip 访问 status 属性
  const seriesData = chartData.values.map((val, index) => ({
    value: val,
    status: chartData.statuses[index]
  }));

  charts.giniBar.setOption({
    // 1. 优化悬浮提示框
    tooltip: { 
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: function (params) {
        const item = params[0];
        const status = item.data.status;
        let color = item.value > 0.4 ? '#f56c6c' : '#67c23a';
        return `<b>${item.name}</b><br/>
                基尼系数: <span style="color:${item.color}">${item.value.toFixed(4)}</span><br/>
                公平性状态: <span style="color:${color}; font-weight:bold;">${status}</span>`;
      }
    },
    // 2. 指标多了，X 轴文字需要旋转并减小字体
    xAxis: { 
      type: 'category', 
      data: chartData.categories, 
      axisLabel: { 
        rotate: 35, // 增加旋转角度避免重叠
        fontSize: 10,
        interval: 0 // 强制显示所有标签
      } 
    },
    yAxis: { 
      type: 'value',
      name: '基尼系数',
      max: 0.6, // 基尼系数通常在0-0.6之间，0.4为警戒线
      splitLine: { lineStyle: { type: 'dashed' } }
    },
    grid: {
      left: '12%',
      right: '5%',
      bottom: '25%', // 给旋转后的文字留出空间
      top: '15%'
    },
    series: [{ 
      data: seriesData, 
      type: 'bar', 
      barWidth: '50%',
      label: { 
        show: true, 
        position: 'top', 
        fontSize: 10,
        formatter: (p) => p.value.toFixed(2)
      },
      itemStyle: { 
        // 自动配色：超过 0.4 警戒线显示红色，否则显示深灰色
        color: (p) => p.value > 0.4 ? '#c23531' : '#447C6D' 
      },
      // 辅助线：0.4 警戒线
      markLine: {
        silent: true,
        symbol: 'none',
        lineStyle: { color: '#f56c6c', type: 'dashed' },
        data: [{ yAxis: 0.4, label: { position: 'insideEnd', formatter: '警戒线(0.4)' } }]
      }
    }]
  }, true);
};

const loadCluster = async () => {
  const res = await getClusterData(currentYear.value);
  const rawData = res.data || res;

  if (!rawData || rawData.length === 0) return;

  const categories = [
    '高水平地区(PTE/SE双高)', 
    '中水平地区(PTE低/SE中)', 
    '低水平地区(PTE高/SE低)'
  ];
  const colors = ['#DE8F55', '#55A868', '#4C72B0'];

  const series = categories.map((name, index) => ({
    name: name,
    type: 'scatter',
    data: rawData.filter(item => item.cluster_name === name),
    itemStyle: { 
      color: colors[index],
      edgeColor: '#333',
      borderWidth: 1
    },
    symbolSize: 18,
    label: { show: false }, 
    emphasis: {
      label: { 
        show: true, 
        formatter: (p) => p.data.name, 
        position: 'top',
        backgroundColor: 'rgba(255,255,255,0.8)',
        padding: [2, 4],
        borderRadius: 3
      }
    }
  }));

  charts.cluster.setOption({
    tooltip: {
      trigger: 'item',
      formatter: (p) => `<b>${p.data.name}</b><br/>PTE: ${p.data.value[0]}<br/>SE: ${p.data.value[1]}`
    },
    // 2. 修改图例布局：垂直排列，防止重叠
    legend: { 
      // orient: 'vertical',  // 垂直排列
      left: 'center',      // 居中显示
      bottom: 0,           // 贴在最底部
      itemWidth: 12, 
      itemHeight: 5,
      textStyle: { fontSize: 11 },
      padding: [2, 0]     // 增加一点内边距
    },
    // 3. 调整网格，给底部的垂直图例留出空间
    grid: {
      top: '1%',
      left: '5%',
      right: '3%',
      bottom: '20%', // 增加底部边距，防止坐标轴标题和垂直图例重叠
      containLabel: false
    },
    xAxis: { 
      type: 'value',
      name: '纯技术效率(PTE)',
      nameLocation: 'middle',
      nameGap: 25,
      min: (value) => (value.min - 0.05).toFixed(1),
      max: 1.05, 
      splitLine: { show: true, lineStyle: { type: 'dashed', opacity: 0.4 } } 
    },
    yAxis: { 
      type: 'value',
      name: '规模效率(SE)',
      nameLocation: 'middle',
      nameGap: 35,
      min: (value) => (value.min - 0.05).toFixed(1),
      max: 1.05,
      splitLine: { show: true, lineStyle: { type: 'dashed', opacity: 0.4 } }
    },
    series: series,
    markLine: {
      silent: true,
      symbol: 'none',
      label: { show: false },
      lineStyle: { type: 'dashed', color: 'red', width: 1.5, opacity: 0.5 },
      data: [
        { xAxis: 1.0 },
        { yAxis: 1.0 }
      ]
    }
  }, true);
};

const loadRsrValidation = async () => {
  const res = await getRsrValidation(currentYear.value);
  const { summary, points } = res.data;
  rsrSummary.value = summary;
  if (!points || points.length === 0) return;

  const n = points.length;
  let sX=0, sY=0, sXY=0, sXX=0;
  points.forEach(p => { sX+=p.value[0]; sY+=p.value[1]; sXY+=p.value[0]*p.value[1]; sXX+=p.value[0]*p.value[0]; });
  const k = (n*sXY - sX*sY) / (n*sXX - sX*sX);
  const b = (sY - k*sX) / n;
  const minX = Math.min(...points.map(p => p.value[0])), maxX = Math.max(...points.map(p => p.value[0]));

  charts.rsrScatter.setOption({
    grid: { top: 30, bottom: 40, left: 50, right: 20 },
    xAxis: { type: 'value', min: (minX * 0.95).toFixed(2) },
    yAxis: { type: 'value', min: 0.4 },
    series: [
      {
        type: 'scatter', data: points, symbolSize: 12,
        label: { show: true, position: 'top', formatter: (p) => (p.value[1] > 0.9 || p.value[0] > 0.7) ? p.data.name : '', fontSize: 9 },
        emphasis: {
          label: { show: true, formatter: (p) => `${p.data.name}\nRSR:${p.value[0]}\nDEA:${p.value[1]}`, backgroundColor: '#fff', padding: 5, borderRadius: 4, borderWidth: 1, borderColor: '#ccc' }
        },
        markLine: { lineStyle: { color: 'green' }, label: { position: 'insideEnd', formatter: '平均:{c}' }, data: [{ type: 'average' }] }
      },
      { type: 'line', data: [[minX, k*minX+b], [maxX, k*maxX+b]], showSymbol: false, lineStyle: { color: 'red', opacity: 0.5 } },
      { 
        type: 'custom', data: [0], 
        renderItem: (params, api) => {
          const p1 = api.coord([minX, k*minX+b+0.035]), p2 = api.coord([maxX, k*maxX+b+0.035]);
          const p3 = api.coord([maxX, k*maxX+b-0.035]), p4 = api.coord([minX, k*minX+b-0.035]);
          return { type: 'polygon', shape: { points: [p1,p2,p3,p4] }, style: api.style({ fill: 'red', opacity: 0.05 }) };
        }
      }
    ]
  }, true);
};

const loadDeaTrend = async () => {
  const res = await getDeaTrendData();
  charts.deaTrend.setOption({
    tooltip: { trigger: 'axis' }, legend: { bottom: 0 },
    xAxis: { type: 'category', data: res.data.years },
    yAxis: { type: 'value', min: 0.5 },
    series: ['te', 'pte', 'se'].map(k => ({ name: k.toUpperCase(), type: 'line', data: res.data[k], smooth: true }))
  });
};

const loadGiniTrendData = async () => {
  const res = await getGiniTrend(currentGiniIndex.value);
  charts.giniTrend.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: res.data.years },
    yAxis: { type: 'value', scale: true },
    series: [{ 
      data: res.data.values, type: 'line', symbol: 'circle', symbolSize: 8,
      label: { show: true, position: 'top' } // 数据标注
    }]
  });
};

const loadNetwork = async () => {
  const res = await getRelationNetwork();
  charts.network.setOption({
    series: [{ 
      type: 'graph', layout: 'force', data: res.data.nodes, links: res.data.links, 
      label: { show: true, fontSize: 10 }, draggable: true,
      force: { repulsion: 200, edgeLength: 50 }
    }]
  });
};

const loadCoupling = async () => {
  const res = await getGiniDeaCoupling();
  const { years, gini_all, gini_total, gini_per, dea_values } = res.data;

  charts.coupling.setOption({
    tooltip: { trigger: 'axis' },
    legend: { bottom: 0, textStyle: { fontSize: 10 } },
    grid: { top: '15%', left: '10%', right: '10%', bottom: '15%' },
    xAxis: { type: 'category', data: years },
    yAxis: [
      { type: 'value', name: 'Gini系数', min: 0.1, max: 0.36 },
      { type: 'value', name: '综合效率(TE)', min: 0.7, max: 1.0 }
    ],
    series: [
      { name: '总量基尼均值', type: 'line', data: gini_total, yAxisIndex: 0, lineStyle: { type: 'dashed' }, itemStyle: { color: '#fb8c00' } },
      { name: '人均基尼均值', type: 'line', data: gini_per, yAxisIndex: 0, lineStyle: { type: 'dashed' }, itemStyle: { color: '#43a047' } },
      { 
        name: '全国平均效率(TE)', type: 'bar', data: dea_values, yAxisIndex: 1, 
        barWidth: '20%', itemStyle: { color: '#1565C0', opacity: 0.6 } 
      }
    ]
  }, true);
};

onMounted(() => {
  nextTick(() => initCharts());
  window.onresize = () => Object.values(charts).forEach(c => c.resize());
});
</script>

<style scoped>
.header { 
  background: #171e72; 
  color: white; 
  text-align: center; 
  padding: 15px 0; 
  height: 90px; 
}

.main-content { 
  background: #f0f2f5; 
  padding: 15px; 
}

/* 统一所有卡片的高度 */
.grid-card { 
  height: 440px; 
  border-radius: 8px; 
  margin-bottom: 0px;
}

/* 统一所有图表容器的高度 */
.chart-box {
  width: 100%;
  height: 340px;
}

.card-header { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  font-size: 14px;
}

.title-bold { font-weight: bold; }

/* 冗余面板小幅度紧凑调整 */
.waste-panel {
  padding: 8px;
  background: #f9f9f9;
  border-radius: 6px;
  margin-bottom: 5px;
  font-size: 11px;
}
.section-title { font-weight: bold; margin-bottom: 3px; font-size: 12px; }
.section-title.redundancy { color: #f56c6c; }
.section-title.deficit { color: #e6a23c; }

.info-box {
  background: #fff;
  border: 1px solid #eee;
  padding: 2px;
  text-align: center;
  border-radius: 4px;
}
.info-box .label { display: block; color: #999; font-size: 10px; transform: scale(0.9); }
.info-box .value { font-weight: bold; font-size: 12px; }
.info-box .value.red { color: #f56c6c; }
.info-box .value.orange { color: #e6a23c; }

.map-footer { text-align: center; color: #999; font-size: 10px; margin-top: 2px; }

/* 针对特定图表的微调 */
#detail-chart {
  margin-top: 5px;
}
</style>