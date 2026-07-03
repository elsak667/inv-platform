# 投资测算平台 - 详细方案

## 一、系统定位

一个**模板驱动**的投资测算平台。核心能力：
- 预置测算模板（保租房/长租公寓/商业地产/厂房…）
- 用户填参数或导入 Excel → 引擎计算 → 网页看结果
- 多方案并排对比、图表可视化、导出 PDF
- 新增测算类型 = 加一份 YAML 模板，零代码

---

## 二、架构

```
┌─────────────────────────────────────────────────┐
│  前端 (Vue3 + Vite)                              │
│  ┌───────────┐ ┌───────────┐ ┌───────────────┐  │
│  │ 模板选择   │ │ 参数表单   │ │ 结果展示/对比  │  │
│  │ (动态)    │ │ (动态生成) │ │ (表格+图表)   │  │
│  └───────────┘ └───────────┘ └───────────────┘  │
└────────────────────┬────────────────────────────┘
                     │ HTTP/JSON
┌────────────────────┴────────────────────────────┐
│  后端 (FastAPI)                                  │
│  ┌───────────┐ ┌───────────┐ ┌───────────────┐  │
│  │ 模板管理   │ │ 测算引擎   │ │ 导出服务      │  │
│  │ (load yml)│ │ (core.py) │ │ (PDF/Excel)   │  │
│  └───────────┘ └───────────┘ └───────────────┘  │
└────────────────────┬────────────────────────────┘
                     │
              ┌──────┴──────┐
              │ templates/  │  YAML 模板库（可扩展）
              └─────────────┘
```

---

## 三、技术栈

| 层 | 选型 | 理由 |
|---|---|---|
| 后端 | FastAPI | Python，直接复用 core.py，自动生成 API 文档 |
| 前端 | Vue3 + Vite | 轻量，国企也好维护 |
| UI 组件 | Element Plus | 表单/表格/对话框齐全，中文友好 |
| 图表 | ECharts | 对比图/现金流瀑布图，国产文档全 |
| 表单引擎 | vue-form-generator 或自研 | 读 schema 动态生成表单 |
| 导出 | weasyprint（PDF）+ openpyxl（Excel 兜底） | PDF 为主，Excel 作可选 |
| 部署 | docker-compose | 单机起，内网部署 |

---

## 四、模板 Schema 设计（核心）

一份 YAML = 一个测算模板。分三段：**参数定义 / 计算逻辑 / 结果视图**。

```yaml
# templates/baozufang.yaml
meta:
  id: baozufang
  name: 收购项目测算（房管）
  version: 1.0
  engine: baozufang_v1   # 指向 core.py 中的引擎函数

# ---- 参数定义（前端据此生成表单）----
params:
  - key: units
    type: array
    label: 房源清单
    fields:
      - {key: name, label: 区位, type: text}
      - {key: area, label: 建筑面积(㎡), type: number}
      - {key: units, label: 套数, type: number}
      - {key: price_per_sqm, label: 均价(万元/㎡), type: number}
      - {key: market_rent, label: 市场租金(元/㎡/月), type: number}
      - {key: discount, label: 折扣, type: number, step: 0.01}
      - {key: decoration_cost_per_sqm, label: 装修成本(元/㎡), type: number}

  - key: operations
    type: group
    label: 运营参数
    fields:
      - {key: holding_years, label: 持有年数, type: number}
      - {key: rent_adjust_rate, label: 租金涨幅, type: number, step: 0.01}
      - {key: opex_ratio, label: 运营成本占比, type: number, step: 0.01}

  - key: taxes
    type: group
    label: 税费参数
    fields:
      - {key: deed_tax_rate, label: 契税率, type: number, step: 0.001}
      - {key: vat_rate, label: 增值税率, type: number, step: 0.001}
      # ...

  - key: loan_plans
    type: array
    label: 贷款方案（可多个）
    fields:
      - {key: id, label: 方案ID, type: text}
      - {key: rate, label: 利率, type: number, step: 0.0001}
      - {key: loan_ratio, label: 贷款比例, type: number, step: 0.01}
      - {key: holding_years, label: 贷款年限, type: number}
      - {key: repayment_type, label: 还款节奏, type: select, options: [custom, bullet, equal_principal, stepped]}
      - {key: repayment_schedule, label: 逐年还本(custom), type: keyvalue}
      - {key: repayment_start, label: 第2年还本(stepped), type: number}
      - {key: repayment_increment, label: 每年增量(stepped), type: number}

# ---- 计算引擎挂载点 ----
# core.py 中注册: @engine("baozufang_v1")
# def run(config): ...

# ---- 结果视图（前端据此渲染）----
views:
  - type: summary_cards
    title: 核心指标
    metrics:
      - {key: total_investment, label: 总投资(万元)}
      - {key: project_gross_profit, label: 项目整体毛利(万元)}
      - {key: cash_flow_total, label: 现金流结余(万元)}

  - type: table
    title: 逐年现金流
    data: yearly
    columns:
      - {key: year, label: 年份}
      - {key: rent_income, label: 租金收入}
      - {key: tax, label: 税费}
      - {key: finance_cost, label: 财务成本}
      - {key: operating_profit, label: 运营毛利}

  - type: chart
    title: 现金流走势
    chart_type: line
    x: year
    series:
      - {key: rent_income, label: 租金收入}
      - {key: finance_cost, label: 财务成本}
      - {key: operating_profit, label: 运营毛利}

  - type: comparison
    title: 多方案对比
    plans: loan_plans
    metrics:
      - {key: loan_total_interest, label: 利息合计}
      - {key: operating_profit_total, label: 运营毛利}
      - {key: project_gross_profit, label: 项目毛利}
      - {key: cash_flow_total, label: 现金流结余}
```

---

## 五、目录结构

```
inv-platform/
├── backend/
│   ├── main.py              # FastAPI 入口
│   ├── engines/
│   │   ├── __init__.py      # 引擎注册装饰器
│   │   ├── baozufang.py     # 保租房引擎（现 core.py）
│   │   └── changzu.py       # 长租公寓引擎（未来）
│   ├── templates/
│   │   ├── baozufang.yaml
│   │   └── changzu.yaml
│   ├── services/
│   │   ├── template.py      # 加载/校验模板
│   │   ├── calculator.py    # 调度引擎
│   │   └── exporter.py      # PDF/Excel 导出
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── TemplateList.vue    # 模板选择页
│   │   │   ├── Calculator.vue      # 测算页（表单+结果）
│   │   │   └── Comparison.vue      # 多方案对比页
│   │   ├── components/
│   │   │   ├── DynamicForm.vue     # 读 schema 生成表单
│   │   │   ├── ResultTable.vue
│   │   │   └── ResultChart.vue
│   │   └── api/
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml
└── docs/
```

---

## 六、API 设计

```
GET  /api/templates                 列出所有模板
GET  /api/templates/{id}            取模板 schema（前端据此渲染表单）

POST /api/calculate                 提交参数 → 返回测算结果
  body: { template_id, params }
  resp: { summary, yearly, plans[] }

POST /api/calculate/compare         多方案对比
  body: { template_id, params, plan_ids: [] }
  resp: { plans: [{plan_id, summary, yearly}] }

POST /api/export/pdf                导出 PDF
  body: { template_id, params, plan_id }
  resp: application/pdf

POST /api/import/excel              从 Excel 提取参数（可选）
  body: multipart file
  resp: { params }  # 映射到模板 schema
```

---

## 七、前端页面

**页1 模板选择**
- 卡片列出所有模板（保租房/长租公寓…）
- 点卡片进入测算

**页2 测算页**（左右分栏）
- 左：参数表单（按 schema 动态生成，分组折叠）
- 右：结果区
  - 顶部：核心指标卡片（总投资/毛利/现金流）
  - 中部：逐年现金流表格
  - 底部：现金流走势图（ECharts 折线）
- 底部按钮：「保存方案」「导出PDF」「加入对比」

**页3 方案对比**
- 多个贷款方案并排表格
- 雷达图/柱状图对比关键指标
- 一键导出对比报告 PDF

---

## 八、实施路线（分 4 期）

### 第1期：MVP（1-2天）— 单模板跑通网页
- [ ] FastAPI 暴露 `/api/templates` 和 `/api/calculate`
- [ ] 把 core.py 包装成引擎，注册 `baozufang_v1`
- [ ] 前端最简页面：表单填参数 → 调 API → 显示结果表格
- [ ] 无样式，先验证链路通

### 第2期：可用（2-3天）— 表单+图表+对比
- [ ] DynamicForm 组件读 schema 生成表单
- [ ] ECharts 现金流走势图
- [ ] 多方案对比页
- [ ] Element Plus 美化

### 第3期：可交付（2-3天）— 导出+Excel导入
- [ ] PDF 导出（weasyprint，套模板排版）
- [ ] Excel 导入参数（解析 sample.xlsx → 映射 schema）
- [ ] 方案保存/加载（localStorage 或 sqlite）

### 第4期：可扩展（1-2天）— 第二个模板验证
- [ ] 加一个长租公寓模板（简化版）
- [ ] 验证"加 yaml 即新模板"的闭环
- [ ] 文档：如何写新模板

---

## 九、关键决策点（需确认）

1. **部署环境**：内网单机？还是需要多用户/权限？
   - 影响：是否要做登录/数据库
2. **Excel 导入**：必选还是可选？
   - 影响：第3期工作量
3. **数据持久化**：测算方案要不要存档复用？
   - 影响：是否需要数据库（sqlite 够用）
4. **并发**：多人同时用？
   - 影响：后端是否需要异步/队列
```
