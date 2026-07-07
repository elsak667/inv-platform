"""测算分析报告生成 — 模板 + LLM 增强"""

from datetime import date
import os
from engines.baozufang import calc_investment, TaxParams, Unit


_NVIDIA_API = "https://integrate.api.nvidia.com/v1/chat/completions"


def _fmt(v: float) -> str:
    return f"{v:,.2f}"


def _pct(v: float) -> str:
    return f"{v * 100:.2f}%"


def _inv_breakdown(config: dict) -> dict:
    """从 config 算投资成本明细"""
    units = [Unit(**u) for u in config["units"]]
    taxes = TaxParams(**config["taxes"])
    return calc_investment(units, taxes)


def _project_overview(config: dict, inv: dict) -> str:
    units = config["units"]
    total_units = sum(u["units"] for u in units)
    total_area = sum(u["area"] for u in units)
    locs = " + ".join(f'{u["name"]}×{u["units"]}套' for u in units)
    avg_price = sum(u["price_per_sqm"] * u["area"] for u in units) / total_area

    lines = [
        "## 一、项目概况",
        "",
        f"- **房源**：{locs}",
        f"- **总建筑面积**：{_fmt(total_area)}㎡",
        f"- **收购均价**：{_fmt(avg_price)}万元/㎡",
        f"- **收购总价**：{_fmt(inv['total_acquisition'])}万元",
        f"- **装修成本**：{_fmt(inv['total_decoration'])}万元",
        f"- **总投资**：**{_fmt(inv['total_investment'])}万元**",
    ]
    return "\n".join(lines)


def _assumptions(config: dict) -> str:
    dep = config["depreciation"]
    ops = config["operations"]
    taxes = config["taxes"]

    lines = [
        "## 二、测算假设条件",
        "",
        "### 2.1 折旧摊销",
        f"- 房屋折旧年限：{dep['building_life']}年",
        f"- 装修摊销年限：{dep['decoration_life']}年",
        f"- 残值率：{_pct(dep.get('residual_ratio', 0))}",
        "",
        "### 2.2 运营参数",
        f"- 运营成本占比：{_pct(ops['opex_ratio'])}",
        f"- 租金调涨间隔：每{ops['rent_adjust_period']}年调涨{_pct(ops['rent_adjust_rate'])}",
        "",
        "### 2.3 税费参数",
        f"- 契税：{_pct(taxes['deed_tax_rate'])}",
        f"- 交易印花税：{_pct(taxes['transaction_stamp_rate'])}",
        f"- 增值税及附加：{_pct(taxes['vat_rate'])}",
        f"- 租赁印花税：{_pct(taxes['rent_stamp_rate'])}",
        f"- 房产税（从租）：{_pct(taxes['property_tax_lease'])}",
        f"- 房产税（从价）：{_pct(taxes['property_tax_value'])}",
        f"- 借款合同印花税：{_pct(taxes['loan_stamp_rate'])}",
        f"- 城镇土地使用税：{_fmt(taxes['land_tax_per_sqm'])}元/㎡ · 占地面积{_fmt(taxes['land_area'])}㎡",
    ]
    return "\n".join(lines)


def _cost_breakdown(inv: dict) -> str:
    total = inv["total_investment"]
    lines = [
        "## 三、投资成本结构",
        "",
        f"总投资 **{_fmt(total)}万元**, 构成如下：",
        "",
        "| 项目 | 金额（万元） | 占比 |",
        "|------|------------|------|",
        f"| 收购款 | {_fmt(inv['total_acquisition'])} | {_pct(inv['total_acquisition']/total)} |",
        f"| 装修成本 | {_fmt(inv['total_decoration'])} | {_pct(inv['total_decoration']/total)} |",
        f"| 契税 | {_fmt(inv['deed_tax'])} | {_pct(inv['deed_tax']/total)} |",
        f"| 交易印花税 | {_fmt(inv['transaction_stamp'])} | {_pct(inv['transaction_stamp']/total)} |",
        f"| **合计** | **{_fmt(total)}** | **100%** |",
    ]
    return "\n".join(lines)


def _plan_comparison(config: dict, plans: list) -> str:
    """融资方案对比表"""
    # 从 config 取利率
    rate_map = {lp["id"]: lp["rate"] for lp in config["loan_plans"]}
    lines = [
        "## 四、融资方案对比分析",
        "",
        f"共 **{len(plans)}个** 融资方案, 核心指标对比如下：",
        "",
        "| 指标 | " + " | ".join(f"{p['plan']}" for p in plans) + " |",
        "|------|" + "|".join("---" for _ in plans) + "|",
    ]
    rows = [
        ("贷款额", "loan_amount"),
        ("资本金", "equity"),
        ("贷款利率", None),
        ("贷款利息合计", "loan_total_interest"),
        ("租金收入合计", "total_rent"),
        ("运营成本合计", "total_opex"),
        ("运营毛利合计", "operating_profit_total"),
        ("出售收回", "sale_revenue"),
        ("投资出售毛利", "sale_profit"),
        ("**项目整体毛利**", "project_gross_profit"),
        ("现金流结余", "cash_flow_total"),
    ]
    for label, key in rows:
        if key is None:
            # 贷款利率 — 从 config 取
            vals = [_pct(rate_map.get(p["plan"], 0)) for p in plans]
        else:
            vals = [_fmt(p.get(key, 0)) for p in plans]
        lines.append(f"| {label} | " + " | ".join(str(v) for v in vals) + " |")

    return "\n".join(lines)


def _yearly_detail(plans: list) -> str:
    lines = ["## 五、各方案逐年经营明细", ""]
    for p in plans:
        lines.append(f"### {p['plan']}")
        lines.append("")
        lines.append("| 年份 | 租金收入 | 税费 | 折旧 | 运营成本 | 财务成本 | 运营毛利 | 出售收回 | 贷款余额 |")
        lines.append("|------|---------|------|------|----------|----------|----------|----------|----------|")
        for y in p["yearly"]:
            lines.append(
                f"| {y['year']} | {_fmt(y['rent_income'])} "
                f"| {_fmt(y['tax'])} | {_fmt(y['depreciation'])} "
                f"| {_fmt(y['opex'])} | {_fmt(y['finance_cost'])} "
                f"| {_fmt(y['operating_profit'])} | {_fmt(y.get('sale_revenue',0))} "
                f"| {_fmt(y.get('loan_balance',0))} |"
            )
        lines.append("")
    return "\n".join(lines)


def _evaluation(plans: list) -> str:
    best = max(plans, key=lambda p: p["project_gross_profit"])
    texts = [f'{_fmt(p["project_gross_profit"])}\u4e07\u5143\uff08{p["plan"]}\uff09' for p in plans]
    lines = [
        "## 六、项目综合评价",
        "",
        f"三方案整体毛利分别为 {', '.join(texts)}。",
        f"其中 **{best['plan']}方案** 整体毛利最高（**{_fmt(best['project_gross_profit'])}万元**），",
        f"在同时考虑持有期、现金流安全性的情况下为首选方案。",
    ]
    return "\n".join(lines)


def _ppt_outline(config: dict, inv: dict, plans: list) -> str:
    total = inv["total_investment"]
    best = max(plans, key=lambda p: p["project_gross_profit"])
    units = config["units"]
    locs = " + ".join(f'{u["name"]}\u00d7{u["units"]}\u5957' for u in units)
    total_area = sum(u["area"] for u in units)
    rate_min = min(p["loan_total_interest"] for p in plans)
    rate_max = max(p["loan_total_interest"] for p in plans)
    equity_min = min(p["equity"] for p in plans)
    equity_max = max(p["equity"] for p in plans)

    lines = [
        "\u0023\u0023 七、PPT大纲",
        "",
        "> 以下每页 Slide 均可直接作为演示文稿的单页内容。",
        "",
        "### Slide 1：封面",
        f"- {config['meta']['name']}",
        f"- 测算日期：{date.today().isoformat()}",
        "",
        "### Slide 2：项目概览",
        f"- 房源：{locs}",
        f"- 总面积：{_fmt(total_area)}㎡",
        f"- 总投资：**{_fmt(total)}万元**",
        "> 一句话讲清项目规模",
        "",
        "### Slide 3：投资成本结构",
        "> **建议图表**：饼图",
        f"- 收购款 {_fmt(inv['total_acquisition'])}万（{_pct(inv['total_acquisition']/total)}）",
        f"- 装修 {_fmt(inv['total_decoration'])}万（{_pct(inv['total_decoration']/total)}）",
        "> 收购款占绝对大头",
        "",
        "### Slide 4：融资方案对比",
        "> **建议图表**：并列柱状图（贷款额+资本金）",
        f"- 共 {len(plans)} 个方案，利息合计 {_fmt(rate_min)} ~ {_fmt(rate_max)}，资本金 {_fmt(equity_min)} ~ {_fmt(equity_max)}",
        "> 各方案核心区别在于利率和贷款成数",
        "",
        "### Slide 5：收益对比——选哪个方案",
        "> **建议图表**：堆叠柱状图（运营毛利+出售毛利）",
    ]
    for p in sorted(plans, key=lambda x: x["project_gross_profit"], reverse=True):
        lines.append(
            f"- {p['plan']}：整体毛利 **{_fmt(p['project_gross_profit'])}万元**"
            f"（运营{_fmt(p['operating_profit_total'])} + 出售{_fmt(p['sale_profit'])}）"
        )
    lines.append(f"> 推荐 **{best['plan']}**，毛利最高且持有期合理")
    lines.extend([
        "",
        "### Slide 6：逐年现金流走势",
        "> **建议图表**：折线图",
        "- 前 3 年现金流为负（装修+出租爬坡期）",
        "- 期末通过出售一次性回正",
        "> 项目依赖期末出售实现盈利",
        "",
        "### Slide 7：风险与缓释措施",
        "- 出租率风险：低于预期则租金收入下降",
        "- 利率风险：当前低利率，上行空间需关注",
        "- 出售价格风险：期末售价直接影响最终收益",
        "> 三个风险中影响最大的是期末出售价格",
        "",
        "### Slide 8：结论与建议",
        f"- **推荐方案**：{best['plan']}",
        f"- 整体毛利：**{_fmt(best['project_gross_profit'])}万元**",
        f"- 资本金需求：{_fmt(best['equity'])}万元",
        f"- 现金流结余：{_fmt(best['cash_flow_total'])}万元",
        "> 建议采用该方案，在收益与风险之间取得最佳平衡",
    ])
    return "\n".join(lines)

def _build_data_summary(config: dict, inv: dict, plans: list) -> str:
    """构建 LLM prompt 所需的数据摘要"""
    best = max(plans, key=lambda p: p["project_gross_profit"])
    units = config["units"]
    locs = " + ".join(f'{u["name"]}×{u["units"]}套' for u in units)
    total_area = sum(u["area"] for u in units)
    avg_price = sum(u["price_per_sqm"] * u["area"] for u in units) / total_area if total_area else 0
    total = inv["total_investment"]

    lines = [
        "## 项目数据",
        f"- 项目名称：{config['meta']['name']}",
        f"- 房源：{locs} | 总面积：{_fmt(total_area)}㎡ | 收购均价：{_fmt(avg_price)}万/㎡",
        f"- 收购总价：{_fmt(inv['total_acquisition'])}万元 | 装修：{_fmt(inv['total_decoration'])}万元 | 总投资：{_fmt(total)}万元",
        f"- 契税：{_fmt(inv['deed_tax'])}万元 | 印花税：{_fmt(inv['transaction_stamp'])}万元",
        "",
        "### 测算假设",
    ]
    dep = config["depreciation"]
    ops = config["operations"]
    taxes = config["taxes"]
    lines.append(f"- 折旧年限：{dep['building_life']}年 | 装修摊销：{dep['decoration_life']}年 | 残值率：{_pct(dep.get('residual_ratio',0))}")
    lines.append(f"- 运营成本占比：{_pct(ops['opex_ratio'])} | 租金调涨：每{ops['rent_adjust_period']}年{_pct(ops['rent_adjust_rate'])}")
    lines.append(f"- 契税：{_pct(taxes['deed_tax_rate'])} | 增值税：{_pct(taxes['vat_rate'])} | 房产税(从租)：{_pct(taxes['property_tax_lease'])}")

    lines.extend(["", "### 方案对比"])
    rate_map = {lp["id"]: lp["rate"] for lp in config["loan_plans"]}
    headers = ["指标"] + [p["plan"] for p in plans]
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("|" + "|".join("---" for _ in headers) + "|")
    for label, key in [
        ("贷款额", "loan_amount"), ("资本金", "equity"), ("利率", None),
        ("利息合计", "loan_total_interest"), ("租金合计", "total_rent"),
        ("运营成本", "total_opex"), ("运营毛利", "operating_profit_total"),
        ("出售毛利", "sale_profit"), ("出售收回", "sale_revenue"),
        ("项目整体毛利", "project_gross_profit"),
        ("现金流结余", "cash_flow_total"),
    ]:
        vals = [_pct(rate_map[p["plan"]]) if key is None else _fmt(p[key]) for p in plans]
        lines.append(f"| {label} | " + " | ".join(vals) + " |")

    lines.extend(["", "### 逐年经营明细"])
    for p in plans:
        lines.append(f"\n#### {p['plan']}方案")
        lines.append("| 年 | 租金 | 税费 | 折旧 | 运营成本 | 财务成本 | 还本 | 运营毛利 | 贷款余额 |")
        lines.append("|---|---|---|---|---|---|---|---|---|")
        for y in p["yearly"]:
            lines.append(f"| {y['year']} | {_fmt(y['rent_income'])} | {_fmt(y['tax'])} | {_fmt(y['depreciation'])} | {_fmt(y['opex'])} | {_fmt(y['finance_cost'])} | {_fmt(y['loan_principal'])} | {_fmt(y['operating_profit'])} | {_fmt(y['loan_balance'])} |")

    lines.extend(["", "### 各方案还款计划"])
    for p in plans:
        sched = [f"y{y['year']}={_fmt(y['loan_principal'])}" for y in p["yearly"]]
        lines.append(f"- {p['plan']}：{' / '.join(sched)}")

    # 各方案汇总指标
    lines.extend(["", "### 推荐方案"])
    lines.append(f"综合毛利最高的方案为**{best['plan']}**（{_fmt(best['project_gross_profit'])}万元），现金流结余{_fmt(best['cash_flow_total'])}万元")

    return "\n".join(lines)


def _call_llm(api_key: str, data_summary: str) -> str:
    """调用 NVIDIA GLM-5.2 生成国企上会汇报稿"""
    prompt = f"""你是一位国企投资分析师，负责撰写一份关于收购项目的测算分析报告，用于上会决策参考。

=== 格式要求 ===
标题：关于收购项目测算分析报告
全文用 Markdown 书写
章节用汉字编号：一、二、三、四、五、六、七
数据对比使用表格
关键数据用**加粗**

=== 章节内容要求（每章必须充分展开，不少于500字） ===
一、项目基本情况
包括但不限于：房源位置、套数、面积、收购单价、收购总价、装修成本、总投资额、契税、印花税等。用表格列出收购成本明细。

二、测算依据与假设条件
（1）折旧摊销假设：折旧年限、装修摊销年限、残值率
（2）运营参数假设：运营成本占比、租金调涨机制、出租率变化
（3）税费参数假设：各项税费率

三、投资成本构成
用表格列出各项支出的金额和占比，并简要分析。

四、融资方案对比分析
（1）用完整表格对比三个方案的贷款额、资本金、利率、利息合计、租金合计、运营成本、运营毛利、出售毛利、整体毛利、现金流结余等指标
（2）分别分析每个方案的特点，每个方案用3~5行展开说明
（3）重点说明各方案的财务成本差异和盈利能力差异

五、风险提示
分析以下三类风险，每类风险用3~5行展开：
（1）出租率风险：对项目收益的敏感度分析
（2）利率风险：当前利率环境及未来走势判断
（3）出售价格风险：期末售价波动的影响

六、结论与建议
（1）对比三个方案的综合表现（用表格）
（2）给出推荐方案及详细理由（数据支撑）
（3）后续工作建议

七、PPT汇报提纲（8页，每页标题+3~4个要点）

=== 写作风格 ===
- 国企公文风格，用词规范、数据严谨
- 每个章节充分展开，全文字数3000~5000字
- 避免以下用语："经过"、"进行了"、"在...方面"、"从...来看"、"针对"
- 形容方案时用"建议"、"倾向"、"综合来看"，不用"最优"、"最佳"
- 每个数据点要有上下文说明，不要孤立列数字
- 像一份完整的决策参考材料，而非摘要

=== 项目数据 ===
{data_summary}"""
    import httpx
    resp = httpx.post(
        _NVIDIA_API,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": "z-ai/glm-5.2",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 8192,
        },
        timeout=180,
    )
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def generate_report_llm(config: dict, result: dict, api_key: str = None) -> str:
    """LLM 增强版报告生成"""
    api_key = api_key or os.getenv("NVIDIA_API_KEY")
    if not api_key:
        return generate_report(config, result) + "\n\n> ⚠ 未配置 API Key，已降级为模板报告"
    plans = result.get("plans", [])
    inv = _inv_breakdown(config)
    data_summary = _build_data_summary(config, inv, plans)
    llm_report = _call_llm(api_key, data_summary)
    return llm_report


def generate_report(config: dict, result: dict) -> str:
    """生成完整分析报告 Markdown"""
    plans = result.get("plans", [])
    inv = _inv_breakdown(config)

    sections = [
        f"# {config['meta']['name']}",
        f"生成日期：{date.today().isoformat()}",
        "",
        _project_overview(config, inv),
        "",
        _assumptions(config),
        "",
        _cost_breakdown(inv),
        "",
        _plan_comparison(config, plans),
        "",
        _yearly_detail(plans),
        "",
        _evaluation(plans),
        "",
        _ppt_outline(config, inv, plans),
    ]
    return "\n".join(sections)


def generate_ppt_outline(config: dict, result: dict) -> str:
    """仅输出 PPT 大纲部分"""
    plans = result.get("plans", [])
    inv = _inv_breakdown(config)
    return _ppt_outline(config, inv, plans)
