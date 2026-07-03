"""保租房投资测算引擎 - 核心计算模块

把 Excel 的测算逻辑抽成函数，参数由模板 yaml 驱动。
所有金额单位: 万元
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import yaml

from . import engine


# ============ 数据结构 ============

@dataclass
class Unit:
    """房源单元"""
    name: str
    area: float                    # 建筑面积 ㎡
    units: int                     # 套数
    price_per_sqm: float           # 万元/㎡
    market_rent: float             # 元/㎡/月
    discount: float                # 折扣
    decoration_cost_per_sqm: float # 元/㎡
    avg_unit_price: float | None = None   # 户均收购价，自动算
    total_acquisition: float | None = None  # 收购总价，自动算
    decoration_total: float | None = None  # 装修合计，自动算

    def __post_init__(self):
        if self.total_acquisition is None:
            self.total_acquisition = round(self.area * self.price_per_sqm, 2)
        if self.avg_unit_price is None:
            self.avg_unit_price = round(self.total_acquisition / self.units, 2)
        if self.decoration_total is None:
            self.decoration_total = round(self.decoration_cost_per_sqm * self.area / 10000, 2)
        self.discounted_rent_per_sqm = round(self.market_rent * self.discount, 4)
        self.avg_area = self.area / self.units
        self.monthly_rent_per_unit = round(self.discounted_rent_per_sqm * self.avg_area, 4)


@dataclass
class TaxParams:
    deed_tax_rate: float
    transaction_stamp_rate: float
    loan_stamp_rate: float
    vat_rate: float
    rent_stamp_rate: float
    property_tax_lease: float
    property_tax_value: float
    land_tax_per_sqm: float
    land_area: float


@dataclass
class LoanPlan:
    id: str
    holding_years: int
    rate: float
    loan_ratio: float
    name: str = ""
    base_rate: float = 0.035
    discount_rate: float = 0.0
    # 还款节奏: custom(手填) | bullet(到期一次还本) | equal_principal(等额本金) | stepped(等额递增)
    repayment_type: str = "custom"
    repayment_schedule: dict = field(default_factory=dict)  # custom 模式逐年还本额
    repayment_start: float = 0.0    # stepped: 第2年还本起始额
    repayment_increment: float = 0.0  # stepped: 每年增量


# ============ 1. 投资成本 ============

def calc_investment(units: list[Unit], taxes: TaxParams) -> dict:
    """收购成本 + 装修 + 交易税费"""
    total_acquisition = sum(u.total_acquisition for u in units)
    total_decoration = sum(u.decoration_total for u in units)

    deed_tax = round(total_acquisition * taxes.deed_tax_rate, 2)          # 1094.4
    transaction_stamp = round(total_acquisition * taxes.transaction_stamp_rate, 4)  # 18.24

    # 折旧基数 = 收购款 - 契税（Excel: 36480-1094.4=35385.6, /30=1179.52）
    depreciation_base = total_acquisition - deed_tax

    return {
        "total_acquisition": total_acquisition,        # 36480
        "total_decoration": total_decoration,          # 1001
        "deed_tax": deed_tax,                          # 1094.4
        "transaction_stamp": transaction_stamp,        # 18.24
        "depreciation_base": depreciation_base,        # 35385.6
        "total_investment": round(total_acquisition + total_decoration, 2),  # 37481
    }


# ============ 2. 租金收入 ============

def calc_rent_income(unit: Unit, year: int, occupancy: float) -> float:
    """单年单区域租金收入（万元）

    Excel验证: 潍坊 第2年 0.85出租率
      4128.3元/月/套 * 144套 * 12月 * 0.85 / 10000 = 606.36 ✓
    """
    annual_rent = unit.monthly_rent_per_unit * unit.units * 12 / 10000  # 满租年租金 万元
    return round(annual_rent * occupancy, 6)


def get_rent_price_for_year(unit: Unit, year: int, adjust_period: int, adjust_rate: float) -> float:
    """计算某年的租金单价（含调整）

    Excel: 每5年调一次, 第6年开始涨5%
    第1-5年: 原价, 第6-10年: *1.05, 第11-15年: *1.05^2...
    """
    if year <= 1:
        return unit.discounted_rent_per_sqm
    steps = (year - 1) // adjust_period  # year6→steps=1, year11→steps=2
    return round(unit.discounted_rent_per_sqm * (1 + adjust_rate) ** steps, 4)


def get_occupancy(year: int, schedule: dict) -> float:
    """出租率"""
    key = f"year_{year}"
    if key in schedule:
        return schedule[key]
    return schedule.get("default", 0.95)


# ============ 3. 税费（运营期） ============

def calc_operating_tax(rent_income: float, taxes: TaxParams, unit: Unit,
                       occupancy: float = 0.95, total_acquisition: float = 0,
                       deed_tax: float = 0) -> float:
    """运营期税费（严格按Excel公式）

    Excel F30: =F19/(1+1.5%)*$C$14 + F19/(1+1.5%)*$G$14 + F19*$E$14
              + ($H$10+$C$13)*(1-F23)*$I$14 + $G$15*$E$15/10000

    拆解:
      F19/(1+1.5%)*增值税率        增值税及附加（含税租金剥离1.5%）
      F19/(1+1.5%)*租赁印花税率    租赁印花税
      F19*房产税(从租)率           房产税从租
      (收购款+契税)*(1-出租率)*从价率  房产税从价（对空置部分按房产余值计征）
      土地税单价*面积/10000        城镇土地使用税
    """
    rent_ex_vat = rent_income / (1 + 0.015)  # 含税租金剥离1.5%
    vat = rent_ex_vat * taxes.vat_rate
    rent_stamp = rent_ex_vat * taxes.rent_stamp_rate
    property_tax_lease = rent_income * taxes.property_tax_lease
    # 从价房产税: (收购款+契税) * 空置率 * 税率, I14=0.7*1.2%=0.0084
    property_tax_value = (total_acquisition + deed_tax) * (1 - occupancy) * taxes.property_tax_value
    land_tax = taxes.land_tax_per_sqm * taxes.land_area / 10000
    return round(vat + rent_stamp + property_tax_lease + property_tax_value + land_tax, 6)


# ============ 4. 折旧摊销 ============

def calc_depreciation(investment: dict, building_life: int, decoration_life: int) -> dict:
    """年折旧 + 年装修摊销

    Excel: 年折旧1179.52=(36480-1094.4)/30, 年摊销200.2=1001/5
    """
    building_annual = round(investment["depreciation_base"] / building_life, 2)
    decoration_annual = round(investment["total_decoration"] / decoration_life, 2)
    return {
        "building_annual": building_annual,     # 1179.52
        "decoration_annual": decoration_annual, # 200.2
        "total_annual": round(building_annual + decoration_annual, 2),  # 1379.72
    }


# ============ 5. 贷款财务成本 ============

def _build_repayment_schedule(plan: LoanPlan) -> dict:
    """根据还款类型生成逐年还本额 (year_N: 本金)

    四种节奏:
      custom         - 手填 repayment_schedule, 末年自动还清剩余
      bullet         - 中间全0, 末年还清全部本金
      equal_principal- 每年还本 = 贷款额/年限 (不含第1年, 第1年只付息)
      stepped        - 第2年起始额起, 每年+increment, 末年还清剩余
    """
    n = plan.holding_years
    if plan.repayment_type == "custom":
        return plan.repayment_schedule

    if plan.repayment_type == "bullet":
        # 末年还清, 其余0
        return {f"year_{i}": 0 for i in range(1, n)}

    if plan.repayment_type == "equal_principal":
        # 第1年只付息, 2~n年等额还本
        per = round(1.0 / (n - 1), 6) if n > 1 else 1.0
        return {f"year_{i}": per for i in range(2, n)}

    if plan.repayment_type == "stepped":
        # 第2年=start, 第3年=start+increment, ... 末年=-1(还清剩余)
        sched = {}
        for i in range(2, n):
            sched[f"year_{i}"] = round(plan.repayment_start + plan.repayment_increment * (i - 2), 2)
        return sched

    return plan.repayment_schedule


def calc_loan(plan: LoanPlan, loan_amount: float) -> dict:
    """贷款还本付息表

    Excel逻辑:
    - 年初余额 = 上年末余额
    - 本年应计利息 = 年初余额 * 利率
    - 本年还款 = schedule中的本金 + 利息 (或等本)
    - 本年还本 = schedule中的本金部分
    - 年末余额 = 年初余额 - 本年还本

    schedule 值含义:
      正数  - 该年还本额 (万元)
      -1    - 还清剩余全部
      0~1   - 小数视为贷款额的比例 (custom模式兼容手填比例)
    """
    schedule = _build_repayment_schedule(plan)
    rows = []
    balance = loan_amount

    for year in range(1, plan.holding_years + 1):
        scheduled = schedule.get(f"year_{year}", 0)
        # -1 或末年: 还清剩余
        if scheduled == -1 or year == plan.holding_years:
            principal = round(balance, 2)
        elif 0 < scheduled < 1:
            # 小数 = 贷款比例 (兼容手填)
            principal = round(loan_amount * scheduled, 2)
        else:
            principal = scheduled

        new_balance = round(balance - principal, 2)

        # 平均余额法计息: year1按半年(资金年中到位)
        if year == 1:
            interest = round(loan_amount * plan.rate * 0.5, 6)
        else:
            interest = round((balance + new_balance) / 2 * plan.rate, 6)

        balance = new_balance
        rows.append({
            "year": year,
            "begin_balance": round(balance + principal, 2),
            "interest": interest,
            "principal": principal,
            "end_balance": balance,
            "total_payment": round(interest + principal, 2),
        })

    total_interest = round(sum(r["interest"] for r in rows), 4)
    return {"schedule": rows, "total_interest": total_interest}


# ============ 6. 主测算函数 ============

def run_model(config: dict, loan_plan_id: str) -> dict:
    """跑一套完整测算"""
    # 构建对象
    units = [Unit(**u) for u in config["units"]]
    taxes = TaxParams(**config["taxes"])
    plan_cfg = next(p for p in config["loan_plans"] if p["id"] == loan_plan_id)
    plan = LoanPlan(**plan_cfg)

    # 1. 投资
    inv = calc_investment(units, taxes)
    total_investment = inv["total_investment"]

    # 3. 逐年现金流（提前取ops引用，贷款/折旧/现金流都用）
    ops = config["operations"]
    occ_schedule = ops["occupancy_schedule"]
    adjust_period = ops["rent_adjust_period"]
    adjust_rate = ops["rent_adjust_rate"]

    # 贷款 (loan_ratio = 贷款占总投资的比例)
    loan_amount = round(total_investment * plan.loan_ratio, 2)
    equity = round(total_investment - loan_amount, 2)
    loan = calc_loan(plan, loan_amount)

    # 借款合同印花税
    loan_stamp = round(loan_amount * taxes.loan_stamp_rate, 5)

    # 2. 折旧
    dep = calc_depreciation(inv, config["depreciation"]["building_life"],
                            config["depreciation"]["decoration_life"])

    yearly = []
    cumulative_dep = 0
    for year in range(1, plan.holding_years + 1):
        # 租金
        occ = get_occupancy(year, occ_schedule)
        rent_total = 0
        for u in units:
            rent_total += calc_rent_income(u, year, occ)

        # 税费: y1=收购阶段一次性(交易印花税+借款合同印花税), y2+=运营税
        if year == 1:
            tax = round(inv["transaction_stamp"] + loan_stamp, 6)
        else:
            tax = calc_operating_tax(rent_total, taxes, units[0], occ,
                                     inv["total_acquisition"], inv["deed_tax"])

        # 折旧摊销：第1年收购+装修未投入使用，不计提；第2年起计提
        # ponytail: 会计准则固定资产投入使用次月计提，Excel按第1年0折旧处理
        if year == 1:
            depreciation = 0
        else:
            depreciation = dep["total_annual"] if year <= config["depreciation"]["building_life"] + 1 else 0
        cumulative_dep += depreciation

        # 运营成本（付现10%）
        opex = round(rent_total * ops["opex_ratio"], 6)

        # 财务成本
        loan_row = loan["schedule"][year - 1]
        finance_cost = loan_row["interest"]

        # 运营毛利 = 收入 - 税费 - 折旧 - 运营成本 - 财务成本
        operating_profit = round(rent_total - tax - depreciation - opex - finance_cost, 6)

        yearly.append({
            "year": year,
            "rent_income": rent_total,
            "tax": tax,
            "depreciation": depreciation,
            "opex": opex,
            "finance_cost": finance_cost,
            "operating_profit": operating_profit,
            "loan_principal": loan_row["principal"],
            "loan_interest": loan_row["interest"],
            "loan_balance": loan_row["end_balance"],
        })

    # 4. 出售 - 严格对齐Excel: 投资出售毛利 = 累计折旧（折旧回血）
    # Excel: 出售收回=总投资37481, 投资出售毛利=累计折旧
    sale_revenue = total_investment
    sale_profit = cumulative_dep

    # 5. 汇总
    total_rent = round(sum(y["rent_income"] for y in yearly), 4)
    total_tax = round(sum(y["tax"] for y in yearly), 4)
    total_opex = round(sum(y["opex"] for y in yearly), 4)
    total_finance = round(sum(y["finance_cost"] for y in yearly), 4)
    operating_profit_total = round(sum(y["operating_profit"] for y in yearly), 4)

    # 税费合计: Excel口径=运营税费(不含契税印花税), 契税/印花税单独列
    total_tax_operating = round(total_tax - (inv["transaction_stamp"] + loan_stamp), 4)

    # 现金流（严格对齐Excel筹资sheet D25/D28）
    # D25 现金流结余 = 租金 - 财务成本 - 贷款本金 - 契税 - 交易印花税 - 借款印花税
    #                 - 运营成本 - 税费(运营期) - 资本金
    cash_flow_balance = round(
        total_rent - total_finance - loan_amount
        - inv["deed_tax"] - inv["transaction_stamp"] - loan_stamp
        - total_opex - total_tax_operating
        - equity,
        4
    )
    cash_flow_total = round(cash_flow_balance + sale_revenue, 4)

    return {
        "plan": plan.id,
        "total_investment": total_investment,
        "equity": equity,
        "loan_amount": loan_amount,
        "loan_total_interest": loan["total_interest"],
        "loan_stamp_tax": loan_stamp,
        "yearly": yearly,
        "total_rent": total_rent,
        "total_tax": total_tax,
        "total_opex": total_opex,
        "total_finance": total_finance,
        "operating_profit_total": operating_profit_total,
        "sale_revenue": sale_revenue,
        "sale_profit": sale_profit,
        "project_gross_profit": round(operating_profit_total + sale_profit, 4),
        "cash_flow_total": cash_flow_total,
        "cumulative_depreciation": cumulative_dep,
    }


def load_config(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


@engine("baozufang_v1")
def run(config: dict, loan_plan_id: str = None) -> dict:
    """平台入口: 接收完整模板参数, 返回测算结果

    若 loan_plan_id 为 None, 返回所有方案结果对比
    """
    if loan_plan_id is None:
        plans = [p["id"] for p in config["loan_plans"]]
        return {
            "plans": [run_model(config, pid) for pid in plans],
        }
    return run_model(config, loan_plan_id)


if __name__ == "__main__":
    cfg = load_config("templates/baozufang.yaml")
    for plan_id in ["3+3", "5year", "1+1+1+1+1"]:
        print(f"\n{'='*60}\n方案: {plan_id}\n{'='*60}")
        result = run_model(cfg, plan_id)
        print(f"总投资:       {result['total_investment']}")
        print(f"资本金:       {result['equity']}")
        print(f"贷款金额:     {result['loan_amount']}")
        print(f"贷款利息合计: {result['loan_total_interest']}")
        print(f"租金合计:     {result['total_rent']}")
        print(f"税费合计:     {result['total_tax']}")
        print(f"运营成本合计: {result['total_opex']}")
        print(f"财务成本合计: {result['total_finance']}")
        print(f"运营毛利合计: {result['operating_profit_total']}")
        print(f"出售收回:     {result['sale_revenue']}")
        print(f"投资出售毛利: {result['sale_profit']}")
        print(f"项目整体毛利: {result['project_gross_profit']}")
        print(f"现金流结余:   {result['cash_flow_total']}")

    # ponytail: 4种还款节奏自检
    print(f"\n{'='*60}\n还款节奏自检\n{'='*60}")
    for rtype, sched, start, inc in [
        ("custom", {"year_2": 154, "year_3": 203, "year_4": 254, "year_5": 260}, 0, 0),
        ("bullet", {}, 0, 0),
        ("equal_principal", {}, 0, 0),
        ("stepped", {}, 154, 50),
    ]:
        p = LoanPlan(id=rtype, holding_years=6, rate=0.0229, loan_ratio=0.36,
                     repayment_type=rtype, repayment_schedule=sched,
                     repayment_start=start, repayment_increment=inc)
        loan = calc_loan(p, 13493.09)
        prins = [f"y{r['year']}:{r['principal']:.0f}" for r in loan["schedule"]]
        print(f"{rtype:16s} 还本: {', '.join(prins)}  利息合计: {loan['total_interest']:.2f}")
