<template>
  <div v-if="loadingTemplate" style="text-align:center;padding:80px 0;color:#999">加载中...</div>
  <div v-else-if="!params" style="text-align:center;padding:80px 0;color:#f00">模板加载失败</div>
  <el-tabs v-model="activeTab" v-else>
    <el-tab-pane label="测算" name="calc">
      <el-row :gutter="20">
        <!-- 左: 参数表单 -->
        <el-col :xs="24" :sm="24" :md="10">
          <el-form label-position="top" size="small">

            <!-- ==================== 一、收购项目 ==================== -->
            <div style="margin-bottom:10px;border:1px solid #e4e7ed;border-radius:6px;padding:10px 12px 6px">
              <div style="font-size:13px;font-weight:600;color:#303133;margin-bottom:8px">一、收购项目</div>
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
                  <el-col :span="6"><div style="font-size:10px;color:#999;margin-bottom:1px">租金折扣</div>
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
              <el-row :gutter="6" style="margin-top:6px">
                <el-col :span="6" :offset="18"><div style="font-size:11px;color:#606266;margin-bottom:1px">出售收回总额（万元）</div><el-input-number v-model="params.sale.revenue" :min="0" controls-position="right" style="width:100%" size="small" /></el-col>
              </el-row>
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

            <!-- ==================== 四、会计估计 ==================== -->
            <div style="margin-bottom:10px;border:1px solid #e4e7ed;border-radius:6px;padding:10px 12px 6px">
              <div style="font-size:13px;font-weight:600;color:#303133;margin-bottom:8px">四、会计估计</div>
              <el-row :gutter="6" style="margin-bottom:6px">
                <el-col :span="8"><div style="font-size:11px;color:#606266;margin-bottom:1px">房屋折旧年限</div><el-input-number v-model="params.depreciation.building_life" :min="1" :max="60" controls-position="right" style="width:100%" size="small" /></el-col>
                <el-col :span="6"><div style="font-size:11px;color:#606266;margin-bottom:1px">残值率</div><el-input-number v-model="params.depreciation.residual_ratio" :min="0" :max="0.5" :step="0.01" :formatter="pct0" :parser="unpct" controls-position="right" style="width:100%" size="small" /></el-col>
                <el-col :span="8"><div style="font-size:11px;color:#606266;margin-bottom:1px">装修摊销年限</div><el-input-number v-model="params.depreciation.decoration_life" :min="1" :max="30" controls-position="right" style="width:100%" size="small" /></el-col>
              </el-row>
            </div>

            <!-- ==================== 五、融资方案 ==================== -->
            <div style="margin-bottom:10px;border:1px solid #e4e7ed;border-radius:6px;padding:10px 12px 6px">
              <div style="font-size:13px;font-weight:600;color:#303133;margin-bottom:8px">五、融资方案</div>
              <div v-for="(p, i) in params.loan_plans" :key="i" style="margin-bottom:8px;border:1px solid #ebeef5;border-radius:4px;padding:8px">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
                  <span style="font-size:12px;font-weight:500;color:#606266">方案 {{ i+1 }}：{{ p.id || '(未命名)' }}</span>
                  <el-button type="danger" link size="small" @click="params.loan_plans.splice(i,1)">删除</el-button>
                </div>
                <el-row :gutter="6" style="margin-bottom:2px">
                  <el-col :span="6"><div style="font-size:10px;color:#999">方案名称</div></el-col>
                  <el-col :span="6"><div style="font-size:10px;color:#999">年利率</div></el-col>
                  <el-col :span="6"><div style="font-size:10px;color:#999">贷款比例</div></el-col>
                  <el-col :span="6"><div style="font-size:10px;color:#999">贷款年限</div></el-col>
                </el-row>
                <el-row :gutter="6">
                  <el-col :span="6"><el-input v-model="p.id" placeholder="如：3+3年" size="small" /></el-col>
                  <el-col :span="6"><el-input-number v-model="p.rate" :min="0" :max="1" :step="0.001" :formatter="pct2" :parser="unpct" controls-position="right" style="width:100%" size="small" /></el-col>
                  <el-col :span="6"><el-input-number v-model="p.loan_ratio" :min="0" :max="1" :step="0.01" :formatter="pct0" :parser="unpct" controls-position="right" style="width:100%" size="small" /></el-col>
                  <el-col :span="6"><el-input-number v-model="p.holding_years" :min="1" @change="onHoldingYearsChange(p)" controls-position="right" style="width:100%" size="small" /></el-col>
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
                    <div style="font-size:10px;color:#999;margin-bottom:2px">逐年还本额（万元，-1=还清剩余，第1年默认0只付息）</div>
                    <div style="display:flex;flex-wrap:wrap;gap:4px">
                      <div v-for="y in p.holding_years" :key="'rep'+y" style="display:flex;align-items:center;gap:2px">
                        <span style="font-size:10px;color:#999;width:32px">Y{{y}}</span>
                        <el-input-number v-model="p.repayment_schedule['year_' + y]" :min="-1" :step="10" size="small" controls-position="right" style="width:90px" />
                      </div>
                    </div>
                    <div style="font-size:10px;color:#bbb;margin-top:2px">第1年默认0（只付息）· 末年默认-1（还清剩余）· 均可修改</div>
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
                      <el-col :span="12">
                        <div style="font-size:11px;color:#999;text-align:center">项目毛利</div>
                        <div style="text-align:center;font-size:18px;font-weight:700;color:#67c23a">
                          {{ fmt0(p.project_gross_profit) }}<span style="font-size:11px;font-weight:400;color:#999">万</span>
                        </div>
                        <div style="font-size:10px;color:#999;text-align:center;margin-top:2px">
                          运营毛利 {{ fmt0(p.operating_profit_total) }} + 出售毛利 {{ fmt0(p.sale_profit) }}
                        </div>
                        <div style="font-size:10px;color:#bbb;text-align:center">出售毛利 = 累计折旧 {{ fmt0(p.cumulative_depreciation) }}</div>
                      </el-col>
                      <el-col :span="12">
                        <div style="font-size:11px;color:#999;text-align:center">现金流结余</div>
                        <div style="text-align:center;font-size:18px;font-weight:700;color:#67c23a">
                          {{ fmt0(p.cash_flow_total) }}<span style="font-size:11px;font-weight:400;color:#999">万</span>
                        </div>
                        <div style="font-size:10px;color:#999;text-align:center;margin-top:2px">
                          持有期收支 {{ fmt0(p.cash_flow_total - p.sale_revenue) }} + 出售 {{ fmt0(p.sale_revenue) }}
                        </div>
                        <div style="font-size:10px;color:#bbb;text-align:center">持有期收支包含租金·还本·利息·税费·资本金</div>
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
              <el-table :data="currentPlan.yearly" size="small" border show-summary :summary-method="getSummaries">
                <el-table-column prop="year" label="年份" width="60" align="center" />
                <el-table-column prop="rent_income" label="租金收入" :formatter="fmt" align="right" />
                <el-table-column prop="tax" label="税费" :formatter="fmt" align="right" />
                <el-table-column prop="depreciation" label="折旧" :formatter="fmt" align="right" />
                <el-table-column prop="opex" label="运营成本" :formatter="fmt" align="right" />
                <el-table-column prop="finance_cost" label="财务成本" :formatter="fmt" align="right" />
                <el-table-column prop="operating_profit" label="运营毛利" :formatter="fmt" align="right" />
                <el-table-column prop="sale_revenue" label="出售收回" :formatter="fmt" align="right" />
                <el-table-column prop="loan_balance" label="贷款余额" :formatter="fmt" align="right" />
              </el-table>
            </el-card>

            <!-- 分析报告 -->
            <el-card shadow="never" style="margin-bottom:16px">
              <template #header>
                <div style="display:flex;align-items:center;gap:12px">
                  <span style="font-weight:600;font-size:14px">分析报告</span>
                  <el-switch v-model="reportAiMode" active-text="AI增强" inactive-text="标准" size="small" style="margin-right:4px" />
                  <el-button type="primary" size="small" @click="doGenerateReport" :loading="reportLoading">生成报告</el-button>
                  <el-button v-if="reportMd" size="small" @click="copyReport">复制</el-button>
                  <el-button v-if="reportMd" size="small" @click="downloadReport">下载</el-button>
                  <el-button v-if="reportOutline" size="small" @click="downloadOutline">下载PPT大纲</el-button>
                </div>
              </template>
              <div v-if="reportMd" style="max-height:600px;overflow:auto;background:#f8f9fa;border-radius:4px;padding:16px;font-size:13px;line-height:1.7;white-space:pre-wrap;font-family:monospace">{{ reportMd }}</div>
              <div v-if="!reportMd" style="color:#999;font-size:13px;text-align:center;padding:20px">点击"生成报告"按钮，基于当前测算结果自动生成分析报告和PPT大纲。</div>
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
      reportLoading: false,
      reportMd: '',
      reportOutline: '',
      reportAiMode: false,
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
    fmt0(v) { return Number(v).toFixed(2) },
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
          p.repayment_schedule = {}
          for (let y = 1; y <= p.holding_years; y++) {
            p.repayment_schedule['year_' + y] = (y === 1) ? 0 : (y === p.holding_years ? -1 : 0)
          }
        }
      } else if (p.repayment_type === 'stepped') {
        if (!p.repayment_start) p.repayment_start = 100
        if (!p.repayment_increment) p.repayment_increment = 50
      }
    },
    onHoldingYearsChange(p) {
      // 贷款年限变了, 末年始终=-1(还清剩余), 保留已填年份的值
      if (p.repayment_type === 'custom') {
        const old = { ...(p.repayment_schedule || {}) }
        p.repayment_schedule = {}
        for (let y = 1; y <= p.holding_years; y++) {
          if (y === p.holding_years) p.repayment_schedule['year_' + y] = -1
          else if (old['year_' + y] != null) p.repayment_schedule['year_' + y] = old['year_' + y]
          else p.repayment_schedule['year_' + y] = (y === 1) ? 0 : 0
        }
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
    async doGenerateReport() {
      this.reportLoading = true
      try {
        const r = await api.generateReport(this.$route.params.templateId, this.params, this.reportAiMode ? 'llm' : 'template')
        this.reportMd = r.markdown
        this.reportOutline = r.outline
      } catch (e) {
        this.$message.error('生成报告失败: ' + (e.response?.data?.detail || e.message))
      }
      this.reportLoading = false
    },
    copyReport() {
      navigator.clipboard.writeText(this.reportMd).then(() => this.$message.success('已复制'))
    },
    downloadReport() {
      const blob = new Blob([this.reportMd], { type: 'text/markdown;charset=utf-8' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a'); a.href = url; a.download = '分析报告.md'; a.click()
      URL.revokeObjectURL(url)
    },
    downloadOutline() {
      const blob = new Blob([this.reportOutline], { type: 'text/markdown;charset=utf-8' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a'); a.href = url; a.download = 'PPT大纲.md'; a.click()
      URL.revokeObjectURL(url)
    },
    drawChart() {
      if (!this.$refs.chartEl) return
      const chart = echarts.init(this.$refs.chartEl)
      const yd = this.currentPlan.yearly
      const years = yd.map(y => '第' + y.year + '年')
      const eq = this.currentPlan.equity
      const dt = this.currentPlan.deed_tax
      const cum = (() => {
        let c = 0
        return yd.map(y => { c += y.rent_income - y.tax - y.opex - y.finance_cost - y.loan_principal + y.sale_revenue; if (y.year === 1) c -= eq + dt; return Math.round(c * 100) / 100 })
      })()
      chart.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        legend: { data: ['租金收入','出售收回','运营成本','税费','财务成本','还本支出','投资支出','现金净额'] },
        xAxis: { data: years },
        yAxis: { type: 'value', name: '万元' },
        series: [
          { name: '租金收入', type: 'bar', stack: 'total', data: yd.map(y => y.rent_income),
            itemStyle: { color: '#67c23a' } },
          { name: '出售收回', type: 'bar', stack: 'total', data: yd.map(y => y.sale_revenue),
            itemStyle: { color: '#e6a23c' } },
          { name: '运营成本', type: 'bar', stack: 'total', data: yd.map(y => -y.opex),
            itemStyle: { color: '#909399' } },
          { name: '税费', type: 'bar', stack: 'total', data: yd.map(y => -y.tax),
            itemStyle: { color: '#d7b806' } },
          { name: '财务成本', type: 'bar', stack: 'total', data: yd.map(y => -y.finance_cost),
            itemStyle: { color: '#f56c6c' } },
          { name: '还本支出', type: 'bar', stack: 'total', data: yd.map(y => -y.loan_principal),
            itemStyle: { color: '#f0a0a0' } },
          { name: '投资支出', type: 'bar', stack: 'total', data: yd.map((y,i) => i === 0 ? -(eq + dt) : 0),
            itemStyle: { color: '#c03620' } },
          { name: '现金净额', type: 'line', data: cum,
            lineStyle: { width: 2, color: '#409eff' },
            itemStyle: { color: '#409eff' },
            label: { show: true, formatter: (p) => p.value.toFixed(2), fontSize: 10, color: '#409eff', fontWeight: 'bold' },
            markPoint: {
              symbol: 'pin', symbolSize: 50,
              data: [
                { type: 'min', label: { formatter: (p) => '投资 -' + Math.abs(p.value).toFixed(2), color: '#fff', fontSize: 10 } },
                { type: 'max', label: { formatter: (p) => '结余 ' + p.value.toFixed(2), color: '#fff', fontSize: 10 } },
              ]
            },
          },
        ]
      })
    },
    fmt(row, col, val) { return val != null ? Number(val).toFixed(2) : '-' },
    getSummaries({ columns, data }) {
      const sums = []
      const fields = ['rent_income','tax','depreciation','opex','finance_cost','operating_profit','sale_revenue']
      columns.forEach((col, i) => {
        if (i === 0) { sums[i] = '合计'; return }
        const key = col.property
        if (fields.includes(key)) {
          sums[i] = data.reduce((s, r) => s + (Number(r[key]) || 0), 0).toFixed(2)
        } else {
          sums[i] = ''
        }
      })
      return sums
    },
    async save() {
      if (!this.saveName) { this.$message.warning('请输入方案名称'); return }
      await api.saveRecord(this.saveName, this.$route.params.templateId, this.params, this.result)
      this.$message.success('已存档')
      this.saveName = ''
    }
  }
}
</script>
