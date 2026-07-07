"""租赁运营测算引擎

收购存量房 → 装修 → 长期租赁运营。
支持: 税盾开关(折旧/利息抵扣), 亏损结转, 爬坡期, 周期性装修, 多方案对比。
"""
from __future__ import annotations
from typing import Any
import math
import numpy_financial as npf

from . import engine


# ============ 工具函数 ============

def _weighted_avg_occupancy(start_rate: float, end_rate: float,
                            total_months: int, year_months: int,
                            shift: int) -> float:
    """计算某年的加权平均出租率

    shift = 该年起始相对月份 - 爬坡起始相对月份
    shift < 0 的月份还没开始出租 → 0
    爬坡期内每月线性递增, 之后稳定在 end_rate
    """
    occ = 0
    for m in range(shift, shift + year_months):
        if m < 0:
            occ += 0  # 还没开始出租
        elif m >= total_months:
            occ += end_rate  # 爬坡结束,进入稳定期
        else:
            t = m / max(total_months - 1, 1)
            occ += start_rate + (end_rate - start_rate) * t
    return occ / year_months if year_months else 0


def _calc_loan(balance: float, rate: float, term_years: int,
               grace_years: int, repayment: dict) -> list[dict]:
    """贷款还本付息表

    - 宽限期内只付息
    - 还款计划用 repayment 字典 (year_N: 本金)
    - 平均余额法计息
    - -1 = 还清剩余
    """
    rows = []
    for y in range(1, term_years + 1):
        key = f"year_{y}"
        scheduled = repayment.get(key, 0)

        if y == 1:
            # 首年按半年计息(资金年中到位)
            interest = round(balance * rate * 0.5, 6)
        else:
            interest = round(balance * rate, 6)

        if y <= grace_years:
            principal = 0
        elif scheduled == -1 or y == term_years:
            principal = round(balance, 2)
        else:
            principal = min(scheduled, balance)

        new_balance = round(balance - principal, 2)

        if y > 1:
            # 平均余额法: 利息基于(年初+年末)/2
            interest = round((balance + new_balance) / 2 * rate, 6)

        rows.append({
            "year": y,
            "begin_balance": round(balance, 2),
            "interest": interest,
            "principal": principal,
            "end_balance": new_balance,
            "total_payment": round(principal + interest, 2),
        })
        balance = new_balance

    return rows


def _calc_irr(cf: list[float]) -> float:
    if not any(v != 0 for v in cf):
        return 0
    pos = sum(1 for v in cf if v > 0)
    neg = sum(1 for v in cf if v < 0)
    if pos == 0 or neg == 0:
        return 0
    return round(npf.irr(cf), 6)


def _calc_payback(cf: list[float]) -> int | None:
    cum = 0
    for y, v in enumerate(cf):
        cum += v
        if cum >= 0 and y > 0:
            return y
    return None


# ============ 主测算 ============

def run_model(config: dict, scenario_id: str = None) -> dict:
    """跑一套完整测算"""
    acq = config["acquisition"]
    renov = config["renovation"]
    dep_cfg = config["depreciation"]
    rent_cfg = config["rental"]
    ramp = config["ramp_up"]
    loan_cfg = config["loan"]
    tax_cfg = config.get("tax", {})
    sale_cfg = config.get("sale", {})

    total_years = config["project"]["total_years"]
    tax_rate = tax_cfg.get("income_tax_rate", 0.25)
    tax_shield = tax_cfg.get("tax_shield", True)
    loss_cf = tax_cfg.get("loss_carryforward", True)
    cf_years = tax_cfg.get("carryforward_years", 5)

    vat_rate = tax_cfg.get("vat_rate", 0.09)
    pt_rate = tax_cfg.get("property_tax_rate", 0.12)
    sur_rate = tax_cfg.get("surcharge_rate", 0.12)
    sd_rate = tax_cfg.get("stamp_duty_rate", 0.001)

    # ---------- 场景覆盖 ----------
    if scenario_id:
        sc = next((s for s in config.get("scenarios", []) if s["id"] == scenario_id), None)
        if sc:
            sr = sc.get("rental", {})
            if "occupancy_stable" in sr:
                rent_cfg = {**rent_cfg, "occupancy_stable": sr["occupancy_stable"]}
            if "rent_discount" in sr:
                rent_cfg = {**rent_cfg, "rent_discount": sr["rent_discount"]}

    occupancy_stable = rent_cfg["occupancy_stable"]
    rent_discount = rent_cfg.get("rent_discount", 1.0)
    monthly_full = rent_cfg["monthly_rent_full"] * rent_discount

    # ---------- 爬坡期: 逐月出租率 → 逐年 ----------
    ramp_months = ramp["months"]
    ramp_start = ramp["start_rate"]
    ramp_end = occupancy_stable

    # 会计期间: 全部按12个月(年), 首年贷款按半年计息
    # Excel列: 2024(7.1)→2049(6.30) = 25年 = 26个年度列
    # rent在year 1(2024)为0(装修), year 2起租
    year_months_list = [12] * total_years
    # 按日历年度: month 0 = Jan 2024
    year_start_month = list(range(0, total_years * 12, 12))

    # 爬坡期从2025.5开始 = month 16 (Jan 2024 + 16 months = May 2025)
    ramp_start_month = 16

    # 计算逐年出租率
    yearly_occupancy = []
    for y in range(total_years):
        sm = year_start_month[y] - ramp_start_month  # 相对爬坡起点
        ym = year_months_list[y]
        if sm + ym <= 0:
            # 完全在爬坡前 → 0
            occ = 0
        elif sm >= ramp_months:
            # 完全在爬坡后 → 稳定
            occ = occupancy_stable
        else:
            occ = _weighted_avg_occupancy(ramp_start, occupancy_stable,
                                          ramp_months, ym, sm)
        yearly_occupancy.append(occ)

    # ---------- 折旧摊销 ----------
    building_life = dep_cfg["building_life"]
    decor_life = dep_cfg["decoration_life"]
    building_dep = round(acq["total_price"] / building_life, 2)

    # 装修摊销: 首次33600, 每5年续5600, 摊销n年
    # 首轮: year 2-6 (6720/yr)
    # 次轮: year 7-11 (1120/yr)
    # ...
    def _decor_amort(year_idx: int) -> float:
        """装修摊销(非付现)

        首次 33600 从 year 2(2025) 起摊 5年, 6720/yr
        每5年续 5600 从安装当年起摊 5年, 1120/yr
        不重叠: 首次摊完(yr 1-5) → 续期(yr 6+)
        """
        if year_idx == 0:
            return 0  # year 1 还没装修
        total = 0
        # 首次: year_idx 1-5 (2025-2029)
        if year_idx <= decor_life:
            total += round(renov["initial_cost"] / decor_life, 2)
        # 周期性: 每 cycle_years 年续一次
        for cycle in range(1, 10):
            install = 1 + cycle * renov["cycle_years"]
            if install <= year_idx < install + decor_life:
                total += round(renov["cycle_cost"] / decor_life, 2)
        return total

    # ---------- 贷款 ----------
    loan_amount = acq["loan_amount"]
    loan_schedule = _calc_loan(loan_amount, loan_cfg["rate"],
                                total_years, loan_cfg["grace_years"],
                                loan_cfg.get("repayment", {}))

    # ---------- 逐年现金流 ----------
    equity = round(acq["total_price"] * (1 - acq["equity_ratio"]), 2)
    # 自有资金 = 收购自有20% + 首次装修
    initial_equity = round(acq["total_price"] * acq["equity_ratio"], 2)

    yearly = []
    cum_loss = 0.0  # 累计可抵扣亏损

    for y in range(total_years):
        year_num = y + 1
        occ = yearly_occupancy[y]
        ym = year_months_list[y]

        # --- 租金收入 ---
        rent = round(monthly_full * ym * occ, 6)

        # --- 租金增长(每2年+2%, 从稳定期开始) ---
        # Excel: 2027年开始涨, 每2年2%
        # 稳定年份 = 3 (2027)
        if year_num >= 3:
            growth_steps = (year_num - 3) // rent_cfg["growth_interval"]
            growth_mult = (1 + rent_cfg["growth_rate"]) ** growth_steps
            rent = round(monthly_full * ym * occ * growth_mult, 6)

        # --- 运营成本(付现) ---
        opex = round(rent * config["operating_cost_ratio"], 6)

        # --- 增值税/房产税/附加/印花税 ---
        vat = round(rent * vat_rate, 6) if vat_rate > 0 else 0
        surcharge = round(vat * sur_rate, 6) if vat_rate > 0 and sur_rate > 0 else 0
        property_tax = round(rent * pt_rate, 6) if pt_rate > 0 else 0
        stamp_duty = round(rent * sd_rate, 6) if sd_rate > 0 else 0
        turnover_taxes = round(vat + surcharge + property_tax + stamp_duty, 6)

        # --- 装修支出(付现) ---
        renov_capex = 0
        if y == 1:  # year 2 = 2025, 首次装修
            renov_capex = renov["initial_cost"]
        else:
            for cycle in range(1, 10):
                install_year = 1 + cycle * renov["cycle_years"]
                if y == install_year:
                    renov_capex = renov["cycle_cost"]
                    break

        # --- 折旧摊销(非付现) ---
        dep = round(building_dep, 2) if y >= 0 else 0
        amort = round(_decor_amort(y), 2)
        total_dep = round(dep + amort, 2)

        # --- 贷款 ---
        loan_row = loan_schedule[y]
        interest = loan_row["interest"]
        principal = loan_row["principal"]

        # --- 税前利润 ---
        if tax_shield:
            # 税盾ON: 折旧+利息+流转税在税前扣除
            profit_bt = round(rent - opex - total_dep - interest - property_tax - surcharge - stamp_duty, 6)
        else:
            # 税盾OFF: 折旧+利息不扣除, 流转税仍可扣除
            profit_bt = round(rent - opex - property_tax - surcharge - stamp_duty, 6)

        # --- 所得税 ---
        if tax_shield and loss_cf:
            # 亏损结转
            taxable = max(0, profit_bt)
            if cum_loss > 0 and taxable > 0:
                offset = min(taxable, cum_loss)
                taxable = round(taxable - offset, 6)
                cum_loss = round(cum_loss - offset, 6)
            income_tax = round(taxable * tax_rate, 6)
            if profit_bt < 0:
                cum_loss = round(cum_loss + abs(profit_bt), 6)
        else:
            income_tax = round(max(0, profit_bt) * tax_rate, 6)

        # --- 净利润 ---
        net_profit = round(profit_bt - income_tax, 6)

        # --- 现金流 ---
        # 项目现金净流量 = 租金 - 运营成本 - 装修 - 利息 - 还本 - 流转税 - 所得税
        cf = round(rent - opex - renov_capex - interest - principal - turnover_taxes - income_tax, 6)

        yearly.append({
            "year": year_num,
            "calendar_year": config["project"]["start_year"] + y,
            "occupancy": occ,
            "rent_income": rent,
            "opex": opex,
            "depreciation": dep,
            "amortization": amort,
            "total_depreciation": total_dep,
            "renovation_capex": renov_capex,
            "loan_interest": interest,
            "loan_principal": principal,
            "loan_balance": loan_row["end_balance"],
            "profit_bt": profit_bt,
            "income_tax": income_tax,
            "vat": vat,
            "property_tax": property_tax,
            "surcharge": surcharge,
            "stamp_duty": stamp_duty,
            "turnover_taxes": turnover_taxes,
            "net_profit": net_profit,
            "cash_flow": cf,
            "cumulative_loss": cum_loss if tax_shield and loss_cf else 0,
        })

    # ---------- 合计 ----------
    total_rent = round(sum(y["rent_income"] for y in yearly), 4)
    total_opex = round(sum(y["opex"] for y in yearly), 4)
    total_dep = round(sum(y["total_depreciation"] for y in yearly), 4)
    total_renov = round(sum(y["renovation_capex"] for y in yearly), 4)
    total_interest = round(sum(y["loan_interest"] for y in yearly), 4)
    total_principal = round(sum(y["loan_principal"] for y in yearly), 4)
    total_tax = round(sum(y["income_tax"] for y in yearly), 4)
    total_vat = round(sum(y["vat"] for y in yearly), 4)
    total_pt = round(sum(y["property_tax"] for y in yearly), 4)
    total_sur = round(sum(y["surcharge"] for y in yearly), 4)
    total_sd = round(sum(y["stamp_duty"] for y in yearly), 4)
    total_profit = round(sum(y["net_profit"] for y in yearly), 4)

    # 项目现金净流量(Excel: Y1= Equity+Interest, Y2+=租-成本)
    cf_list = [round(-initial_equity + yearly[0]["cash_flow"], 6)]
    for y in yearly[1:]:
        cf_list.append(y["cash_flow"])

    cumulative_cf = []
    cum = 0
    for v in cf_list:
        cum += v
        cumulative_cf.append(round(cum, 4))
    cumulative_cf_annual = cumulative_cf[-1] if cumulative_cf else 0

    # 项目IRR
    irr = _calc_irr(cf_list)
    # 静态回收期
    payback = _calc_payback(cf_list)

    # ---------- 期末出售(可选) ----------
    sale_revenue = 0
    sale_profit = 0
    if sale_cfg.get("enabled", False):
        premium = sale_cfg.get("price_premium", 0)
        sale_revenue = round(acq["total_price"] * (1 + premium) + total_dep, 2)
        sale_profit = total_dep

    # ---------- 税盾省税额 ----------
    # 无税盾情景下的应纳税额对比
    tax_no_shield = 0
    for y in yearly:
        p = round(y["rent_income"] - y["opex"], 6)
        tax_no_shield += max(0, p) * tax_rate

    total_investment = round(initial_equity + renov["initial_cost"], 2)
    return {
        "scenario": scenario_id or "default",
        "project": config["project"]["name"],
        "total_years": total_years,
        "initial_equity": initial_equity,
        "initial_renovation": renov["initial_cost"],
        "total_investment": total_investment,
        "loan_amount": loan_amount,
        "total_rent": total_rent,
        "total_opex": total_opex,
        "total_depreciation": total_dep,
        "total_renovation": total_renov,
        "total_interest": total_interest,
        "total_principal": total_principal,
        "total_tax": total_tax,
        "total_vat": total_vat,
        "total_property_tax": total_pt,
        "total_surcharge": total_sur,
        "total_stamp_duty": total_sd,
        "total_net_profit": total_profit,
        "sale_revenue": sale_revenue,
        "sale_profit": sale_profit,
        "project_gross_profit": round(total_profit + sale_profit, 4),
        "cumulative_cash_flow": cumulative_cf_annual,
        "irr": irr,
        "irr_pct": round(irr * 100, 2),
        "payback_year": payback,
        "yearly": yearly,
        "cumulative_cf": cumulative_cf,
        "loan_schedule": loan_schedule,
        # 税盾对比
        "tax_shield_enabled": tax_shield,
        "loss_carryforward": loss_cf,
        "tax_no_shield": round(tax_no_shield, 4),
        "tax_shield_saving": round(max(0, tax_no_shield - total_tax), 4),
    }


@engine("zulin_v1")
def run(config: dict, plan_id: str = None) -> dict:
    """平台入口

    如果 config 含 scenarios, 跑所有方案对比;
    否则跑单一方案。
    """
    scenarios = config.get("scenarios", [])
    if not scenarios or plan_id:
        sid = plan_id or "default"
        return run_model(config, sid)

    results = []
    for sc in scenarios:
        r = run_model(config, sc["id"])
        results.append(r)
    return {"plans": results}


if __name__ == "__main__":
    import yaml, sys
    path = sys.argv[1] if len(sys.argv) > 1 else "templates/zulin.yaml"
    with open(path) as f:
        cfg = yaml.safe_load(f)

    scenarios = cfg.get("scenarios", [])
    if scenarios:
        for sc in scenarios:
            r = run_model(cfg, sc["id"])
            y = r["yearly"]
            print(f"\n{'='*60}")
            print(f"方案: {sc['name']}")
            print(f"{'='*60}")
            print(f"IRR:         {r['irr_pct']}%")
            print(f"累计净现金流: {r['cumulative_cash_flow']:.0f} 万元")
            print(f"静态回收期:   {r['payback_year']}年" if r['payback_year'] else "未回收")
            print(f"所得税合计:   {r['total_tax']:.0f} 万元")
            print(f"租金合计:     {r['total_rent']:.0f} 万元")
            print(f"利息合计:     {r['total_interest']:.0f} 万元")
            print(f"运营成本合计: {r['total_opex']:.0f} 万元")
            print(f"装修合计:     {r['total_renovation']:.0f} 万元")
            print(f"折旧合计:     {r['total_depreciation']:.0f} 万元")
            print(f"税盾省税:     {r['tax_shield_saving']:.0f} 万元" if r['tax_shield_enabled'] else "税盾关闭")
            print(f"\n第1年现金净流量: {y[0]['cash_flow']:.0f}")
            print(f"第2年: {y[1]['cash_flow']:.0f} (租金{y[1]['rent_income']:.0f}, 出租率{y[1]['occupancy']*100:.0f}%)")
            print(f"第3年: {y[2]['cash_flow']:.0f} (租金{y[2]['rent_income']:.0f}, 出租率{y[2]['occupancy']*100:.0f}%)")
    else:
        r = run_model(cfg)
        print(f"\nIRR: {r['irr_pct']}%")
        print(f"累计净现金流: {r['cumulative_cash_flow']:.0f}")
        print(f"回收期: {r['payback_year']}年")
