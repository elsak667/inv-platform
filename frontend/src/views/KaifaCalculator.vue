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
        <div class="result-section">
          <div class="section-hd">盈利汇总</div>
          <el-row :gutter="8">
            <el-col :span="8"><div class="metric"><label>净利润</label><span class="val pos">{{ fmt0(pf.net_profit) }}万</span></div></el-col>
            <el-col :span="8"><div class="metric"><label>净利率</label><span class="val">{{ (pf.net_margin*100).toFixed(1) }}%</span></div></el-col>
            <el-col :span="8"><div class="metric"><label>ROI</label><span class="val">{{ (pf.roi*100).toFixed(1) }}%</span></div></el-col>
          </el-row>
        </div>
        <div class="result-section">
          <div class="section-hd">现金流指标</div>
          <el-row :gutter="8">
            <el-col :span="6"><div class="metric"><label>项目IRR(年)</label><span class="val">{{ ((1+cf.project_irr)**12-1).toFixed(1) }}%</span></div></el-col>
            <el-col :span="6"><div class="metric"><label>权益IRR(年)</label><span class="val">{{ ((1+cf.equity_irr)**12-1).toFixed(1) }}%</span></div></el-col>
            <el-col :span="6"><div class="metric"><label>回正</label><span class="val">{{ cf.payback_month }}个月</span></div></el-col>
            <el-col :span="6"><div class="metric"><label>权益出资</label><span class="val">{{ cf.equity.toFixed(0) }}万</span></div></el-col>
          </el-row>
        </div>
        <div class="result-section">
          <div class="section-hd">成本构成</div>
          <el-row :gutter="8">
            <el-col :span="6"><div class="metric"><label>土地</label><span class="val">{{ r.land_cost.total.toFixed(0) }}万</span></div></el-col>
            <el-col :span="6"><div class="metric"><label>建安</label><span class="val">{{ r.construction.total.toFixed(0) }}万</span></div></el-col>
            <el-col :span="6"><div class="metric"><label>三费</label><span class="val">{{ r.period_fees.total.toFixed(0) }}万</span></div></el-col>
            <el-col :span="6"><div class="metric"><label>税金</label><span class="val">{{ r.taxes.total.toFixed(0) }}万</span></div></el-col>
          </el-row>
        </div>
        <div class="result-section" v-if="r.vat">
          <div class="section-hd">增值税链</div>
          <el-row :gutter="8">
            <el-col :span="6"><div class="metric"><label>销项税</label><span class="val">{{ r.vat.output_vat.toFixed(0) }}万</span></div></el-col>
            <el-col :span="6"><div class="metric"><label>土地抵减</label><span class="val">{{ r.vat.land_deduction.toFixed(0) }}万</span></div></el-col>
            <el-col :span="6"><div class="metric"><label>进项税</label><span class="val">{{ r.vat.input_vat.total.toFixed(0) }}万</span></div></el-col>
            <el-col :span="6"><div class="metric"><label>应交增值税</label><span class="val">{{ r.vat.vat_payable.toFixed(0) }}万</span></div></el-col>
          </el-row>
        </div>
        <div class="result-section" v-if="r.taxes.land_settlement_detail">
          <div class="section-hd">土地增值税清算</div>
          <div v-for="(ty, i) in r.taxes.land_settlement_detail.types" :key="i">
            <div v-if="ty.gfa > 0" class="lat-type">
              <div class="lat-hd">{{ ty.type }}
                <span v-if="ty.products" style="color:#94a3b8;font-size:11px">({{ ty.products.join('/') }})</span>
              </div>
              <el-row :gutter="6">
                <el-col :span="5"><div class="metric-sm"><label>收入(不含税)</label><span>{{ ty.revenue_ex_vat.toFixed(0) }}万</span></div></el-col>
                <el-col :span="5"><div class="metric-sm"><label>扣除合计</label><span>{{ ty.deduction.toFixed(0) }}万</span></div></el-col>
                <el-col :span="5"><div class="metric-sm"><label>增值率</label><span>{{ (ty.excess_ratio*100).toFixed(1) }}%</span></div></el-col>
                <el-col :span="4"><div class="metric-sm"><label>税率</label><span>{{ (ty.rate*100).toFixed(0) }}%</span></div></el-col>
                <el-col :span="5"><div class="metric-sm"><label>应纳税额</label><span class="val">{{ ty.tax.toFixed(0) }}万</span></div></el-col>
              </el-row>
            </div>
          </div>
          <div style="margin-top:8px"><el-row :gutter="6">
            <el-col :span="8"><div class="metric"><label>预征(CF)</label><span>{{ r.taxes.prepay.land_prepay.toFixed(0) }}万</span></div></el-col>
            <el-col :span="8"><div class="metric"><label>清算找差</label><span>{{ r.taxes.land_settlement_diff.toFixed(0) }}万</span></div></el-col>
            <el-col :span="8"><div class="metric"><label>合计(P&L)</label><span class="val">{{ r.taxes.land_appreciation.toFixed(0) }}万</span></div></el-col>
          </el-row></div>
        </div>
        <div class="result-section" v-if="cf.project_cf && cf.project_cf.length">
          <div class="section-hd">现金流曲线</div>
          <div ref="cfChartRef" style="width:100%;height:260px"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api/index.js'
import * as echarts from 'echarts'
export default {
  data() {
    return { loading: true, cfg: null, p: null, result: null, running: false, cfChart: null }
  },
  computed: {
    r() { return this.result || {} },
    pf() { return this.r.profit || {} },
    cf() { return this.r.cashflow || {} },
  },
  async mounted() {
    try {
      this.cfg = await api.getTemplate(this.$route.params.templateId)
      const { meta, ...rest } = this.cfg; this.p = JSON.parse(JSON.stringify(rest))
    } catch (e) { this.$message.error(String(e)) }
    this.loading = false
  },
  methods: {
    pct(v) { return v != null ? (v * 100).toFixed(1) + '%' : '' },
    unpct(v) { return parseFloat(v.replace('%', '')) / 100 },
    fmt0(v) { return Number(v).toLocaleString('zh-CN', {maximumFractionDigits:0}) },
    addProd() {
      this.p.products.push({ name:'', type:'住宅', gfa:10000, saleable_area:9500, unit_price:20000, const_cost_per_sqm:4000, decoration:'毛坯' })
    },
    drawCfChart() {
      this.$nextTick(() => {
        if (this.cfChart) this.cfChart.dispose()
        const el = this.$refs.cfChartRef
        if (!el) return
        this.cfChart = echarts.init(el)
        const months = this.cf.project_cf.map((_, i) => `第${i}月`)
        const project = this.cf.project_cf.map(v => Math.round(v))
        const equity = this.cf.equity_cf ? this.cf.equity_cf.map(v => Math.round(v)) : null
        const series = [{
          name: '项目现金流', type: 'line', data: project,
          smooth: true, lineStyle: { width: 2 }, itemStyle: { color: '#3b82f6' },
          areaStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1, [{offset:0,color:'rgba(59,130,246,0.2)'},{offset:1,color:'rgba(59,130,246,0)'}]) },
        }]
        if (equity) series.push({
          name: '权益现金流', type: 'line', data: equity,
          smooth: true, lineStyle: { width: 2 }, itemStyle: { color: '#10b981' },
        })
        this.cfChart.setOption({
          tooltip: { trigger: 'axis', valueFormatter: v => `${v.toFixed(0)}万` },
          legend: { show: true, bottom: 0 },
          grid: { left: 50, right: 16, top: 16, bottom: 36 },
          xAxis: { type: 'category', data: months, axisLabel: { rotate: 45, fontSize: 9, interval: 2 } },
          yAxis: { type: 'value', axisLabel: { formatter: v => `${v}万` } },
          series,
        })
        this.cfChart.resize()
      })
    },
    async runCalc() {
      this.running = true
      try {
        const params = { ...this.p, meta: this.cfg.meta }
        this.result = await api.calculate(this.$route.params.templateId, params)
        this.drawCfChart()
      } catch (e) { this.$message.error(e.response?.data?.detail || e.message) }
      this.running = false
    },
  },
}
</script>

<style scoped>
.kaifa-layout { display:flex; gap:24px; align-items:flex-start; }
.form-panel { flex:0 0 500px; }
.result-panel { flex:1; }
.form-section { background:#fff; border-radius:10px; padding:16px; margin-bottom:12px; border:1px solid #e2e8f0; }
.section-hd { font-size:14px; font-weight:600; color:#1e293b; margin-bottom:12px; }
.prod-block { background:#f8fafc; border-radius:8px; padding:10px; margin-bottom:6px; }
.prod-hd { font-size:12px; font-weight:600; color:#64748b; margin-bottom:6px; }
label { font-size:10px; color:#64748b; display:block; margin-bottom:2px; }
.calc-btn { width:100%; height:42px; font-size:15px; margin-top:8px; }
.result-section { background:#fff; border-radius:10px; padding:16px; margin-bottom:12px; border:1px solid #e2e8f0; }
.metric { background:#f8fafc; border-radius:8px; padding:10px; text-align:center; }
.metric label { font-size:10px; color:#94a3b8; text-align:center; }
.metric .val { font-size:18px; font-weight:700; display:block; margin-top:2px; }
.metric .val.pos { color:#10b981; }
.metric-sm { background:#f8fafc; border-radius:6px; padding:6px 8px; text-align:center; }
.metric-sm label { font-size:9px; color:#94a3b8; text-align:center; }
.metric-sm span { font-size:13px; font-weight:600; display:block; margin-top:1px; color:#1e293b; }
.metric-sm .val { color:#f59e0b; }
.lat-type { background:#fffbeb; border:1px solid #fde68a; border-radius:8px; padding:10px; margin-bottom:6px; }
.lat-hd { font-size:12px; font-weight:600; color:#92400e; margin-bottom:6px; }
.empty-state { text-align:center; padding:80px; color:#94a3b8; }
</style>
