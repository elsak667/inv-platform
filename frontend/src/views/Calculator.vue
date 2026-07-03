<template>
  <div v-if="loadingTemplate" style="text-align:center;padding:80px 0;color:#999">加载中...</div>
  <div v-else-if="!params" style="text-align:center;padding:80px 0;color:#f00">模板加载失败</div>
  <el-tabs v-model="activeTab" v-else>
    <el-tab-pane label="测算" name="calc">
      <el-row :gutter="20">
        <!-- 左: 参数表单 -->
        <el-col :xs="24" :sm="24" :md="10">
          <el-form label-position="top" size="small">

            <!-- ==================== 一、收购物业 ==================== -->
            <div style="margin-bottom:10px;border:1px solid #e4e7ed;border-radius:6px;padding:10px 12px 6px">
              <div style="font-size:13px;font-weight:600;color:#303133;margin-bottom:8px">一、收购物业</div>
              <div v-for="(u, i) in params.units" :key="i"
                style="margin-bottom:8px;border:1px solid #ebeef5;border-radius:4px;padding:8px;position:relative">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
                  <span style="font-weight:500;font-size:12px;color:#606266">物业 {{ i+1 }}</span>
                  <el-button type="danger" link size="small" @click="params.units.splice(i,1)">删除</el-button>
                </div>
                <el-row :gutter="6">
                  <el-col :span="6"><div style="font-size:10px;color:#999;margin-bottom:1px">项目名称</div><el-input v-model="u.name" placeholder="如：潍坊" size="small" /></el-col>
                  <el-col :span="4"><div style="font-size:10px;color:#999;margin-bottom:1px">套数</div><el-input-number v-model="u.units" :min="1" controls-position="right" style="width:100%" size="small" /></el-col>
                  <el-col :span="5"><div style="font-size:10px;color:#999;margin-bottom:1px">面积（㎡）</div><el-input-number v-model="u.area" :min="1" controls-position="right" style="width:100%" size="small" /></el-col>
                  <el-col :span="4"><div style="font-size:10px;color:#999;margin-bottom:1px">均价（万元/㎡）</div><el-input-number v-model="u.price_per_sqm" :min="0" :precision="2" :step="0.1" controls-position="right" style="width:100%" size="small" /></el-col>
                  <el-col :span="5"><div style="font-size:10px;color:#999;margin-bottom:1px">市场租金（元/㎡/月）</div><el-input-number v-model="u.market_rent" :min="0" controls-position="right" style="width:100%" size="small" /></el-col>
                </el-row>
                <el-row :gutter="6">
                  <el-col :span="6"><div style="font-size:10px;color:#999;margin-bottom:1px">保租房折扣</div>
                    <el-input-number v-model="u.discount" :min="0" :max="1" :step="0.01"
                      :formatter="pct0" :parser="unpct" controls-position="right" style="width:100%" size="small" />
                  </el-col>
                  <el-col :span="6"><div style="font-size:10px;color:#999;margin-bottom:1px">装修成本（元/㎡）</div><el-input-number v-model="u.decoration_cost_per_sqm" :min="0" :step="100" controls-position="right" style="width:100%" size="small" /></el-col>
                  <el-col :span="6">
                    <div style="font-size:10px;color:#999;margin-bottom:1px">折后租金（自动）</div>
                    <div style="line-height:28px;font-size:12px;font-weight:500;color:#409eff;padding-left:4px">
                      {{ (u.market_rent * u.discount).toFixed(1) }}
                    </div>
                  </el-col>
                  <el-col :span="6">
                    <div style="font-size:10px;color:#999;margin-bottom:1px">收购总价（自动）</div>
                    <div style="line-height:28px;font-size:12px;font-weight:500;color:#409eff;padding-left:4px">
                      {{ (u.area * u.price_per_sqm).toFixed(0) }} 万元
                    </div>
                  </el-col>
                </el-row>
              </div>
              <el-button type="primary" link size="small" @click="addUnit" style="margin-bottom:4px">+ 新增物业</el-button>
            </div>

            <!-- ==================== 二、经营预期 ==================== -->
            <div style="margin-bottom:10px;border:1px solid #e4e7ed;border-radius:6px;padding:10px 12px 6px">
              <div style="font-size:13px;font-weight:600;color:#303133;margin-bottom:8px">二、经营预期</div>
              <el-row :gutter="6" style="margin-bottom:6px">
                <el-col :span="8"><div style="font-size:11px;color:#606266;margin-bottom:1px">运营成本占比</div><el-input-number v-model="params.operations.opex_ratio" :min="0" :max="1" :step="0.01" :formatter="pct0" :parser="unpct" controls-position="right" style="width:100%" size="small" /></el-col>
                <el-col :span="8"><div style="font-size:11px;color:#606266;margin-bottom:1px">每次涨幅</div><el-input-number v-model="params.operations.rent_adjust_rate" :min="0" :max="1" :step="0.01" :formatter="pct1" :parser="unpct" controls-position="right" style="width:100%" size="small" /></el-col>
                <el-col :span="8"><div style="font-size:11px;color:#606266;margin-bottom:1px">调租间隔（年）</div><el-input-number v-model="params.operations.rent_adjust_period" :min="1" :max="30" controls-position="right" style="width:100%" size="small" /></el-col>
              </el-row>
              <div style="margin-bottom:6px">
                <div style="font-size:11px;color:#606266;margin-bottom:3px">出租率（每年能租出去几成）</div>
                <el-row :gutter="6" style="margin-bottom:2px">
                  <el-col :span="4"><div style="font-size:10px;color:#999;text-align:center">第1年</div></el-col>
                  <el-col :span="4"><div style="font-size:10px;color:#999;text-align:center">第2年</div></el-col>
                  <el-col :span="4"><div style="font-size:10px;color:#999;text-align:center">第3年</div></el-col>
                  <el-col :span="4"><div style="font-size:10px;color:#999;text-align:center">第4年起</div></el-col>
                </el-row>
                <el-row :gutter="6">
                  <el-col :span="4"><el-input-number v-model="params.operations.occupancy_schedule.year_1" :min="0" :max="1" :step="0.05" :formatter="pct0" :parser="unpct" controls-position="right" size="small" style="width:100%" /></el-col>
                  <el-col :span="4"><el-input-number v-model="params.operations.occupancy_schedule.year_2" :min="0" :max="1" :step="0.05" :formatter="pct0" :parser="unpct" controls-position="right" size="small" style="width:100%" /></el-col>
                  <el-col :span="4"><el-input-number v-model="params.operations.occupancy_schedule.year_3" :min="0" :max="1" :step="0.05" :formatter="pct0" :parser="unpct" controls-position="right" size="small" style="width:100%" /></el-col>
                  <el-col :span="4"><el-input-number v-model="params.operations.occupancy_schedule.year_4" :min="0" :max="1" :step="0.05" :formatter="pct0" :parser="unpct" controls-position="right" size="small" style="width:100%" /></el-col>
                </el-row>
              </div>
            </div>

            <!-- ==================== 三、税费设定 ==================== -->
            <div style="margin-bottom:10px;border:1px solid #e4e7ed;border-radius:6px;padding:10px 12px 6px">
              <div style="font-size:13px;font-weight:600;color:#303133;margin-bottom:8px">三、税费设定</div>
              <el-row :gutter="6" style="margin-bottom:6px">
                <el-col :span="6"><div style="font-size:11px;color:#606266;margin-bottom:1px">契税</div><el-input-number v-model="params.taxes.deed_tax_rate" :min="0" :max="1" :step="0.001" :formatter="pct2" :parser="unpct" controls-position="right" style="width:100%" size="small" /></el-col>
                <el-col :span="6"><div style="font-size:11px;color:#606266;margin-bottom:1px">交易印花税</div><el-input-number v-model="params.taxes.transaction_stamp_rate" :min="0" :max="1" :step="0.0001" :formatter="pct2" :parser="unpct" controls-position="right" style="width:100%" size="small" /></el-col>
                <el-col :span="6"><div style="font-size:11px;color:#606266;margin-bottom:1px">增值税及附加</div><el-input-number v-model="params.taxes.vat_rate" :min="0" :max="1" :step="0.001" :formatter="pct2" :parser="unpct" controls-position="right" style="width:100%" size="small" /></el-col>
                <el-col :span="6"><div style="font-size:11px;color:#606266;margin-bottom:1px">租赁印花税</div><el-input-number v-model="params.taxes.rent_stamp_rate" :min="0" :max="1" :step="0.0001" :formatter="pct2" :parser="unpct" controls-position="right" style="width:100%" size="small" /></el-col>
              </el-row>
              <el-row :gutter="6" style="margin-bottom:6px">
                <el-col :span="4"><div style="font-size:11px;color:#606266;margin-bottom:1px">房产税(从租)</div><el-input-number v-model="params.taxes.property_tax_lease" :min="0" :max="1" :step="0.001" :formatter="pct2" :parser="unpct" controls-position="right" style="width:100%" size="small" /></el-col>
                <el-col :span="4"><div style="font-size:11px;color:#606266;margin-bottom:1px">房产税(从价)</div><el-input-number v-model="params.taxes.property_tax_value" :min="0" :max="1" :step="0.0001" :formatter="pct2" :parser="unpct" controls-position="right" style="width:100%" size="small" /></el-col>
                <el-col :span="4"><div style="font-size:11px;color:#606266;margin-bottom:1px">借款印花税</div><el-input-number v-model="params.taxes.loan_stamp_rate" :min="0" :max="1" :step="0.00001" :formatter="pct2" :parser="unpct" controls-position="right" style="width:100%" size="small" /></el-col>
                <el-col :span="6"><div style="font-size:11px;color:#606266;margin-bottom:1px">土地使用税(元/㎡)</div><el-input-number v-model="params.taxes.land_tax_per_sqm" :min="0" controls-position="right" style="width:100%" size="small" /></el-col>
                <el-col :span="6"><div style="font-size:11px;color:#606266;margin-bottom:1px">占地面积(㎡)</div><el-input-number v-model="params.taxes.land_area" :min="0" controls-position="right" style="width:100%" size="small" /></el-col>
              </el-row>
            </div>

            <!-- ==================== 四、融资方案 ==================== -->
            <div style="margin-bottom:10px;border:1px solid #e4e7ed;border-radius:6px;padding:10px 12px 6px">
              <div style="font-size:13px;font-weight:600;color:#303133;margin-bottom:8px">四、融资方案</div>
              <div v-for="(p, i) in params.loan_plans" :key="i" style="margin-bottom:8px;border:1px solid #ebeef5;border-radius:4px;padding:8px">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
                  <span style="font-size:12px;font-weight:500;color:#606266">方案 {{ i+1 }}：{{ p.id || '(未命名)' }}</span>
                  <el-button type="danger" link size="small" @click="params.loan_plans.splice(i,1)">删除</el-button>
                </div>
                <el-row :gutter="6" style="margin-bottom:2px">
                  <el-col :span="5"><div style="font-size:10px;color:#999">方案名称</div></el-col>
                  <el-col :span="5"><div style="font-size:10px;color:#999">年利率</div></el-col>
                  <el-col :span="5"><div style="font-size:10px;color:#999">贷款比例</div></el-col>
                  <el-col :span="4"><div style="font-size:10px;color:#999">贷款年限</div></el-col>
                  <el-col :span="5"><div style="font-size:10px;color:#999">自动推算</div></el-col>
                </el-row>
                <el-row :gutter="6">
                  <el-col :span="5"><el-input v-model="p.id" placeholder="如：3+3年" size="small" /></el-col>
                  <el-col :span="5"><el-input-number v-model="p.rate" :min="0" :max="1" :step="0.001" :formatter="pct2" :parser="unpct" controls-position="right" style="width:100%" size="small" /></el-col>
                  <el-col :span="5"><el-input-number v-model="p.loan_ratio" :min="0" :max="1" :step="0.01" :formatter="pct0" :parser="unpct" controls-position="right" style="width:100%" size="small" /></el-col>
                  <el-col :span="4"><el-input-number v-model="p.holding_years" :min="1" controls-position="right" style="width:100%" size="small" /></el-col>
                  <el-col :span="5">
                    <div style="line-height:28px;font-size:11px;color:#409eff;padding-left:4px">
                      贷{{ (p.loan_ratio * 100).toFixed(0) }}% · 年{{ pct2(p.rate) }}
                    </div>
                  </el-col>
                </el-row>
                <!-- 还款节奏 -->
                <el-row :gutter="6" style="margin-top:6px">
                  <el-col :span="24">
                    <div style="font-size:10px;color:#999;margin-bottom:2px">还款节奏</div>
                    <el-radio-group v-model="p.repayment_type" size="small" @change="onRepaymentTypeChange(p)">
                      <el-radio-button label="custom">手填</el-radio-button>
                      <el-radio-button label="bullet">到期一次还本</el-radio-button>
                      <el-radio-button label="equal_principal">等额本金</el-radio-button>
                      <el-radio-button label="stepped">等额递增</el-radio-button>
                    </el-radio-group>
                  </el-col>
                </el-row>
                <!-- 手填模式: 逐年还本额 -->
                <el-row v-if="p.repayment_type === 'custom'" :gutter="6" style="margin-top:6px">
                  <el-col :span="24">
                    <div style="font-size:10px;color:#999;margin-bottom:2px">逐年还本额（万元，-1=还清剩余，第1年固定0）</div>
                    <div style="display:flex;flex-wrap:wrap;gap:4px">
                      <div v-for="y in p.holding_years" :key="'rep'+y" style="display:flex;align-items:center;gap:2px">
                        <span style="font-size:10px;color:#999;width:32px">Y{{y}}</span>
                        <el-input-number v-model="p.repayment_schedule['year_' + y]" :min="-1" :step="10" size="small" controls-position="right" style="width:90px" :disabled="y === 1 || y === p.holding_years" />
                      </div>
                    </div>
                    <div style="font-size:10px;color:#bbb;margin-top:2px">第1年=0（只付息）· 末年=-1（自动还清剩余）</div>
                  </el-col>
                </el-row>
                <!-- 等额递增: 起始额+增量 -->
                <el-row v-if="p.repayment_type === 'stepped'" :gutter="6" style="margin-top:6px">
                  <el-col :span="12">
                    <div style="font-size:10px;color:#999">第2年还本（万元）</div>
                    <el-input-number v-model="p.repayment_start" :min="0" :step="10" size="small" controls-position="right" style="width:100%" />
                  </el-col>
                  <el-col :span="12">
                    <div style="font-size:10px;color:#999">每年增量（万元）</div>
                    <el-input-number v-model="p.repayment_increment" :step="10" size="small" controls-position="right" style="width:100%" />
                  </el-col>
                </el-row>
              </div>
              <el-button type="primary" link size="small" @click="addPlan" style="margin-bottom:4px">+ 新增方案</el-button>
            </div>

            <!-- 测算按钮 -->
            <el-button type="primary" @click="runCalc" :loading="loading" style="width:100%;height:40px;font-size:15px;margin-bottom:20px">开始测算</el-button>
          </el-form>
        </el-col>

        <!-- 右: 结果 -->
        <el-col :xs="24" :sm="24" :md="14">
          <div v-if="!result" style="text-align:center;padding:80px 20px;background:#fff;border-radius:8px;border:1px solid #ebeef5">
            <div style="font-size:40px;color:#dcdfe6;margin-bottom:12px">📊</div>
            <p style="color:#909399;font-size:14px;margin:0">填写左边的参数，点击「开始测算」查看结果</p>
          </div>

          <div v-else>
            <!-- 方案对比卡片 -->
            <el-card shadow="never" style="margin-bottom:16px">
              <template #header><span style="font-weight:600;font-size:14px">方案对比</span></template>
              <el-row :gutter="12">
                <el-col v-for="p in result.plans" :key="p.plan" :span="24 / result.plans.length">
                  <el-card :shadow="selectedPlan === p.plan ? 'always' : 'hover'"
                    :style="selectedPlan === p.plan ? 'border:2px solid #409eff;cursor:pointer' : 'cursor:pointer'"
                    @click="selectedPlan = p.plan; $nextTick(drawChart)">
                    <h4 style="margin:0 0 10px;font-size:14px;color:#409eff;text-align:center">{{ p.plan }}</h4>
                    <el-row :gutter="8">
                      <el-col :span="12" style="text-align:center">
                        <div style="font-size:11px;color:#999">项目毛利</div>
                        <div :style="'font-size:18px;font-weight:700;' + (Number(p.project_gross_profit) >= 0 ? 'color:#67c23a' : 'color:#f56c6c')">
                          {{ fmt0(p.project_gross_profit) }}
                          <span style="font-size:11px;font-weight:400;color:#999">万</span>
                        </div>
                      </el-col>
                      <el-col :span="12" style="text-align:center">
                        <div style="font-size:11px;color:#999">现金流结余</div>
                        <div :style="'font-size:18px;font-weight:700;' + (Number(p.cash_flow_total) >= 0 ? 'color:#67c23a' : 'color:#f56c6c')">
                          {{ fmt0(p.cash_flow_total) }}
                          <span style="font-size:11px;font-weight:400;color:#999">万</span>
                        </div>
                      </el-col>
                    </el-row>
                  </el-card>
                </el-col>
              </el-row>
            </el-card>

            <!-- 现金流走势图 -->
            <el-card shadow="never" style="margin-bottom:16px">
              <template #header>
                <span style="font-weight:600;font-size:14px">现金流走势</span>
                <span style="font-size:12px;color:#999;margin-left:8px">{{ selectedPlan }}</span>
              </template>
              <div ref="chartEl" style="height:300px"></div>
            </el-card>

            <!-- 逐年明细表 -->
            <el-card shadow="never" style="margin-bottom:16px">
              <template #header>
                <div style="display:flex;align-items:center;gap:12px">
                  <span style="font-weight:600;font-size:14px">逐年明细</span>
                  <el-select v-model="selectedPlan" size="small" style="width:200px" @change="drawChart">
                    <el-option v-for="p in result.plans" :key="p.plan" :label="p.plan" :value="p.plan" />
                  </el-select>
                </div>
              </template>
              <el-table :data="currentPlan.yearly" size="small" border>
                <el-table-column prop="year" label="年份" width="60" align="center" />
                <el-table-column prop="rent_income" label="租金收入" :formatter="fmt" align="right" />
                <el-table-column prop="tax" label="税费" :formatter="fmt" align="right" />
                <el-table-column prop="depreciation" label="折旧" :formatter="fmt" align="right" />
                <el-table-column prop="opex" label="运营成本" :formatter="fmt" align="right" />
                <el-table-column prop="finance_cost" label="财务成本" :formatter="fmt" align="right" />
                <el-table-column prop="operating_profit" label="运营毛利" :formatter="fmt" align="right" />
              </el-table>
            </el-card>

            <!-- 保存 -->
            <el-card shadow="never" style="margin-bottom:24px">
              <div style="display:flex;align-items:center;gap:8px">
                <el-input v-model="saveName" placeholder="给这个方案取个名字" style="width:240px" size="small" />
                <el-button type="success" @click="save" size="small">保存方案</el-button>
              </div>
            </el-card>
          </div>
        </el-col>
      </el-row>
    </el-tab-pane>
  </el-tabs>
</template>

<script>
import * as echarts from 'echarts'
import api from '../api/index.js'

export default {
  data() {
    return {
      activeTab: 'calc',
      params: null,
      result: null,
      loading: false,
      loadingTemplate: true,
      selectedPlan: '',
      saveName: '',
    }
  },
  computed: {
    currentPlan() {
      if (!this.result) return { yearly: [] }
      return this.result.plans.find(p => p.plan === this.selectedPlan) || this.result.plans[0]
    },
  },
  async mounted() {
    try {
      const tpl = await api.getTemplate(this.$route.params.templateId)
      this.params = this.stripMeta(tpl)
    } catch (e) {
      this.$message.error('加载模板失败: ' + (e.response?.data?.detail || e.message))
    }
    this.loadingTemplate = false
  },
  methods: {
    pct0(v) { return v != null ? (v * 100).toFixed(0) + '%' : '' },
    pct1(v) { return v != null ? (v * 100).toFixed(1) + '%' : '' },
    pct2(v) { return v != null ? (v * 100).toFixed(2) + '%' : '' },
    unpct(v) { return parseFloat(v.replace('%', '')) / 100 },
    fmt0(v) { return Number(v).toFixed(0) },
    stripMeta(tpl) { const { meta, ...rest } = tpl; return rest },
    addUnit() {
      this.params.units.push({ name: '', units: 1, area: 1000, price_per_sqm: 5, market_rent: 100, discount: 0.8, decoration_cost_per_sqm: 1500 })
    },
    addPlan() {
      this.params.loan_plans.push({ id: '新方案', holding_years: 5, rate: 0.025, loan_ratio: 0.3, repayment_type: 'bullet', repayment_schedule: {}, repayment_start: 0, repayment_increment: 0 })
    },
    onRepaymentTypeChange(p) {
      if (p.repayment_type === 'custom') {
        if (!p.repayment_schedule || Object.keys(p.repayment_schedule).length === 0) {
          p.repayment_schedule = { year_1: 0 }
          for (let y = 2; y < p.holding_years; y++) p.repayment_schedule['year_' + y] = 0
          p.repayment_schedule['year_' + p.holding_years] = -1
        }
      } else if (p.repayment_type === 'stepped') {
        if (!p.repayment_start) p.repayment_start = 100
        if (!p.repayment_increment) p.repayment_increment = 50
      }
    },
    async runCalc() {
      this.loading = true
      try {
        this.result = await api.calculate(this.$route.params.templateId, this.params)
        this.selectedPlan = this.result.plans[0].plan
        this.$nextTick(() => this.drawChart())
      } catch (e) {
        this.$message.error(e.response?.data?.detail || e.message)
      }
      this.loading = false
    },
    drawChart() {
      if (!this.$refs.chartEl) return
      const chart = echarts.init(this.$refs.chartEl)
      const years = this.currentPlan.yearly.map(y => '第' + y.year + '年')
      chart.setOption({
        tooltip: { trigger: 'axis' },
        legend: { data: ['租金收入', '财务成本', '运营毛利'] },
        xAxis: { data: years },
        yAxis: { type: 'value', name: '万元' },
        series: [
          { name: '租金收入', type: 'bar', data: this.currentPlan.yearly.map(y => y.rent_income),
            label: { show: true, position: 'top', formatter: (p) => p.value.toFixed(0), fontSize: 10, color: '#666' } },
          { name: '财务成本', type: 'bar', data: this.currentPlan.yearly.map(y => y.finance_cost),
            label: { show: true, position: 'top', formatter: (p) => p.value.toFixed(0), fontSize: 10, color: '#666' } },
          { name: '运营毛利', type: 'line', data: this.currentPlan.yearly.map(y => y.operating_profit),
            label: { show: true, formatter: (p) => p.value.toFixed(0), fontSize: 10, color: '#666' } },
        ]
      })
    },
    fmt(row, col, val) { return val != null ? Number(val).toFixed(2) : '-' },
    async save() {
      if (!this.saveName) { this.$message.warning('请输入方案名称'); return }
      await api.saveRecord(this.saveName, this.$route.params.templateId, this.params, this.result)
      this.$message.success('已存档')
      this.saveName = ''
    }
  }
}
</script>
