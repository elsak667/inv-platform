<template>
  <div v-if="loadingTemplate" class="page-container" style="text-align:center;padding:80px 0;color:#999">加载中...</div>
  <div v-else-if="!params" class="page-container" style="text-align:center;padding:80px 0;color:#f00">模板加载失败</div>
  <div v-else class="page-container">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="测算" name="calc">
        <el-row :gutter="24">
          <!-- 左: 参数表单 -->
          <el-col :xs="24" :sm="24" :md="10">
            <el-form label-position="top" size="small">

              <!-- 一、收购项目 -->
              <div class="section-card">
                <div class="section-title">一、收购项目</div>
                <div v-for="(u, i) in params.units" :key="i"
                  style="margin-bottom:10px;border:1px solid #e2e8f0;border-radius:8px;padding:10px;position:relative">
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                    <span style="font-weight:600;font-size:13px;color:#1e293b">物业 {{ i+1 }}</span>
                    <el-button type="danger" link size="small" @click="params.units.splice(i,1)">删除</el-button>
                  </div>
                  <el-row :gutter="8">
                    <el-col :span="6"><div class="field-label">项目名称</div><el-input v-model="u.name" placeholder="如：潍坊" size="small" /></el-col>
                    <el-col :span="4"><div class="field-label">套数</div><el-input-number v-model="u.units" :min="1" controls-position="right" style="width:100%" size="small" /></el-col>
                    <el-col :span="5"><div class="field-label">面积（㎡）</div><el-input-number v-model="u.area" :min="1" controls-position="right" style="width:100%" size="small" /></el-col>
                    <el-col :span="4"><div class="field-label">均价（万元/㎡）</div><el-input-number v-model="u.price_per_sqm" :min="0" :precision="2" :step="0.1" controls-position="right" style="width:100%" size="small" /></el-col>
                    <el-col :span="5"><div class="field-label">市场租金（元/㎡/月）</div><el-input-number v-model="u.market_rent" :min="0" controls-position="right" style="width:100%" size="small" /></el-col>
                  </el-row>
                  <el-row :gutter="8" style="margin-top:6px">
                    <el-col :span="6"><div class="field-label">租金折扣</div>
                      <el-input-number v-model="u.discount" :min="0" :max="1" :step="0.01"
                        :formatter="pct0" :parser="unpct" controls-position="right" style="width:100%" size="small" />
                    </el-col>
                    <el-col :span="6"><div class="field-label">装修成本（元/㎡）</div><el-input-number v-model="u.decoration_cost_per_sqm" :min="0" :step="100" controls-position="right" style="width:100%" size="small" /></el-col>
                    <el-col :span="6">
                      <div class="field-label">折后租金（自动）</div>
                      <div class="auto-value">{{ (u.market_rent * u.discount).toFixed(1) }}</div>
                    </el-col>
                    <el-col :span="6">
                      <div class="field-label">收购总价（自动）</div>
                      <div class="auto-value">{{ (u.area * u.price_per_sqm).toFixed(0) }} 万元</div>
                    </el-col>
                  </el-row>
                </div>
                <el-button type="primary" link size="small" @click="addUnit" style="margin-bottom:2px">+ 新增物业</el-button>
                <el-row :gutter="8" style="margin-top:8px">
                  <el-col :span="8" :offset="16"><div class="field-label">出售收回总额（万元）</div><el-input-number v-model="params.sale.revenue" :min="0" controls-position="right" style="width:100%" size="small" /></el-col>
                </el-row>
              </div>

              <!-- 二、经营预期 -->
              <div class="section-card green">
                <div class="section-title">二、经营预期</div>
                <el-row :gutter="8" style="margin-bottom:8px">
                  <el-col :span="8"><div class="field-label">运营成本占比</div><el-input-number v-model="params.operations.opex_ratio" :min="0" :max="1" :step="0.01" :formatter="pct0" :parser="unpct" controls-position="right" style="width:100%" size="small" /></el-col>
                  <el-col :span="8"><div class="field-label">每次涨幅</div><el-input-number v-model="params.operations.rent_adjust_rate" :min="0" :max="1" :step="0.01" :formatter="pct1" :parser="unpct" controls-position="right" style="width:100%" size="small" /></el-col>
                  <el-col :span="8"><div class="field-label">调租间隔（年）</div><el-input-number v-model="params.operations.rent_adjust_period" :min="1" :max="30" controls-position="right" style="width:100%" size="small" /></el-col>
                </el-row>
                <div style="margin-bottom:4px">
                  <div class="field-label" style="margin-bottom:4px">出租率</div>
                  <el-row :gutter="8" style="margin-bottom:2px">
                    <el-col :span="4"><div class="field-label-sub" style="text-align:center">第1年</div></el-col>
                    <el-col :span="4"><div class="field-label-sub" style="text-align:center">第2年</div></el-col>
                    <el-col :span="4"><div class="field-label-sub" style="text-align:center">第3年</div></el-col>
                    <el-col :span="4"><div class="field-label-sub" style="text-align:center">第4年起</div></el-col>
                  </el-row>
                  <el-row :gutter="8">
                    <el-col :span="4"><el-input-number v-model="params.operations.occupancy_schedule.year_1" :min="0" :max="1" :step="0.05" :formatter="pct0" :parser="unpct" controls-position="right" size="small" style="width:100%" /></el-col>
                    <el-col :span="4"><el-input-number v-model="params.operations.occupancy_schedule.year_2" :min="0" :max="1" :step="0.05" :formatter="pct0" :parser="unpct" controls-position="right" size="small" style="width:100%" /></el-col>
                    <el-col :span="4"><el-input-number v-model="params.operations.occupancy_schedule.year_3" :min="0" :max="1" :step="0.05" :formatter="pct0" :parser="unpct" controls-position="right" size="small" style="width:100%" /></el-col>
                    <el-col :span="4"><el-input-number v-model="params.operations.occupancy_schedule.year_4" :min="0" :max="1" :step="0.05" :formatter="pct0" :parser="unpct" controls-position="right" size="small" style="width:100%" /></el-col>
                  </el-row>
                </div>
              </div>

              <!-- 三、税费设定 -->
              <div class="section-card orange">
                <div class="section-title">三、税费设定</div>
                <el-row :gutter="8" style="margin-bottom:8px">
                  <el-col :span="6"><div class="field-label">契税</div><el-input-number v-model="params.taxes.deed_tax_rate" :min="0" :max="1" :step="0.001" :formatter="pct2" :parser="unpct" controls-position="right" style="width:100%" size="small" /></el-col>
                  <el-col :span="6"><div class="field-label">交易印花税</div><el-input-number v-model="params.taxes.transaction_stamp_rate" :min="0" :max="1" :step="0.0001" :formatter="pct2" :parser="unpct" controls-position="right" style="width:100%" size="small" /></el-col>
                  <el-col :span="6"><div class="field-label">增值税及附加</div><el-input-number v-model="params.taxes.vat_rate" :min="0" :max="1" :step="0.001" :formatter="pct2" :parser="unpct" controls-position="right" style="width:100%" size="small" /></el-col>
                  <el-col :span="6"><div class="field-label">租赁印花税</div><el-input-number v-model="params.taxes.rent_stamp_rate" :min="0" :max="1" :step="0.0001" :formatter="pct2" :parser="unpct" controls-position="right" style="width:100%" size="small" /></el-col>
                </el-row>
                <el-row :gutter="8">
                  <el-col :span="4"><div class="field-label">房产税(从租)</div><el-input-number v-model="params.taxes.property_tax_lease" :min="0" :max="1" :step="0.001" :formatter="pct2" :parser="unpct" controls-position="right" style="width:100%" size="small" /></el-col>
                  <el-col :span="4"><div class="field-label">房产税(从价)</div><el-input-number v-model="params.taxes.property_tax_value" :min="0" :max="1" :step="0.0001" :formatter="pct2" :parser="unpct" controls-position="right" style="width:100%" size="small" /></el-col>
                  <el-col :span="4"><div class="field-label">借款印花税</div><el-input-number v-model="params.taxes.loan_stamp_rate" :min="0" :max="1" :step="0.00001" :formatter="pct2" :parser="unpct" controls-position="right" style="width:100%" size="small" /></el-col>
                  <el-col :span="6"><div class="field-label">土地使用税(元/㎡)</div><el-input-number v-model="params.taxes.land_tax_per_sqm" :min="0" controls-position="right" style="width:100%" size="small" /></el-col>
                  <el-col :span="6"><div class="field-label">占地面积(㎡)</div><el-input-number v-model="params.taxes.land_area" :min="0" controls-position="right" style="width:100%" size="small" /></el-col>
                </el-row>
              </div>

              <!-- 四、会计估计 -->
              <div class="section-card purple">
                <div class="section-title">四、会计估计</div>
                <el-row :gutter="8">
                  <el-col :span="8"><div class="field-label">房屋折旧年限</div><el-input-number v-model="params.depreciation.building_life" :min="1" :max="60" controls-position="right" style="width:100%" size="small" /></el-col>
                  <el-col :span="6"><div class="field-label">残值率</div><el-input-number v-model="params.depreciation.residual_ratio" :min="0" :max="0.5" :step="0.01" :formatter="pct0" :parser="unpct" controls-position="right" style="width:100%" size="small" /></el-col>
                  <el-col :span="8"><div class="field-label">装修摊销年限</div><el-input-number v-model="params.depreciation.decoration_life" :min="1" :max="30" controls-position="right" style="width:100%" size="small" /></el-col>
                </el-row>
              </div>

              <!-- 五、融资方案 -->
              <div class="section-card red">
                <div class="section-title">五、融资方案</div>
                <div v-for="(p, i) in params.loan_plans" :key="i" style="margin-bottom:10px;border:1px solid #e2e8f0;border-radius:8px;padding:10px">
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
                    <span style="font-size:13px;font-weight:600;color:#1e293b">方案 {{ i+1 }}：{{ p.id || '(未命名)' }}</span>
                    <el-button type="danger" link size="small" @click="params.loan_plans.splice(i,1)">删除</el-button>
                  </div>
                  <el-row :gutter="8" style="margin-bottom:2px">
                    <el-col :span="6"><div class="field-label-sub">方案名称</div></el-col>
                    <el-col :span="6"><div class="field-label-sub">年利率</div></el-col>
                    <el-col :span="6"><div class="field-label-sub">贷款比例</div></el-col>
                    <el-col :span="6"><div class="field-label-sub">贷款年限</div></el-col>
                  </el-row>
                  <el-row :gutter="8">
                    <el-col :span="6"><el-input v-model="p.id" placeholder="如：3+3年" size="small" /></el-col>
                    <el-col :span="6"><el-input-number v-model="p.rate" :min="0" :max="1" :step="0.001" :formatter="pct2" :parser="unpct" controls-position="right" style="width:100%" size="small" /></el-col>
                    <el-col :span="6"><el-input-number v-model="p.loan_ratio" :min="0" :max="1" :step="0.01" :formatter="pct0" :parser="unpct" controls-position="right" style="width:100%" size="small" /></el-col>
                    <el-col :span="6"><el-input-number v-model="p.holding_years" :min="1" @change="onHoldingYearsChange(p)" controls-position="right" style="width:100%" size="small" /></el-col>
                  </el-row>
                  <!-- 还款节奏 -->
                  <el-row :gutter="8" style="margin-top:8px">
                    <el-col :span="24">
                      <div class="field-label" style="margin-bottom:4px">还款节奏</div>
                      <el-radio-group v-model="p.repayment_type" size="small" @change="onRepaymentTypeChange(p)">
                        <el-radio-button label="custom">手填</el-radio-button>
                        <el-radio-button label="bullet">到期一次还本</el-radio-button>
                        <el-radio-button label="equal_principal">等额本金</el-radio-button>
                        <el-radio-button label="stepped">等额递增</el-radio-button>
                      </el-radio-group>
                    </el-col>
                  </el-row>
                  <!-- 手填模式 -->
                  <el-row v-if="p.repayment_type === 'custom'" :gutter="8" style="margin-top:8px">
                    <el-col :span="24">
                      <div class="field-label" style="margin-bottom:4px">逐年还本额（万元，-1=还清剩余，第1年默认0只付息）</div>
                      <div style="display:flex;flex-wrap:wrap;gap:4px">
                        <div v-for="y in p.holding_years" :key="'rep'+y" style="display:flex;align-items:center;gap:2px">
                          <span style="font-size:10px;color:#94a3b8;width:28px">Y{{y}}</span>
                          <el-input-number v-model="p.repayment_schedule['year_' + y]" :min="-1" :step="10" size="small" controls-position="right" style="width:90px" />
                        </div>
                      </div>
                      <div style="font-size:10px;color:#94a3b8;margin-top:2px">第1年默认0（只付息）· 末年默认-1（还清剩余）· 均可修改</div>
                    </el-col>
                  </el-row>
                  <!-- 等额递增 -->
                  <el-row v-if="p.repayment_type === 'stepped'" :gutter="8" style="margin-top:8px">
                    <el-col :span="12">
                      <div class="field-label">第2年还本（万元）</div>
                      <el-input-number v-model="p.repayment_start" :min="0" :step="10" size="small" controls-position="right" style="width:100%" />
                    </el-col>
                    <el-col :span="12">
                      <div class="field-label">每年增量（万元）</div>
                      <el-input-number v-model="p.repayment_increment" :step="10" size="small" controls-position="right" style="width:100%" />
                    </el-col>
                  </el-row>
                </div>
                <el-button type="primary" link size="small" @click="addPlan" style="margin-bottom:2px">+ 新增方案</el-button>
              </div>

              <!-- 测算按钮 -->
              <el-button type="primary" @click="runCalc" :loading="loading" class="btn-primary" style="margin-bottom:24px">开始测算</el-button>
            </el-form>
          </el-col>

          <!-- 右: 结果 -->
          <el-col :xs="24" :sm="24" :md="14">
            <div v-if="!result" class="empty-state">
              <svg style="width:48px;height:48px;color:#cbd5e1;margin-bottom:12px" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
              <p>填写左边的参数，点击「开始测算」查看结果</p>
            </div>

            <div v-else>
              <!-- 方案对比卡片 -->
              <div class="section-card" style="margin-bottom:16px">
                <div class="section-title">方案对比</div>
                <el-row :gutter="16">
                  <el-col v-for="p in result.plans" :key="p.plan" :span="24 / result.plans.length">
                    <div :class="['plan-card-v2', selectedPlan === p.plan ? 'selected' : '']"
                      @click="selectedPlan = p.plan; $nextTick(drawChart)">
                      <div class="plan-card-v2-header">
                        <span class="plan-name">{{ p.plan }}</span>
                        <span v-if="selectedPlan === p.plan" class="plan-active-dot"></span>
                      </div>
                      <div class="plan-card-v2-body">
                        <div class="kpi-row">
                          <div class="kpi">
                            <div class="kpi-label">项目毛利</div>
                            <div :class="['kpi-value', p.project_gross_profit >= 0 ? 'pos' : 'neg']">
                              {{ fmt0(p.project_gross_profit) }}<span class="kpi-unit">万</span>
                            </div>
                          </div>
                          <div class="kpi">
                            <div class="kpi-label">现金流结余</div>
                            <div :class="['kpi-value', p.cash_flow_total >= 0 ? 'pos' : 'neg']">
                              {{ fmt0(p.cash_flow_total) }}<span class="kpi-unit">万</span>
                            </div>
                          </div>
                        </div>
                        <div class="kpi-breakdown">
                          <div class="breakdown-item">
                            <span class="bd-dot green"></span>
                            <span class="bd-label">运营毛利</span>
                            <span class="bd-val">{{ fmt0(p.operating_profit_total) }}</span>
                          </div>
                          <div class="breakdown-item">
                            <span class="bd-dot blue"></span>
                            <span class="bd-label">出售毛利</span>
                            <span class="bd-val">{{ fmt0(p.sale_profit) }}</span>
                          </div>
                          <div class="breakdown-item">
                            <span class="bd-dot orange"></span>
                            <span class="bd-label">持有期收支</span>
                            <span class="bd-val">{{ fmt0(p.cash_flow_total - p.sale_revenue) }}</span>
                          </div>
                          <div class="breakdown-item">
                            <span class="bd-dot purple"></span>
                            <span class="bd-label">出售收回</span>
                            <span class="bd-val">{{ fmt0(p.sale_revenue) }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </el-col>
                </el-row>
              </div>

              <!-- 现金流走势图 -->
              <div class="section-card chart-card" style="margin-bottom:16px">
                <div class="chart-header">
                  <div class="chart-title">
                    <span class="chart-title-text">现金流走势</span>
                    <span class="chart-plan-badge">{{ selectedPlan }}</span>
                  </div>
                  <div class="chart-legend-mini">
                    <span class="legend-item"><span class="legend-dot" style="background:#10b981"></span>租金</span>
                    <span class="legend-item"><span class="legend-dot" style="background:#f59e0b"></span>出售</span>
                    <span class="legend-item"><span class="legend-dot" style="background:#3b82f6"></span>现金净额</span>
                  </div>
                </div>
                <div ref="chartEl" style="height:400px"></div>
              </div>

              <!-- 逐年明细表 -->
              <div class="section-card table-card" style="margin-bottom:16px">
                <div class="card-header-bar">
                  <div class="card-header-title">
                    <span class="card-header-icon">📊</span>
                    <span>逐年明细</span>
                  </div>
                  <el-select v-model="selectedPlan" size="small" style="width:200px" @change="drawChart">
                    <el-option v-for="p in result.plans" :key="p.plan" :label="p.plan" :value="p.plan" />
                  </el-select>
                </div>
                <el-table :data="currentPlan.yearly" size="small" show-summary :summary-method="getSummaries"
                  :header-cell-style="{ background:'#f8fafc', color:'#334155', fontWeight:600 }"
                  :cell-style="{ padding:'8px 0' }"
                  style="width:100%">
                  <el-table-column prop="year" label="年份" width="60" align="center">
                    <template #default="{ row }">
                      <span style="font-weight:600;color:#1a56db">Y{{ row.year }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="rent_income" label="租金收入" :formatter="fmt" align="right" />
                  <el-table-column prop="tax" label="税费" :formatter="fmt" align="right" />
                  <el-table-column prop="depreciation" label="折旧" :formatter="fmt" align="right" />
                  <el-table-column prop="opex" label="运营成本" :formatter="fmt" align="right" />
                  <el-table-column prop="finance_cost" label="财务成本" :formatter="fmt" align="right" />
                  <el-table-column prop="operating_profit" label="运营毛利" :formatter="fmt" align="right">
                    <template #default="{ row }">
                      <span :style="{ color: row.operating_profit >= 0 ? '#10b981' : '#ef4444', fontWeight:600 }">
                        {{ fmt(null,null,row.operating_profit) }}
                      </span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="sale_revenue" label="出售收回" :formatter="fmt" align="right" />
                  <el-table-column prop="loan_balance" label="贷款余额" :formatter="fmt" align="right" />
                </el-table>
              </div>

              <!-- 分析报告 -->
              <div class="section-card purple report-card" style="margin-bottom:16px">
                <div class="card-header-bar">
                  <div class="card-header-title">
                    <span class="card-header-icon">📄</span>
                    <span>分析报告</span>
                  </div>
                  <div class="report-actions">
                    <el-switch v-model="reportAiMode" active-text="AI增强" inactive-text="标准" size="small" />
                    <el-button type="primary" size="small" @click="doGenerateReport" :loading="reportLoading">
                      <span style="display:inline-flex;align-items:center;gap:4px">
                        <svg style="width:12px;height:12px" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
                        生成报告
                      </span>
                    </el-button>
                    <el-button v-if="reportMd" size="small" @click="copyReport">复制</el-button>
                    <el-button v-if="reportMd" size="small" @click="downloadReport">下载</el-button>
                    <el-button v-if="reportOutline" size="small" @click="downloadOutline">PPT大纲</el-button>
                  </div>
                </div>
                <div v-if="reportMd">
                  <div class="report-view-toggle">
                    <el-radio-group v-model="reportView" size="small">
                      <el-radio-button label="rendered">预览</el-radio-button>
                      <el-radio-button label="raw">源码</el-radio-button>
                    </el-radio-group>
                  </div>
                  <div v-if="reportView === 'raw'" class="report-content">{{ reportMd }}</div>
                  <div v-else class="report-rendered" v-html="reportRendered"></div>
                </div>
                <div v-if="!reportMd" class="report-empty">
                  <svg style="width:40px;height:40px;color:#cbd5e1;margin-bottom:8px" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
                  <p>点击"生成报告"按钮，基于当前测算结果自动生成分析报告和PPT大纲</p>
                </div>
              </div>

              <!-- 保存 -->
              <div class="section-card save-card" style="margin-bottom:24px">
                <div class="save-row">
                  <div class="save-icon-wrap">
                    <svg style="width:18px;height:18px;color:#fff" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
                  </div>
                  <el-input v-model="saveName" placeholder="给这个方案取个名字" style="flex:1;max-width:280px" size="small" />
                  <el-button type="primary" @click="save" size="small" class="btn-primary">保存方案</el-button>
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import { marked } from 'marked'
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
      reportView: 'rendered',
    }
  },
  computed: {
    currentPlan() {
      if (!this.result) return { yearly: [] }
      return this.result.plans.find(p => p.plan === this.selectedPlan) || this.result.plans[0]
    },
    reportRendered() {
      if (!this.reportMd) return ''
      return marked(this.reportMd, { breaks: true })
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
        color: ['#10b981', '#f59e0b', '#94a3b8', '#cbd5e1', '#f87171', '#fca5a5', '#b91c1c', '#3b82f6'],
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow', shadowStyle: { color: 'rgba(59,130,246,0.08)' } },
          backgroundColor: 'rgba(15,43,92,0.92)',
          borderColor: 'transparent',
          textStyle: { color: '#fff', fontSize: 12 },
          valueFormatter: (v) => v != null ? Number(v).toFixed(2) + ' 万' : '-',
        },
        legend: { show: false },
        grid: { left: 50, right: 24, top: 24, bottom: 40 },
        xAxis: {
          data: years,
          axisLine: { lineStyle: { color: '#e2e8f0' } },
          axisTick: { show: false },
          axisLabel: { color: '#64748b', fontSize: 11 },
        },
        yAxis: {
          type: 'value',
          name: '万元',
          nameTextStyle: { color: '#94a3b8', fontSize: 11 },
          axisLine: { show: false },
          axisTick: { show: false },
          axisLabel: { color: '#94a3b8', fontSize: 11 },
          splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } },
        },
        series: [
          { name: '租金收入', type: 'bar', stack: 'total', data: yd.map(y => y.rent_income),
            itemStyle: { borderRadius: [0,0,0,0] } },
          { name: '出售收回', type: 'bar', stack: 'total', data: yd.map(y => y.sale_revenue) },
          { name: '运营成本', type: 'bar', stack: 'total', data: yd.map(y => -y.opex) },
          { name: '税费', type: 'bar', stack: 'total', data: yd.map(y => -y.tax) },
          { name: '财务成本', type: 'bar', stack: 'total', data: yd.map(y => -y.finance_cost) },
          { name: '还本支出', type: 'bar', stack: 'total', data: yd.map(y => -y.loan_principal) },
          { name: '投资支出', type: 'bar', stack: 'total', data: yd.map((y,i) => i === 0 ? -(eq + dt) : 0),
            itemStyle: { borderRadius: [6,6,0,0] } },
          { name: '现金净额', type: 'line', data: cum,
            smooth: true,
            lineStyle: { width: 3, color: '#3b82f6' },
            itemStyle: { color: '#3b82f6', borderColor: '#fff', borderWidth: 2 },
            symbol: 'circle', symbolSize: 8,
            label: { show: true, formatter: (p) => p.value.toFixed(2), fontSize: 11, color: '#1a56db', fontWeight: 'bold', position: 'top' },
            markPoint: {
              symbol: 'pin', symbolSize: 56,
              itemStyle: { color: '#1a56db' },
              label: { color: '#fff', fontSize: 10, fontWeight: 'bold' },
              data: [
                { type: 'min', label: { formatter: (p) => '投资 -' + Math.abs(p.value).toFixed(0) } },
                { type: 'max', label: { formatter: (p) => '结余 ' + p.value.toFixed(0) } },
              ]
            },
            areaStyle: {
              color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
                colorStops: [{ offset: 0, color: 'rgba(59,130,246,0.25)' }, { offset: 1, color: 'rgba(59,130,246,0)' }] }
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

<style scoped>
.field-label {
  font-size: 11px;
  color: #64748b;
  margin-bottom: 2px;
}

.field-label-sub {
  font-size: 10px;
  color: #94a3b8;
}

.auto-value {
  line-height: 28px;
  font-size: 13px;
  font-weight: 500;
  color: var(--primary-light, #3b82f6);
  padding-left: 4px;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.empty-state p {
  color: #94a3b8;
  font-size: 14px;
  margin: 0;
}

.report-content {
  max-height: 600px;
  overflow: auto;
  background: #f8fafc;
  border-radius: 6px;
  padding: 16px;
  font-size: 13px;
  line-height: 1.7;
  white-space: pre-wrap;
  font-family: monospace;
}

.report-rendered {
  max-height: 600px;
  overflow: auto;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 20px 24px;
  font-size: 14px;
  line-height: 1.8;
}

.report-rendered h1 { font-size: 20px; font-weight: 700; margin: 20px 0 12px; color: #1e293b; }
.report-rendered h2 { font-size: 17px; font-weight: 600; margin: 16px 0 8px; color: #1e293b; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px; }
.report-rendered h3 { font-size: 15px; font-weight: 600; margin: 12px 0 6px; color: #334155; }
.report-rendered p { margin: 0 0 8px; color: #475569; }
.report-rendered table { border-collapse: collapse; width: 100%; margin: 8px 0 12px; font-size: 13px; }
.report-rendered th, .report-rendered td { border: 1px solid #e2e8f0; padding: 6px 10px; text-align: right; }
.report-rendered th { background: #f1f5f9; font-weight: 600; color: #334155; text-align: center; }
.report-rendered ul, .report-rendered ol { padding-left: 20px; margin: 4px 0 8px; color: #475569; }
.report-rendered li { margin-bottom: 4px; }
.report-rendered strong { color: #1e293b; }

.report-empty {
  color: #94a3b8;
  font-size: 13px;
  text-align: center;
  padding: 20px;
}

/* override el-tab-pane styling */
:deep(.el-tabs__item) {
  font-size: 15px;
  font-weight: 500;
}

:deep(.el-tabs__nav-wrap::after) {
  height: 1px;
}

/* === 方案对比卡片 v2 === */
.plan-card-v2 {
  background: #fff;
  border-radius: 14px;
  padding: 0;
  border: 1px solid #e2e8f0;
  transition: all 0.25s;
  cursor: pointer;
  overflow: hidden;
  position: relative;
}

.plan-card-v2::before {
  content: '';
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 3px;
  background: #e2e8f0;
  transition: all 0.25s;
}

.plan-card-v2:hover {
  border-color: #cbd5e1;
  box-shadow: 0 8px 24px rgba(15,43,92,0.08);
  transform: translateY(-2px);
}

.plan-card-v2:hover::before {
  background: var(--primary-light, #3b82f6);
}

.plan-card-v2.selected {
  border-color: var(--primary, #1a56db);
  box-shadow: 0 12px 32px rgba(26,86,219,0.18);
}

.plan-card-v2.selected::before {
  background: var(--primary, #1a56db);
  width: 4px;
}

.plan-card-v2-header {
  padding: 14px 20px 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #f1f5f9;
}

.plan-name {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  letter-spacing: 0.3px;
}

.plan-active-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--primary, #1a56db);
  box-shadow: 0 0 0 4px rgba(26,86,219,0.2);
}

.plan-card-v2-body {
  padding: 16px 20px 18px;
}

.kpi-row {
  display: flex;
  gap: 8px;
  margin-bottom: 14px;
}

.kpi {
  flex: 1;
  text-align: center;
  background: #f8fafc;
  border-radius: 8px;
  padding: 10px 6px;
}

.kpi-label {
  font-size: 11px;
  color: #64748b;
  margin-bottom: 4px;
  font-weight: 500;
}

.kpi-value {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.5px;
  line-height: 1.1;
}

.kpi-value.pos { color: #10b981; }
.kpi-value.neg { color: #ef4444; }

.kpi-unit {
  font-size: 11px;
  font-weight: 400;
  color: #94a3b8;
  margin-left: 2px;
}

.kpi-breakdown {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding-top: 10px;
  border-top: 1px dashed #e2e8f0;
}

.breakdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
}

.bd-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.bd-dot.green { background: #10b981; }
.bd-dot.blue { background: #3b82f6; }
.bd-dot.orange { background: #f59e0b; }
.bd-dot.purple { background: #8b5cf6; }

.bd-label {
  color: #64748b;
  flex: 1;
}

.bd-val {
  color: #1e293b;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

/* === 现金流走势图卡片 === */
.chart-card {
  padding: 20px 24px 16px;
}

.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.chart-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.chart-title-text {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
}

.chart-plan-badge {
  background: linear-gradient(135deg, #1a56db, #3b82f6);
  color: #fff;
  font-size: 11px;
  font-weight: 500;
  padding: 3px 10px;
  border-radius: 10px;
  letter-spacing: 0.3px;
}

.chart-legend-mini {
  display: flex;
  gap: 14px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  color: #64748b;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 2px;
}

/* === 逐年明细表卡片 === */
.table-card {
  padding: 16px 20px;
}

.card-header-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.card-header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
}

.card-header-icon {
  font-size: 16px;
}

/* === 分析报告卡片 === */
.report-card {
  padding: 16px 20px;
}

.report-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.report-view-toggle {
  margin-bottom: 12px;
}

.report-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #94a3b8;
  font-size: 13px;
  text-align: center;
}

.report-empty p {
  margin: 0;
}

/* === 保存卡片 === */
.save-card {
  padding: 12px 16px;
  background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
  border-left-color: var(--primary);
}

.save-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.save-icon-wrap {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, var(--primary), var(--primary-light));
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(26,86,219,0.2);
}
</style>
