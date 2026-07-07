<template>
  <div class="page-container">
    <div v-if="loading">加载中...</div>
    <div v-else-if="!cfg" class="empty-state">模板加载失败</div>
    <div v-else class="zulin-layout">
      <div class="form-panel">
        <div class="form-section">
          <div class="section-hd">1. 收购项目</div>
          <el-row :gutter="8">
            <el-col :span="12"><label>收购总价(万元)</label><el-input-number v-model="p.acquisition.total_price" :min="0" style="width:100%" size="small" /></el-col>
            <el-col :span="12"><label>自有资金比例</label><el-input-number v-model="p.acquisition.equity_ratio" :min="0" :max="1" :step="0.01" :formatter="pct" :parser="unpct" style="width:100%" size="small" /></el-col>
          </el-row>
        </div>
        <div class="form-section">
          <div class="section-hd">2. 租金</div>
          <el-row :gutter="8">
            <el-col :span="12"><label>满租月租金(万元)</label><el-input-number v-model="p.rental.monthly_rent_full" :min="0" :step="10" style="width:100%" size="small" /></el-col>
            <el-col :span="12"><label>稳定期出租率</label><el-input-number v-model="p.rental.occupancy_stable" :min="0" :max="1" :step="0.01" :formatter="pct" :parser="unpct" style="width:100%" size="small" /></el-col>
          </el-row>
          <el-row :gutter="8" style="margin-top:8px">
            <el-col :span="12"><label>调租间隔(年)</label><el-input-number v-model="p.rental.growth_interval" :min="1" style="width:100%" size="small" /></el-col>
            <el-col :span="12"><label>每次涨幅</label><el-input-number v-model="p.rental.growth_rate" :min="0" :max="1" :step="0.01" :formatter="pct" :parser="unpct" style="width:100%" size="small" /></el-col>
          </el-row>
          <el-row :gutter="8" style="margin-top:8px">
            <el-col :span="12"><label>运营成本占比</label><el-input-number v-model="p.operating_cost_ratio" :min="0" :max="1" :step="0.01" :formatter="pct" :parser="unpct" style="width:100%" size="small" /></el-col>
          </el-row>
        </div>
        <div class="form-section">
          <div class="section-hd">3. 爬坡期</div>
          <el-row :gutter="8">
            <el-col :span="8"><label>初始出租率</label><el-input-number v-model="p.ramp_up.start_rate" :min="0" :max="1" :step="0.01" :formatter="pct" :parser="unpct" style="width:100%" size="small" /></el-col>
            <el-col :span="8"><label>结束出租率</label><el-input-number v-model="p.ramp_up.end_rate" :min="0" :max="1" :step="0.01" :formatter="pct" :parser="unpct" style="width:100%" size="small" /></el-col>
            <el-col :span="8"><label>爬坡月数</label><el-input-number v-model="p.ramp_up.months" :min="1" :max="60" style="width:100%" size="small" /></el-col>
          </el-row>
        </div>
        <div class="form-section">
          <div class="section-hd">4. 装修</div>
          <el-row :gutter="8">
            <el-col :span="8"><label>初始装修(万元)</label><el-input-number v-model="p.renovation.initial_cost" :min="0" style="width:100%" size="small" /></el-col>
            <el-col :span="8"><label>周期装修(万元)</label><el-input-number v-model="p.renovation.cycle_cost" :min="0" style="width:100%" size="small" /></el-col>
            <el-col :span="8"><label>装修频率(年)</label><el-input-number v-model="p.renovation.cycle_years" :min="1" style="width:100%" size="small" /></el-col>
          </el-row>
        </div>
        <div class="form-section">
          <div class="section-hd">5. 融资</div>
          <el-row :gutter="8">
            <el-col :span="12"><label>年利率</label><el-input-number v-model="p.loan.rate" :min="0" :max="0.15" :step="0.001" :formatter="pct" :parser="unpct" style="width:100%" size="small" /></el-col>
            <el-col :span="12"><label>贷款期限(年)</label><el-input-number v-model="p.loan.term_years" :min="1" :max="30" style="width:100%" size="small" /></el-col>
          </el-row>
          <el-row :gutter="8" style="margin-top:8px">
            <el-col :span="12"><label>宽限期(年)</label><el-input-number v-model="p.loan.grace_years" :min="0" :max="5" style="width:100%" size="small" /></el-col>
          </el-row>
        </div>
        <div class="form-section">
          <div class="section-hd">6. 税费</div>
          <el-row :gutter="8">
            <el-col :span="12"><label>所得税率</label><el-input-number v-model="p.tax.income_tax_rate" :min="0" :max="0.5" :step="0.01" :formatter="pct" :parser="unpct" style="width:100%" size="small" /></el-col>
            <el-col :span="12"><el-switch v-model="p.tax.tax_shield" active-text="税盾ON" inactive-text="税盾OFF" style="margin-top:18px" /></el-col>
          </el-row>
          <el-row :gutter="8" style="margin-top:8px">
            <el-col :span="12"><el-checkbox v-model="p.tax.loss_carryforward">亏损结转</el-checkbox></el-col>
          </el-row>
        </div>
        <el-button type="primary" @click="runCalc" :loading="running" class="calc-btn">开始测算</el-button>
      </div>

      <div class="result-panel" v-if="result">
        <el-tabs v-model="activeTab" class="result-tabs" @tab-change="redrawOnTab">
          <el-tab-pane label="总览" name="overview">
            <div class="metric-grid-4">
              <div class="big-metric"><label>项目IRR</label><span class="big-val">{{ result.irr_pct }}%</span></div>
              <div class="big-metric"><label>静态回收期</label><span class="big-val">{{ result.payback_year || '—' }}年</span></div>
              <div class="big-metric"><label>累计净现金流</label><span class="big-val">{{ fmt0(result.cumulative_cash_flow) }}万</span></div>
              <div class="big-metric"><label>所得税合计</label><span class="big-val">{{ fmt0(result.total_tax) }}万</span></div>
            </div>
            <div class="metric-grid-3">
              <div class="big-metric"><label>租金总收入</label><span class="big-val">{{ fmt0(result.total_rent) }}万</span></div>
              <div class="big-metric"><label>贷款总利息</label><span class="big-val">{{ fmt0(result.total_interest) }}万</span></div>
              <div class="big-metric"><label>装修总投入</label><span class="big-val">{{ fmt0(result.total_renovation) }}万</span></div>
            </div>
            <div class="chart-row">
              <div class="chart-card full">
                <div class="card-hd">现金流曲线</div>
                <div ref="cfChartRef" style="width:100%;height:280px"></div>
              </div>
            </div>
            <div class="conclusion-card" v-if="result">
              <div class="card-hd">测算结论</div>
              <div class="conclusion-text">项目期待IRR <b>{{ result.irr_pct }}%</b>，静态回收期 <b>{{ result.payback_year }}年</b>，累计净现金流 <b>{{ fmt0(result.cumulative_cash_flow) }}万元</b>。
              税盾{{ result.tax_shield_enabled ? 'ON' : 'OFF' }}，所得税合计 <b>{{ fmt0(result.total_tax) }}万元</b>，税盾省税 <b>{{ fmt0(result.tax_shield_saving) }}万元</b>。</div>
            </div>
          </el-tab-pane>

          <el-tab-pane label="税盾对比" name="taxshield">
            <div class="metric-grid-2">
              <div class="big-metric"><label>税盾ON · IRR</label><span class="big-val shield-on">{{ shieldOn?.irr_pct }}%</span></div>
              <div class="big-metric"><label>税盾OFF · IRR</label><span class="big-val shield-off">{{ shieldOff?.irr_pct }}%</span></div>
            </div>
            <div class="metric-grid-2">
              <div class="big-metric"><label>税盾ON · 所得税</label><span class="big-val shield-on">{{ fmt0(shieldOn?.total_tax) }}万</span></div>
              <div class="big-metric"><label>税盾OFF · 所得税</label><span class="big-val shield-off">{{ fmt0(shieldOff?.total_tax) }}万</span></div>
            </div>
            <div class="chart-row">
              <div class="chart-card full">
                <div class="card-hd">年度所得税对比（税盾ON vs OFF）</div>
                <div ref="taxChartRef" style="width:100%;height:320px"></div>
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane label="年度现金流" name="cashflow">
            <el-table :data="yearlyRows" border size="small" max-height="600" style="width:100%">
              <el-table-column prop="year" label="年份" width="60" align="center" />
              <el-table-column prop="cal" label="年" width="60" align="center" />
              <el-table-column prop="occ" label="出租率" width="80" align="right" />
              <el-table-column prop="rent" label="租金" align="right" width="110" />
              <el-table-column prop="opex" label="运营" align="right" width="100" />
              <el-table-column prop="interest" label="利息" align="right" width="100" />
              <el-table-column prop="decor" label="装修" align="right" width="100" />
              <el-table-column prop="tax" label="所得税" align="right" width="100" />
              <el-table-column prop="repay" label="还本" align="right" width="100" />
              <el-table-column prop="cf" label="净现金流" align="right" width="120">
                <template #default="{row}"><span :class="row.cf >= 0 ? 'pos' : 'neg'">{{ fmt0(row.cf) }}</span></template>
              </el-table-column>
              <el-table-column prop="cum" label="累计CF" align="right" width="130">
                <template #default="{row}"><span :class="row.cum >= 0 ? 'pos' : 'neg'">{{ fmt0(row.cum) }}</span></template>
              </el-table-column>
            </el-table>
          </el-tab-pane>

          <el-tab-pane label="方案对比" name="scenarios">
            <el-table :data="scenarioRows" border size="small" style="width:100%;margin-bottom:16px">
              <el-table-column prop="name" label="方案" width="120" />
              <el-table-column prop="irr" label="IRR" align="right" width="100" />
              <el-table-column prop="payback" label="回收期" align="right" width="100" />
              <el-table-column prop="cum" label="累计CF(万)" align="right" width="120" />
              <el-table-column prop="total_tax" label="所得税(万)" align="right" width="120" />
              <el-table-column prop="total_rent" label="租金(万)" align="right" width="120" />
              <el-table-column prop="total_interest" label="总利息(万)" align="right" width="120" />
            </el-table>

            <div class="section-hd" style="margin:20px 0 12px">敏感性分析</div>
            <div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:16px;margin-bottom:12px">
              <el-row :gutter="8" style="margin-bottom:8px">
                <el-col :span="6"><label>分析参数</label>
                  <el-select v-model="sensParam" size="small" style="width:100%">
                    <el-option label="稳定期出租率" value="rental.occupancy_stable" />
                    <el-option label="满租月租金(万元)" value="rental.monthly_rent_full" />
                    <el-option label="贷款利率" value="loan.rate" />
                    <el-option label="租金涨幅" value="rental.growth_rate" />
                    <el-option label="运营成本占比" value="operating_cost_ratio" />
                  </el-select>
                </el-col>
                <el-col :span="6"><label>最小值</label><el-input-number v-model="sensMin" :min="0" :step="0.01" size="small" style="width:100%" /></el-col>
                <el-col :span="6"><label>最大值</label><el-input-number v-model="sensMax" :min="0" :step="0.01" size="small" style="width:100%" /></el-col>
                <el-col :span="6"><label>步长</label><el-input-number v-model="sensStep" :min="0.001" :step="0.01" size="small" style="width:100%" /></el-col>
              </el-row>
              <el-row :gutter="8">
                <el-col :span="6"><el-button type="primary" @click="runSensitivity" :loading="sensRunning" size="small">运行</el-button></el-col>
              </el-row>
            </div>

            <div v-if="sensResults.length" class="chart-card full" style="margin-bottom:12px">
              <div class="card-hd">敏感性分析 — IRR vs {{ sensParamLabel }}</div>
              <div ref="sensChartRef" style="width:100%;height:280px"></div>
            </div>
            <el-table v-if="sensResults.length" :data="sensResults" border size="small" style="width:100%">
              <el-table-column prop="param" :label="sensParamLabel" align="right" width="120" />
              <el-table-column prop="irr" label="IRR" align="right" width="100" />
              <el-table-column prop="payback" label="回收期" align="right" width="100" />
              <el-table-column prop="cum" label="累计CF(万)" align="right" width="120" />
              <el-table-column prop="total_tax" label="所得税(万)" align="right" width="120" />
            </el-table>
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
    return {
      loading: true, cfg: null, p: null,
      result: null, shieldOn: null, shieldOff: null,
      allPlans: null,
      running: false,
      activeTab: 'overview',
      cfChart: null, taxChart: null,
      // 敏感性分析
      sensParam: 'rental.occupancy_stable',
      sensMin: 0.7, sensMax: 0.95, sensStep: 0.05,
      sensResults: [],
      sensRunning: false,
      sensChart: null,
    }
  },
  computed: {
    yearlyRows() {
      const y = this.result?.yearly || []
      const cumCf = this.result?.cumulative_cf || []
      const equity = this.p?.acquisition?.total_price * this.p?.acquisition?.equity_ratio || 38400
      return y.map((r, i) => ({
        year: i + 1,
        cal: r.calendar_year,
        occ: (r.occupancy * 100).toFixed(1) + '%',
        rent: r.rent_income,
        opex: r.opex,
        interest: r.loan_interest,
        decor: r.renovation_capex,
        tax: r.income_tax,
        repay: r.loan_principal,
        cf: cumCf[i] - (cumCf[i - 1] || 0),
        cum: cumCf[i] || 0,
      }))
    },
    sensParamLabel() {
      const labels = {
        'rental.occupancy_stable': '出租率',
        'rental.monthly_rent_full': '月租金(万)',
        'loan.rate': '利率',
        'rental.growth_rate': '涨幅',
        'operating_cost_ratio': '运营占比',
      }
      return labels[this.sensParam] || this.sensParam
    },
    scenarioRows() {
      const ps = this.allPlans?.plans || []
      return ps.map(s => ({
        name: s.scenario,
        irr: s.irr_pct + '%',
        payback: (s.payback_year || '—') + '年',
        cum: this.fmt0(s.cumulative_cash_flow),
        total_tax: this.fmt0(s.total_tax),
        total_rent: this.fmt0(s.total_rent),
        total_interest: this.fmt0(s.total_interest),
      }))
    },
  },
  async mounted() {
    try {
      this.cfg = await api.getTemplate('zulin')
      const { meta, scenarios, ...rest } = this.cfg
      this.p = JSON.parse(JSON.stringify(rest))
      await this.runCalc()
      this.fetchScenarios()
    } catch (e) { this.$message.error(String(e)) }
    this.loading = false
  },
  methods: {
    pct(v) { return v != null ? (v * 100).toFixed(1) + '%' : '' },
    unpct(v) { return parseFloat(String(v || '0').replace('%', '')) / 100 },
    fmt0(v) { return Number(v || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) },
    async runCalc() {
      this.running = true
      try {
        const params = { ...this.p, meta: this.cfg.meta }
        this.result = await api.calculate('zulin', params)
        this.activeTab = 'overview'
        await this.$nextTick()
        this.drawCfChart()
        this.runShieldCompare()
      } catch (e) { this.$message.error(e.response?.data?.detail || e.message) }
      this.running = false
    },
    async fetchScenarios() {
      try {
        const params = { ...this.p, meta: this.cfg.meta, scenarios: this.cfg.scenarios }
        this.allPlans = await api.calculate('zulin', params)
      } catch (e) { console.error('方案对比失败', e) }
    },
    async runShieldCompare() {
      try {
        const onP = { ...JSON.parse(JSON.stringify(this.p)), tax: { ...this.p.tax, tax_shield: true } }
        const offP = { ...JSON.parse(JSON.stringify(this.p)), tax: { ...this.p.tax, tax_shield: false } }
        const [onRes, offRes] = await Promise.all([
          api.calculate('zulin', { ...onP, meta: this.cfg.meta }),
          api.calculate('zulin', { ...offP, meta: this.cfg.meta }),
        ])
        this.shieldOn = onRes
        this.shieldOff = offRes
        this.drawTaxChart()
      } catch (e) { console.error('税盾对比失败', e) }
    },
    redrawOnTab() {
      this.$nextTick(() => {
        if (this.activeTab === 'overview') this.drawCfChart()
        if (this.activeTab === 'taxshield') this.drawTaxChart()
      })
    },
    drawCfChart() {
      const el = this.$refs.cfChartRef
      if (!el || !this.result?.cumulative_cf?.length) return
      if (this.cfChart) this.cfChart.dispose()
      this.cfChart = echarts.init(el)
      const years = this.result.yearly.map(r => r.calendar_year)
      const cf = this.result.cumulative_cf
      const pb = this.result.payback_year
      this.cfChart.setOption({
        tooltip: { trigger: 'axis', valueFormatter: v => v != null ? this.fmt0(v) + '万' : '' },
        grid: { left: 64, right: 24, top: 24, bottom: 36 },
        xAxis: { type: 'category', data: years, axisLabel: { rotate: 45, fontSize: 10 } },
        yAxis: { type: 'value', axisLabel: { formatter: v => this.fmt0(v) } },
        series: [{
          type: 'line', data: cf, smooth: true, lineStyle: { width: 2, color: '#3b82f6' },
          areaStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(59,130,246,0.2)'},{offset:1,color:'rgba(59,130,246,0)'}]) },
          markLine: pb ? { symbol: 'none', lineStyle: { type: 'dashed', color: '#10b981', width: 2 }, data: [{ xAxis: pb - 1, label: { formatter: `回收期: ${pb}年`, position: 'end', color: '#10b981', fontSize: 12 } }] } : undefined,
        }],
      })
      this.cfChart.resize()
    },
    _setNested(obj, path, val) {
      const parts = path.split('.')
      let cur = obj
      for (let i = 0; i < parts.length - 1; i++) cur = cur[parts[i]]
      cur[parts[parts.length - 1]] = val
    },
    _getNested(obj, path) {
      return path.split('.').reduce((o, k) => (o || {})[k], obj)
    },
    async runSensitivity() {
      this.sensRunning = true
      const results = []
      for (let v = this.sensMin; v <= this.sensMax + this.sensStep * 0.5; v += this.sensStep) {
        const p = JSON.parse(JSON.stringify(this.p))
        this._setNested(p, this.sensParam, v)
        try {
          const r = await api.calculate('zulin', { ...p, meta: this.cfg.meta })
          results.push({ param: v, irr: r.irr_pct + '%', payback: (r.payback_year || '—') + '年', cum: this.fmt0(r.cumulative_cash_flow), total_tax: this.fmt0(r.total_tax), _irr: r.irr_pct, _param: v })
        } catch (e) { console.error('敏感性分析失败', e) }
      }
      this.sensResults = results
      this.sensRunning = false
      this.$nextTick(() => this.drawSensChart())
    },
    drawSensChart() {
      const el = this.$refs.sensChartRef
      if (!el || !this.sensResults.length) return
      if (this.sensChart) this.sensChart.dispose()
      this.sensChart = echarts.init(el)
      this.sensChart.setOption({
        tooltip: { trigger: 'axis', valueFormatter: v => v != null ? v + '%' : '' },
        grid: { left: 60, right: 24, top: 24, bottom: 36 },
        xAxis: { type: 'category', data: this.sensResults.map(r => r._param), axisLabel: { rotate: 45, fontSize: 10 } },
        yAxis: { type: 'value', axisLabel: { formatter: '{value}%' } },
        series: [{ type: 'line', data: this.sensResults.map(r => r._irr), smooth: true, lineStyle: { width: 2, color: '#8b5cf6' }, markLine: { symbol: 'none', lineStyle: { type: 'dashed', color: '#94a3b8' }, data: [{ yAxis: this.result?.irr_pct || 5.5, label: { formatter: `基准: ${this.result?.irr_pct || 5.5}%`, position: 'insideEndTop', color: '#94a3b8', fontSize: 11 } }] } }],
      })
      this.sensChart.resize()
    },
    drawTaxChart() {
      const el = this.$refs.taxChartRef
      if (!el || !this.shieldOn?.yearly?.length) return
      if (this.taxChart) this.taxChart.dispose()
      this.taxChart = echarts.init(el)
      const years = this.shieldOn.yearly.map(r => r.calendar_year)
      const onTax = this.shieldOn.yearly.map(r => Math.round(r.income_tax))
      const offTax = this.shieldOff?.yearly?.map(r => Math.round(r.income_tax)) || []
      this.taxChart.setOption({
        tooltip: { trigger: 'axis', valueFormatter: v => v != null ? this.fmt0(v) + '万' : '' },
        legend: { data: ['税盾ON 所得税', '税盾OFF 所得税'], bottom: 0, textStyle: { fontSize: 11 } },
        grid: { left: 64, right: 24, top: 24, bottom: 48 },
        xAxis: { type: 'category', data: years, axisLabel: { rotate: 45, fontSize: 10 } },
        yAxis: { type: 'value', axisLabel: { formatter: v => this.fmt0(v) } },
        series: [
          { name: '税盾ON 所得税', type: 'bar', data: onTax, itemStyle: { color: '#3b82f6' }, barGap: '10%' },
          { name: '税盾OFF 所得税', type: 'bar', data: offTax, itemStyle: { color: '#f59e0b' } },
        ],
      })
      this.taxChart.resize()
    },
  },
}
</script>

<style scoped>
.zulin-layout { display:flex; gap:24px; align-items:flex-start; }
.form-panel { flex:0 0 460px; }
.result-panel { flex:1; min-width:0; }
.form-section { background:#fff; border-radius:10px; padding:16px; margin-bottom:12px; border:1px solid #e2e8f0; }
.section-hd { font-size:14px; font-weight:600; color:#1e293b; margin-bottom:12px; }
label { font-size:10px; color:#64748b; display:block; margin-bottom:2px; }
.calc-btn { width:100%; height:42px; font-size:15px; margin-top:8px; }
.metric-grid-4 { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:12px; }
.metric-grid-3 { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-bottom:12px; }
.metric-grid-2 { display:grid; grid-template-columns:repeat(2,1fr); gap:12px; margin-bottom:12px; }
.big-metric { background:#fff; border:1px solid #e2e8f0; border-radius:10px; padding:16px; text-align:center; }
.big-metric label { font-size:11px; color:#94a3b8; }
.big-val { font-size:22px; font-weight:700; display:block; margin-top:4px; color:#1e293b; }
.big-val.shield-on { color:#3b82f6; }
.big-val.shield-off { color:#f59e0b; }
.chart-row { margin-bottom:12px; }
.chart-card { background:#fff; border:1px solid #e2e8f0; border-radius:10px; padding:12px; }
.chart-card.full { width:100%; }
.card-hd { font-size:13px; font-weight:600; color:#1e293b; margin-bottom:8px; }
.conclusion-card { background:#f0fdf4; border:1px solid #bbf7d0; border-radius:10px; padding:16px; margin-top:12px; }
.conclusion-text { font-size:13px; color:#1e293b; line-height:1.7; }
.result-tabs :deep(.el-tabs__header) { margin-bottom:12px; }
.result-tabs :deep(.el-tabs__item) { font-size:14px; font-weight:500; }
.pos { color:#10b981; font-weight:600; }
.neg { color:#ef4444; font-weight:600; }
.empty-state { text-align:center; padding:80px; color:#94a3b8; }
</style>
