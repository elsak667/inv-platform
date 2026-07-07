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
          <div class="section-hd">4. 装修 & 折旧摊销</div>
          <el-row :gutter="8">
            <el-col :span="8"><label>初始装修(万元)</label><el-input-number v-model="p.renovation.initial_cost" :min="0" style="width:100%" size="small" /></el-col>
            <el-col :span="8"><label>周期装修(万元)</label><el-input-number v-model="p.renovation.cycle_cost" :min="0" style="width:100%" size="small" /></el-col>
            <el-col :span="8"><label>装修频率(年)</label><el-input-number v-model="p.renovation.cycle_years" :min="1" style="width:100%" size="small" /></el-col>
          </el-row>
          <el-row :gutter="8" style="margin-top:8px">
            <el-col :span="12"><label>房屋折旧年限(年)</label><el-input-number v-model="p.depreciation.building_life" :min="10" :max="70" style="width:100%" size="small" /></el-col>
            <el-col :span="12"><label>装修摊销年限(年)</label><el-input-number v-model="p.depreciation.decoration_life" :min="1" :max="20" style="width:100%" size="small" /></el-col>
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
          <el-divider style="margin:10px 0" />
          <div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center">
            <el-switch v-model="p.tax.vat_enabled" active-text="增值税 9%" inactive-text="增值税(免征)" size="small" />
            <el-switch v-model="p.tax.property_tax_enabled" active-text="房产税 12%" inactive-text="房产税(免征)" size="small" />
            <el-switch v-model="p.tax.surcharge_enabled" active-text="城建附加 12%" inactive-text="城建附加(免征)" size="small" />
            <el-switch v-model="p.tax.stamp_duty_enabled" active-text="印花税 0.1%" inactive-text="印花税(免征)" size="small" />
          </div>
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
            <div class="chart-card full" style="margin-bottom:12px">
              <div class="card-hd">税费明细</div>
              <div style="display:flex;gap:16px;flex-wrap:wrap;font-size:12px">
                <span>所得税: <b>{{ fmt0(result.total_tax) }}万</b></span>
                <span v-if="result.total_vat">增值税: <b>{{ fmt0(result.total_vat) }}万</b></span>
                <span v-if="result.total_property_tax">房产税: <b>{{ fmt0(result.total_property_tax) }}万</b></span>
                <span v-if="result.total_surcharge">城建附加: <b>{{ fmt0(result.total_surcharge) }}万</b></span>
                <span v-if="result.total_stamp_duty">印花税: <b>{{ fmt0(result.total_stamp_duty) }}万</b></span>
                <span v-if="(result.total_vat||0)+(result.total_property_tax||0)+(result.total_surcharge||0)+(result.total_stamp_duty||0) > 0">流转税合计: <b>{{ fmt0((result.total_vat||0)+(result.total_property_tax||0)+(result.total_surcharge||0)+(result.total_stamp_duty||0)) }}万</b></span>
              </div>
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
            <div class="plain-table-wrap" style="max-height:600px;overflow:auto">
              <table class="plain-table">
                <thead><tr>
                  <th>年份</th><th>年</th><th>出租率</th><th>租金(万)</th><th>运营</th><th>利息</th><th>装修</th><th>流转税</th><th>所得税</th><th>还本</th><th class="cf">净现金流</th><th class="cf">累计CF</th>
                </tr></thead>
                <tbody><tr v-for="r in yearlyRows" :key="r.year">
                  <td>{{ r.year }}</td><td>{{ r.cal }}</td><td>{{ r.occ }}</td><td>{{ fmt0(r.rent) }}</td><td>{{ fmt0(r.opex) }}</td><td>{{ fmt0(r.interest) }}</td><td>{{ fmt0(r.decor) }}</td><td>{{ r.tt ? fmt0(r.tt) : '—' }}</td><td>{{ fmt0(r.tax) }}</td><td>{{ fmt0(r.repay) }}</td><td :class="r.cf >= 0 ? 'pos' : 'neg'">{{ fmt0(r.cf) }}</td><td :class="r.cum >= 0 ? 'pos' : 'neg'">{{ fmt0(r.cum) }}</td>
                </tr></tbody>
              </table>
            </div>
          </el-tab-pane>

          <el-tab-pane label="方案对比" name="scenarios">
            <div class="plain-table-wrap" style="margin-bottom:16px">
              <table class="plain-table">
                <thead><tr>
                  <th>方案</th><th>IRR</th><th>回收期</th><th>累计CF(万)</th><th>所得税(万)</th><th>租金(万)</th><th>总利息(万)</th>
                </tr></thead>
                <tbody><tr v-for="s in scenarioRows" :key="s.name">
                  <td>{{ s.name }}</td><td>{{ s.irr }}</td><td>{{ s.payback }}</td><td>{{ s.cum }}</td><td>{{ s.total_tax }}</td><td>{{ s.total_rent }}</td><td>{{ s.total_interest }}</td>
                </tr></tbody>
              </table>
            </div>

            <div class="section-hd" style="margin:20px 0 12px">敏感性分析</div>
            <div class="tornado-config">
              <div class="tornado-row">
                <span class="tornado-label">稳定期出租率</span>
                <span class="tornado-base">{{ pct(p.rental.occupancy_stable) }}</span>
                <label>±</label>
                <el-input-number v-model="tornadoPcts['rental.occupancy_stable']" :min="1" :max="30" size="small" class="tornado-input" controls-position="right" />
                <label>%</label>
              </div>
              <div class="tornado-row">
                <span class="tornado-label">满租月租金</span>
                <span class="tornado-base">{{ fmt0(p.rental.monthly_rent_full) }}万</span>
                <label>±</label>
                <el-input-number v-model="tornadoPcts['rental.monthly_rent_full']" :min="1" :max="30" size="small" class="tornado-input" controls-position="right" />
                <label>%</label>
              </div>
              <div class="tornado-row">
                <span class="tornado-label">运营成本占比</span>
                <span class="tornado-base">{{ pct(p.operating_cost_ratio) }}</span>
                <label>±</label>
                <el-input-number v-model="tornadoPcts['operating_cost_ratio']" :min="1" :max="30" size="small" class="tornado-input" controls-position="right" />
                <label>%</label>
              </div>
              <div class="tornado-row">
                <span class="tornado-label">贷款利率</span>
                <span class="tornado-base">{{ pct(p.loan.rate) }}</span>
                <label>±</label>
                <el-input-number v-model="tornadoPcts['loan.rate']" :min="1" :max="30" size="small" class="tornado-input" controls-position="right" />
                <label>%</label>
              </div>
              <div class="tornado-row">
                <span class="tornado-label">租金涨幅</span>
                <span class="tornado-base">{{ pct(p.rental.growth_rate) }}</span>
                <label>±</label>
                <el-input-number v-model="tornadoPcts['rental.growth_rate']" :min="1" :max="30" size="small" class="tornado-input" controls-position="right" />
                <label>%</label>
              </div>
              <div class="tornado-row">
                <span class="tornado-label">收购总价</span>
                <span class="tornado-base">{{ fmt0(p.acquisition.total_price) }}万</span>
                <label>±</label>
                <el-input-number v-model="tornadoPcts['acquisition.total_price']" :min="1" :max="30" size="small" class="tornado-input" controls-position="right" />
                <label>%</label>
              </div>
              <el-button type="primary" @click="runTornado" :loading="tornadoRunning" size="small" class="tornado-btn">刷新 Tornado</el-button>
            </div>

            <div v-if="tornadoData" class="chart-card full" style="margin-bottom:12px">
              <div class="card-hd">Tornado 图 — 各参数对 IRR 的影响（基准: {{ tornadoBaseIrr }}%）</div>
              <div ref="tornadoChartRef" style="width:100%;height:340px"></div>
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
    return {
      loading: true, cfg: null, p: null,
      result: null, shieldOn: null, shieldOff: null,
      allPlans: null,
      running: false,
      activeTab: 'overview',
      cfChart: null, taxChart: null,
      shieldCache: null,
      tornadoPcts: {
        'rental.occupancy_stable': 10,
        'rental.monthly_rent_full': 10,
        'operating_cost_ratio': 10,
        'loan.rate': 10,
        'rental.growth_rate': 10,
        'acquisition.total_price': 10,
      },
      tornadoData: [],
      tornadoBaseIrr: null,
      tornadoChart: null,
      tornadoRunning: false,
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
        tt: r.turnover_taxes || 0,
        repay: r.loan_principal,
        cf: cumCf[i] - (cumCf[i - 1] || 0),
        cum: cumCf[i] || 0,
      }))
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
    fmtVal(row, col, val) { return this.fmt0(val) },
    async runCalc() {
      this.running = true
      try {
        const params = { ...this.p, meta: this.cfg.meta }
        this.result = await api.calculate('zulin', params)
        this.activeTab = 'overview'
        await this.$nextTick()
        this.drawCfChart()
        this.shieldCache = null
        this.runShieldCompare()
        this.runTornado()
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
        this.shieldCache = { on: onRes, off: offRes }
        if (this.activeTab === 'taxshield') this.drawTaxChart()
      } catch (e) { console.error('税盾对比失败', e) }
    },
    redrawOnTab() {
      this.$nextTick(() => {
        if (this.activeTab === 'overview') this.drawCfChart()
        if (this.activeTab === 'taxshield') {
          if (this.shieldCache) this.drawTaxChart()
          else this.runShieldCompare()
        }
      })
      if (this.activeTab === 'scenarios' && this.tornadoData.length) {
        setTimeout(() => this.drawTornadoChart(), 100)
      }
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
    async runTornado() {
      if (!this.result) return
      this.tornadoRunning = true
      this.tornadoBaseIrr = this.result.irr_pct
      const items = [
        { key: 'rental.occupancy_stable', label: '稳定期出租率' },
        { key: 'rental.monthly_rent_full', label: '满租月租金' },
        { key: 'operating_cost_ratio', label: '运营成本占比' },
        { key: 'loan.rate', label: '贷款利率' },
        { key: 'rental.growth_rate', label: '租金涨幅' },
        { key: 'acquisition.total_price', label: '收购总价' },
      ]
      const results = []
      for (const item of items) {
        const pct = this.tornadoPcts[item.key] || 10
        const baseVal = this._getNested(this.p, item.key)
        if (baseVal == null || baseVal === 0) continue
        try {
          const pLow = JSON.parse(JSON.stringify(this.p))
          this._setNested(pLow, item.key, baseVal * (1 - pct / 100))
          const rLow = await api.calculate('zulin', { ...pLow, meta: this.cfg.meta })
          const pHigh = JSON.parse(JSON.stringify(this.p))
          this._setNested(pHigh, item.key, baseVal * (1 + pct / 100))
          const rHigh = await api.calculate('zulin', { ...pHigh, meta: this.cfg.meta })
          const irrLow = rLow.irr_pct, irrHigh = rHigh.irr_pct
          results.push({ label: item.label, key: item.key, irrLow, irrHigh, range: Math.abs(irrHigh - irrLow) })
        } catch (e) { console.error('Tornado error:', item.key, e) }
      }
      results.sort((a, b) => b.range - a.range)
      this.tornadoData = results
      this.tornadoRunning = false
      this.$nextTick(() => this.drawTornadoChart())
    },
    drawTornadoChart() {
      const el = this.$refs.tornadoChartRef
      if (!el || !this.tornadoData?.length) return
      if (!el.clientHeight) { setTimeout(() => this.drawTornadoChart(), 100); return }
      if (this.tornadoChart) this.tornadoChart.dispose()
      this.tornadoChart = echarts.init(el)
      const base = this.tornadoBaseIrr
      const names = this.tornadoData.map(d => d.label)
      const leftData = this.tornadoData.map(d => {
        const low = Math.min(d.irrLow, d.irrHigh)
        return Math.min(0, +(low - base).toFixed(4))
      })
      const rightData = this.tornadoData.map(d => {
        const high = Math.max(d.irrLow, d.irrHigh)
        return Math.max(0, +(high - base).toFixed(4))
      })
      const chartData = this.tornadoData
      const chartBase = base
      this.tornadoChart.setOption({
        tooltip: {
          trigger: 'axis',
          formatter(params) {
            const p = params[0]
            const d = chartData[p.dataIndex]
            if (!d) return ''
            const low = Math.min(d.irrLow, d.irrHigh)
            const high = Math.max(d.irrLow, d.irrHigh)
            return `${d.label}<br/>IRR 范围: ${low.toFixed(2)}% → ${high.toFixed(2)}%<br/>基准 IRR: ${chartBase.toFixed(2)}%<br/>影响幅度: ${(high - low).toFixed(2)}%`
          }
        },
        legend: { data: ['不利方向', '有利方向'], bottom: 0, textStyle: { fontSize: 11 } },
        grid: { left: 100, right: 80, top: 12, bottom: 48 },
        xAxis: { type: 'value', axisLabel: { formatter: v => (v + chartBase).toFixed(1) + '%' } },
        yAxis: { type: 'category', data: names, axisLabel: { fontSize: 12, fontWeight: 600 } },
        series: [
          { name: '不利方向', type: 'bar', stack: 't', data: leftData, itemStyle: { color: '#f43f5e', borderRadius: [4,0,0,4] } },
          { name: '有利方向', type: 'bar', stack: 't', data: rightData, itemStyle: { color: '#3b82f6', borderRadius: [0,4,4,0] } },
        ],
      })
      this.tornadoChart.resize()
    },
    drawTaxChart() {
      const el = this.$refs.taxChartRef
      const sd = this.shieldCache || {}
      const on = sd.on || this.shieldOn
      const off = sd.off || this.shieldOff
      if (!el || !on?.yearly?.length || el.clientHeight === 0) return
      if (this.taxChart) this.taxChart.dispose()
      this.taxChart = echarts.init(el)
      const years = on.yearly.map(r => r.calendar_year)
      const onTax = on.yearly.map(r => Math.round(r.income_tax))
      const offTax = off?.yearly?.map(r => Math.round(r.income_tax)) || []
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
.plain-table-wrap { overflow-x:auto; border:1px solid #e2e8f0; border-radius:8px; background:#fff; }
.plain-table { width:100%; border-collapse:collapse; font-size:12px; white-space:nowrap; }
.plain-table th { background:#f8fafc; color:#64748b; font-weight:600; padding:8px 10px; text-align:right; border-bottom:1px solid #e2e8f0; }
.plain-table th:first-child { text-align:center; }
.plain-table td { padding:6px 10px; text-align:right; border-bottom:1px solid #f1f5f9; }
.plain-table td:first-child { text-align:center; color:#64748b; }
.plain-table tbody tr:hover { background:#f8fafc; }
.tornado-config { background:#fff; border:1px solid #e2e8f0; border-radius:10px; padding:16px; margin-bottom:12px; display:flex; flex-wrap:wrap; gap:8px; align-items:center; }
.tornado-row { display:flex; align-items:center; gap:4px; background:#f8fafc; border-radius:6px; padding:4px 10px; }
.tornado-label { font-size:12px; font-weight:600; color:#1e293b; white-space:nowrap; }
.tornado-base { font-size:11px; color:#64748b; margin-right:4px; }
.tornado-row label { font-size:11px; color:#94a3b8; margin:0; display:inline; }
.tornado-input { width:68px !important; }
.tornado-btn { margin-left:auto; }
</style>
