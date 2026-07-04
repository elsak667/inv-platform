<template>
  <div class="page-container">
    <div v-if="loading">加载中...</div>
    <div v-else-if="!cfg" class="empty-state">模板加载失败</div>
    <div v-else class="kaifa-layout">
      <div class="form-panel">
        <div class="form-section">
          <div class="section-hd">1. 土地参数</div>
          <el-row :gutter="8">
            <el-col :span="8"><label>土地出让金(万元)</label><el-input-number v-model="p.land.premium" :min="0" style="width:100%" size="small" /></el-col>
            <el-col :span="8"><label>用地面积(㎡)</label><el-input-number v-model="p.land.site_area" :min="0" style="width:100%" size="small" /></el-col>
            <el-col :span="8"><label>容积率</label><el-input-number v-model="p.land.floor_area_ratio" :min="0" :step="0.1" style="width:100%" size="small" /></el-col>
          </el-row>
          <el-row :gutter="8" style="margin-top:8px">
            <el-col :span="8"><label>总建面(㎡)</label><el-input-number v-model="p.land.total_gfa" :min="0" style="width:100%" size="small" /></el-col>
            <el-col :span="8"><label>契税税率</label><el-input-number v-model="p.land.deed_tax_rate" :min="0" :max="0.1" :step="0.001" :formatter="pct" :parser="unpct" style="width:100%" size="small" /></el-col>
            <el-col :span="8"><label>配套费(元/㎡)</label><el-input-number v-model="p.land.city_support_fee_per_sqm" :min="0" style="width:100%" size="small" /></el-col>
          </el-row>
        </div>

        <div class="form-section">
          <div class="section-hd">2. 产品</div>
          <div v-for="(prod, i) in p.products" :key="i" class="prod-block">
            <div class="prod-hd">产品{{ i+1 }} <el-button type="danger" link size="small" @click="p.products.splice(i,1)">×</el-button></div>
            <el-row :gutter="6">
              <el-col :span="6"><label>名称</label><el-input v-model="prod.name" size="small" /></el-col>
              <el-col :span="4"><label>类型</label><el-select v-model="prod.type" size="small" style="width:100%"><el-option label="住宅" value="住宅"/><el-option label="商业" value="商业"/><el-option label="车库" value="车库"/></el-select></el-col>
              <el-col :span="4"><label>建面(㎡)</label><el-input-number v-model="prod.gfa" :min="0" style="width:100%" size="small" /></el-col>
              <el-col :span="4"><label>可售(㎡)</label><el-input-number v-model="prod.saleable_area" :min="0" style="width:100%" size="small" /></el-col>
              <el-col :span="3"><label>售价(元/㎡)</label><el-input-number v-model="prod.unit_price" :min="0" :step="100" style="width:100%" size="small" /></el-col>
              <el-col :span="3"><label>建安(元/㎡)</label><el-input-number v-model="prod.const_cost_per_sqm" :min="0" :step="100" style="width:100%" size="small" /></el-col>
              <el-col v-if="prod.type==='车库'" :span="3"><label>车位数</label><el-input-number v-model="prod.parking_spots" :min="0" style="width:100%" size="small" /></el-col>
              <el-col v-if="prod.type==='车库'" :span="3"><label>单价(万/个)</label><el-input-number v-model="prod.parking_price" :min="0" :step="1" style="width:100%" size="small" /></el-col>
            </el-row>
          </div>
          <el-button type="primary" link size="small" @click="addProd">+ 新增产品</el-button>
        </div>

        <div class="form-section">
          <div class="section-hd">3. 费率</div>
          <el-row :gutter="8">
            <el-col :span="6"><label>管理费率</label><el-input-number v-model="p.fees.management_fee_rate" :min="0" :max="0.1" :step="0.001" :formatter="pct" :parser="unpct" style="width:100%" size="small" /></el-col>
            <el-col :span="6"><label>营销费率</label><el-input-number v-model="p.fees.marketing_fee_rate" :min="0" :max="0.1" :step="0.001" :formatter="pct" :parser="unpct" style="width:100%" size="small" /></el-col>
            <el-col :span="6"><label>前期费率</label><el-input-number v-model="p.fees.preliminary_rate" :min="0" :max="0.1" :step="0.001" :formatter="pct" :parser="unpct" style="width:100%" size="small" /></el-col>
            <el-col :span="6"><label>不可预见费</label><el-input-number v-model="p.fees.contingency_rate" :min="0" :max="0.1" :step="0.001" :formatter="pct" :parser="unpct" style="width:100%" size="small" /></el-col>
          </el-row>
        </div>

        <div class="form-section">
          <div class="section-hd">4. 融资 & 销售</div>
          <el-row :gutter="8">
            <el-col :span="6"><label>自有资金比例</label><el-input-number v-model="p.financing.equity_ratio" :min="0" :max="1" :step="0.01" :formatter="pct" :parser="unpct" style="width:100%" size="small" /></el-col>
            <el-col :span="6"><label>开发贷年利率</label><el-input-number v-model="p.financing.dev_loan_interest_rate" :min="0" :max="0.15" :step="0.001" :formatter="pct" :parser="unpct" style="width:100%" size="small" /></el-col>
            <el-col :span="6"><label>去化周期(月)</label><el-input-number v-model="p.sales.sell_period_months" :min="1" :max="60" style="width:100%" size="small" /></el-col>
            <el-col :span="6"><label>首付比例</label><el-input-number v-model="p.sales.front_payment_ratio" :min="0" :max="1" :step="0.05" :formatter="pct" :parser="unpct" style="width:100%" size="small" /></el-col>
          </el-row>
        </div>

        <div class="form-section">
          <div class="section-hd">5. 税金</div>
          <el-row :gutter="8">
            <el-col :span="6"><label>增值税预征率</label><el-input-number v-model="p.taxes.vat_prepay_rate" :min="0" :max="0.1" :step="0.001" :formatter="pct" :parser="unpct" style="width:100%" size="small" /></el-col>
            <el-col :span="6"><label>附加税率</label><el-input-number v-model="p.taxes.vat_additional_rate" :min="0" :max="0.2" :step="0.01" :formatter="pct" :parser="unpct" style="width:100%" size="small" /></el-col>
            <el-col :span="6"><label>土增预征(住宅)</label><el-input-number v-model="p.taxes.land_tax_prepay_rate" :min="0" :max="0.05" :step="0.001" :formatter="pct" :parser="unpct" style="width:100%" size="small" /></el-col>
            <el-col :span="6"><label>土增预征(商业)</label><el-input-number v-model="p.taxes.land_tax_prepay_commercial" :min="0" :max="0.05" :step="0.001" :formatter="pct" :parser="unpct" style="width:100%" size="small" /></el-col>
          </el-row>
        </div>

        <el-button type="primary" @click="runCalc" :loading="running" class="calc-btn">开始测算</el-button>
      </div>

      <div class="result-panel" v-if="result">
        <el-tabs v-model="activeTab" class="result-tabs" @tab-change="redrawOnTab">
          <!-- Tab 1: 总览 -->
          <el-tab-pane label="总览" name="overview">
            <div class="metric-grid-4">
              <div class="big-metric"><label>净利润</label><span class="big-val" :class="{pos: pf.net_profit>0}">{{ fmt0(pf.net_profit) }}万</span></div>
              <div class="big-metric"><label>净利率</label><span class="big-val">{{ (pf.net_margin*100).toFixed(2) }}%</span></div>
              <div class="big-metric"><label>项目IRR(年)</label><span class="big-val">{{ irrYear(cf.project_irr).toFixed(2) }}%</span></div>
              <div class="big-metric"><label>回正周期</label><span class="big-val">{{ cf.payback_month || '-' }}个月</span></div>
            </div>
            <div class="chart-row">
              <div class="chart-card">
                <div class="card-hd">成本构成</div>
                <div ref="costPieRef" style="width:100%;height:240px"></div>
              </div>
              <div class="chart-card">
                <div class="card-hd">指标雷达</div>
                <div ref="radarRef" style="width:100%;height:240px"></div>
              </div>
            </div>
            <div class="conclusion-card">
              <div class="card-hd">测算结论</div>
              <div class="conclusion-text" v-html="conclusion"></div>
            </div>
          </el-tab-pane>

          <!-- Tab 2: 利润表 -->
          <el-tab-pane label="利润表" name="pl">
            <div class="result-section">
              <el-table :data="plRows" :summary-method="plSummary" border size="small" show-summary>
                <el-table-column prop="item" label="科目" min-width="220" />
                <el-table-column prop="amount" label="金额(万元)" align="right" width="140">
                  <template #default="{row}"><span :class="{pos:row.amount>0, neg:row.amount<0}">{{ fmt0(row.amount) }}</span></template>
                </el-table-column>
                <el-table-column prop="note" label="说明" min-width="200" />
              </el-table>
            </div>
          </el-tab-pane>

          <!-- Tab 3: 税金拆解 -->
          <el-tab-pane label="税金拆解" name="tax">
            <div class="result-section" v-if="r.vat">
              <div class="section-hd">增值税链</div>
              <el-table :data="vatRows" border size="small">
                <el-table-column prop="item" label="科目" min-width="200" />
                <el-table-column prop="amount" label="金额(万元)" align="right" width="140">
                  <template #default="{row}">{{ fmt0(row.amount) }}</template>
                </el-table-column>
                <el-table-column prop="note" label="说明" min-width="200" />
              </el-table>
            </div>
            <div class="result-section" v-if="r.taxes.land_settlement_detail">
              <div class="section-hd">土地增值税清算（三分法）</div>
              <el-table :data="latRows" border size="small">
                <el-table-column prop="type" label="类型" width="120" />
                <el-table-column prop="revenue_ex_vat" label="收入(不含税)" align="right" width="120">
                  <template #default="{row}">{{ fmt0(row.revenue_ex_vat) }}</template>
                </el-table-column>
                <el-table-column prop="deduction" label="扣除合计" align="right" width="120">
                  <template #default="{row}">{{ fmt0(row.deduction) }}</template>
                </el-table-column>
                <el-table-column prop="excess_ratio" label="增值率" align="right" width="100">
                  <template #default="{row}">{{ (row.excess_ratio*100).toFixed(2) }}%</template>
                </el-table-column>
                <el-table-column prop="rate" label="税率" align="right" width="80">
                  <template #default="{row}">{{ (row.rate*100).toFixed(0) }}%</template>
                </el-table-column>
                <el-table-column prop="tax" label="应纳税额" align="right" width="120">
                  <template #default="{row}"><span class="pos">{{ fmt0(row.tax) }}</span></template>
                </el-table-column>
              </el-table>
              <div class="lat-summary">
                <span>预征: {{ fmt0(r.taxes.prepay?.land_prepay) }}万</span>
                <span>清算找差: {{ fmt0(r.taxes.land_settlement_diff) }}万</span>
                <span class="pos">合计入账: {{ fmt0(r.taxes.land_appreciation) }}万</span>
              </div>
            </div>
          </el-tab-pane>

          <!-- Tab 4: 现金流 -->
          <el-tab-pane label="现金流" name="cashflow">
            <div class="metric-grid-4">
              <div class="big-metric"><label>项目IRR(年)</label><span class="big-val">{{ irrYear(cf.project_irr).toFixed(2) }}%</span></div>
              <div class="big-metric"><label>权益IRR(年)</label><span class="big-val">{{ irrYear(cf.equity_irr).toFixed(2) }}%</span></div>
              <div class="big-metric"><label>峰值资金需求</label><span class="big-val">{{ fmt0(cf.peak_deficit) }}万</span></div>
              <div class="big-metric"><label>权益出资</label><span class="big-val">{{ fmt0(cf.equity) }}万</span></div>
            </div>
            <div class="result-section">
              <div class="section-hd">现金流曲线</div>
              <div ref="cfChartRef" style="width:100%;height:300px"></div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api/index.js'
import * as echarts from 'echarts'
export default {
  data() {
    return { loading: true, cfg: null, p: null, result: null, running: false, activeTab: 'overview',
      cfChart: null, costPie: null, radarChart: null }
  },
  computed: {
    r() { return this.result || {} },
    pf() { return this.r.profit || {} },
    cf() { return this.r.cashflow || {} },
    plRows() {
      const pf = this.pf, r = this.r, v = this.r.vat || {}, t = this.r.taxes || {}
      return [
        { item: '一、营业收入(不含税)', amount: pf.total_revenue_ex_vat, note: '含税销售 - 销项税' },
        { item: '  减:营业成本', amount: -r.land_cost?.total - (v.cost_ex_vat?.total || 0), note: '土地(含税) + 建安/前期/三费(不含税)' },
        { item: '  减:税金及附加', amount: -(t.vat_additional + t.land_appreciation + t.stamp), note: '附加税 + 土增税 + 印花税' },
        { item: '二、利润总额', amount: pf.profit_before_tax, note: '营业利润' },
        { item: '  减:所得税', amount: -pf.income_tax, note: '利润总额 × 25%' },
        { item: '三、净利润', amount: pf.net_profit, note: '本年净利润' },
      ]
    },
    vatRows() {
      const v = this.r.vat || {}
      return [
        { item: '销项税额', amount: v.output_vat, note: '含税销售 ÷ 1.09 × 9%' },
        { item: '土地抵减销项', amount: v.land_deduction, note: '土地款 ÷ 1.09 × 9%' },
        { item: '进项税额合计', amount: v.input_vat?.total, note: '建安/前期/三费进项' },
        { item: '应交增值税', amount: v.vat_payable, note: '销项 - 土地抵减 - 进项' },
        { item: '附加税合计', amount: this.r.taxes?.vat_additional, note: '城建税7%+教育3%+地方教育2%' },
      ]
    },
    latRows() {
      const types = this.r.taxes?.land_settlement_detail?.types || []
      return types.filter(t => t.gfa > 0)
    },
    conclusion() {
      const pf = this.pf, cf = this.cf
      if (!pf.net_profit && pf.net_profit !== 0) return ''
      const margin = (pf.net_margin * 100).toFixed(1)
      const irr = this.irrYear(cf.project_irr).toFixed(1)
      const verdict = pf.net_margin > 0.12 ? '<b style="color:#10b981">财务可行</b>'
        : pf.net_margin > 0.08 ? '<b style="color:#f59e0b">边际可行</b>'
        : '<b style="color:#ef4444">财务不可行</b>'
      return `项目预计净利润 <b>${this.fmt0(pf.net_profit)}万元</b>，净利率 <b>${margin}%</b>，项目IRR <b>${irr}%</b>，资金回正周期 <b>${cf.payback_month || '-'}个月</b>。
      综合判断：<span style="font-size:13px">${verdict}</span>。`
    },
  },
  async mounted() {
    try {
      this.cfg = await api.getTemplate('kaifa')
      const { meta, ...rest } = this.cfg; this.p = JSON.parse(JSON.stringify(rest))
    } catch (e) { this.$message.error(String(e)) }
    this.loading = false
  },
  methods: {
    pct(v) { return v != null ? (v * 100).toFixed(1) + '%' : '' },
    unpct(v) { return parseFloat(v.replace('%', '')) / 100 },
    fmt0(v) { return Number(v || 0).toLocaleString('zh-CN', {minimumFractionDigits:2, maximumFractionDigits:2}) },
    irrYear(m) { return m ? ((1+m)**12-1)*100 : 0 },
    addProd() {
      this.p.products.push({ name:'', type:'住宅', gfa:10000, saleable_area:9500, unit_price:20000, const_cost_per_sqm:4000, decoration:'毛坯' })
    },
    plSummary({ columns, data }) {
      const sums = []
      columns.forEach((col, i) => {
        if (i === 0) { sums[i] = '合计'; return }
        if (col.property === 'amount') {
          sums[i] = data.reduce((acc, row) => acc + (Number(row.amount) || 0), 0)
          sums[i] = this.fmt0(sums[i])
        } else sums[i] = ''
      })
      return sums
    },
    drawAllCharts() {
      setTimeout(() => {
        if (this.activeTab === 'overview') {
          this.drawCostPie()
          this.drawRadar()
        }
        if (this.activeTab === 'cashflow') {
          this.drawCfChart()
        }
      }, 200)
    },
    redrawOnTab() {
      this.$nextTick(() => {
        if (this.activeTab === 'overview') { this.drawCostPie(); this.drawRadar() }
        if (this.activeTab === 'cashflow') { this.drawCfChart() }
      })
    },
    drawCfChart() {
      const el = this.$refs.cfChartRef
      if (!el || !this.cf.project_cf?.length) return
      if (this.cfChart) this.cfChart.dispose()
      this.cfChart = echarts.init(el)
      const months = this.cf.project_cf.map((_, i) => `第${i}月`)
      const project = this.cf.project_cf.map(v => Math.round(v))
      const equity = this.cf.equity_cf ? this.cf.equity_cf.map(v => Math.round(v)) : null
      const series = [{
        name: '项目现金流', type: 'line', data: project,
        smooth: true, lineStyle: { width: 2 }, itemStyle: { color: '#3b82f6' },
        areaStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1, [{offset:0,color:'rgba(59,130,246,0.2)'},{offset:1,color:'rgba(59,130,246,0)'}]) },
        markLine: this.cf.peak_month != null ? {
          symbol: 'none', lineStyle: { type: 'dashed', color: '#ef4444' },
          data: [{ xAxis: this.cf.peak_month, label: { formatter: '峰值资金', position: 'start' } }],
        } : undefined,
      }]
      if (equity) series.push({
        name: '权益现金流', type: 'line', data: equity,
        smooth: true, lineStyle: { width: 2 }, itemStyle: { color: '#10b981' },
      })
      this.cfChart.setOption({
        tooltip: { trigger: 'axis', valueFormatter: v => v != null ? `${v.toFixed(0)}万` : '' },
        legend: { show: true, bottom: 0 },
        grid: { left: 50, right: 16, top: 16, bottom: 36 },
        xAxis: { type: 'category', data: months, axisLabel: { rotate: 45, fontSize: 9, interval: 2 } },
        yAxis: { type: 'value', axisLabel: { formatter: v => `${v}万` } },
        series,
      })
      this.cfChart.resize()
    },
    drawCostPie() {
      const el = this.$refs.costPieRef
      if (!el) return
      if (this.costPie) this.costPie.dispose()
      this.costPie = echarts.init(el)
      const r = this.r
      const data = [
        { name: '土地', value: Math.round(r.land_cost?.total || 0) },
        { name: '建安', value: Math.round(r.construction?.total || 0) },
        { name: '前期/间接', value: Math.round(r.other_direct?.total || 0) },
        { name: '三费', value: Math.round(r.period_fees?.total || 0) },
        { name: '税金', value: Math.round(r.taxes?.total || 0) },
      ].filter(d => d.value > 0)
      this.costPie.setOption({
        tooltip: { trigger: 'item', formatter: '{b}: {c}万 ({d}%)' },
        legend: { bottom: 0, textStyle: { fontSize: 11 } },
        series: [{
          type: 'pie', radius: ['40%', '70%'], center: ['50%', '45%'],
          itemStyle: { borderColor: '#fff', borderWidth: 2 },
          label: { formatter: '{b}\n{d}%', fontSize: 10 },
          data,
          color: ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444'],
        }],
      })
      this.costPie.resize()
    },
    drawRadar() {
      const el = this.$refs.radarRef
      if (!el) return
      if (this.radarChart) this.radarChart.dispose()
      this.radarChart = echarts.init(el)
      const pf = this.pf, cf = this.cf
      const marginScore = Math.min(100, (pf.net_margin || 0) * 500)
      const irrScore = Math.min(100, (this.irrYear(cf.project_irr) / 0.25) * 100)
      const paybackScore = Math.min(100, Math.max(0, (36 - (cf.payback_month || 36)) / 36 * 100))
      const roiScore = Math.min(100, (pf.roi || 0) * 200)
      const peakScore = Math.max(0, 100 - (cf.peak_deficit || 0) / (cf.total_investment || 1) * 200)
      this.radarChart.setOption({
        tooltip: {},
        radar: {
          indicator: [
            { name: '净利率', max: 100 }, { name: 'IRR', max: 100 },
            { name: '回正速度', max: 100 }, { name: 'ROI', max: 100 }, { name: '资金压力', max: 100 },
          ],
          radius: '65%',
        },
        series: [{
          type: 'radar', data: [{
            value: [marginScore, irrScore, paybackScore, roiScore, peakScore],
            name: '项目评分', areaStyle: { color: 'rgba(59,130,246,0.2)' }, lineStyle: { color: '#3b82f6' },
          }],
        }],
      })
      this.radarChart.resize()
    },
    async runCalc() {
      this.running = true
      try {
        const params = { ...this.p, meta: this.cfg.meta }
        this.result = await api.calculate('kaifa', params)
        this.activeTab = 'overview'
        this.drawAllCharts()
      } catch (e) { this.$message.error(e.response?.data?.detail || e.message) }
      this.running = false
    },
  },
}
</script>

<style scoped>
.kaifa-layout { display:flex; gap:24px; align-items:flex-start; }
.form-panel { flex:0 0 500px; }
.result-panel { flex:1; min-width:0; }
.form-section { background:#fff; border-radius:10px; padding:16px; margin-bottom:12px; border:1px solid #e2e8f0; }
.section-hd { font-size:14px; font-weight:600; color:#1e293b; margin-bottom:12px; }
.prod-block { background:#f8fafc; border-radius:8px; padding:10px; margin-bottom:6px; }
.prod-hd { font-size:12px; font-weight:600; color:#64748b; margin-bottom:6px; }
label { font-size:10px; color:#64748b; display:block; margin-bottom:2px; }
.calc-btn { width:100%; height:42px; font-size:15px; margin-top:8px; }
.result-section { background:#fff; border-radius:10px; padding:16px; margin-bottom:12px; border:1px solid #e2e8f0; }
.metric-grid-4 { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:12px; }
.big-metric { background:#fff; border:1px solid #e2e8f0; border-radius:10px; padding:16px; text-align:center; }
.big-metric label { font-size:11px; color:#94a3b8; }
.big-val { font-size:22px; font-weight:700; display:block; margin-top:4px; color:#1e293b; }
.big-val.pos { color:#10b981; }
.chart-row { display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:12px; }
.chart-card { background:#fff; border:1px solid #e2e8f0; border-radius:10px; padding:12px; }
.card-hd { font-size:13px; font-weight:600; color:#1e293b; margin-bottom:8px; }
.conclusion-card { background:#f0fdf4; border:1px solid #bbf7d0; border-radius:10px; padding:16px; }
.conclusion-text { font-size:13px; color:#1e293b; line-height:1.7; }
.result-tabs :deep(.el-tabs__header) { margin-bottom:12px; }
.result-tabs :deep(.el-tabs__item) { font-size:14px; font-weight:500; }
.lat-summary { display:flex; justify-content:space-around; margin-top:12px; padding:8px; background:#f8fafc; border-radius:6px; font-size:13px; }
.lat-summary .pos { color:#f59e0b; font-weight:600; }
.pos { color:#10b981; }
.neg { color:#ef4444; }
.empty-state { text-align:center; padding:80px; color:#94a3b8; }
</style>
