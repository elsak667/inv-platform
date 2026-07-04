"""房地产开发项目全成本测算引擎

流水线: 土地成本 → 建安 → 三费 → 融资 → 销售 → 税金 → 现金流 → 盈利
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import numpy_financial as npf
import math

try:
    from . import engine
except ImportError:
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
    from engines import engine


# ============ S曲线权重 ============

def _s_curve_weights(n: int, k: float = 6.0) -> list[float]:
    if n <= 1:
        return [1.0]
    raw = [0.0] * n
    for i in range(n):
        x = (i + 0.5) / n
        raw[i] = 1 / (1 + math.exp(-k * (x - 0.5) * 2))
    s = sum(raw)
    return [round(w / s, 6) for w in raw]


# ============ 数据结构 ============

@dataclass
class Product:
    name: str
    type: str
    gfa: float
    saleable_area: float
    unit_price: float = 0
    unit_price_ex_vat: float = 0
    const_cost_per_sqm: float = 0
    parking_spots: int = 0
    parking_price: float = 0
    parking_price_ex_vat: float = 0
    decoration: str = "毛坯"
    presale_month_offset: int = 0

    def __post_init__(self):
        if not self.unit_price_ex_vat:
            self.unit_price_ex_vat = round(self.unit_price / 1.09, 2)
        if self.parking_price and not self.parking_price_ex_vat:
            self.parking_price_ex_vat = round(self.parking_price / 1.09, 2)


@dataclass
class LandParams:
    site_area: float
    construction_area: float
    floor_area_ratio: float
    total_gfa: float
    premium: float
    deed_tax_rate: float
    city_support_fee_per_sqm: float
    other_land_cost: float


@dataclass
class FeeParams:
    management_fee_rate: float
    marketing_fee_rate: float
    agency_fee_rate: float
    preliminary_rate: float
    contingency_rate: float
    indirect_dev_rate: float


@dataclass
class FinancingParams:
    equity_ratio: float
    dev_loan_interest_rate: float
    dev_loan_term_months: int
    dev_loan_to_value: float
    # 前融(过桥贷款)
    bridge_loan_ratio: float = 0  # 占土地款比例
    bridge_loan_rate: float = 0   # 年利率
    bridge_loan_term: int = 12    # 期限月


@dataclass
class SalesParams:
    sell_period_months: int
    front_payment_ratio: float
    mortgage_ratio: float
    mortgage_release_delay: int


@dataclass
class TaxParams:
    vat_rate: float = 0.09
    vat_rate_services: float = 0.06
    vat_prepay_rate: float = 0.03
    conversion_rate: float = 0.85
    invoice_rate: float = 1.0
    city_maintenance_rate: float = 0.05
    edu_surcharge_rate: float = 0.03
    local_edu_surcharge_rate: float = 0.02
    land_tax_prepay_rate: float = 0.02
    land_tax_prepay_commercial: float = 0.03
    income_tax_rate: float = 0.25
    stamp_tax_rate: float = 0.0005
    # backward compat: if set > 0 overrides individual rates
    vat_additional_rate: float = -1

    def __post_init__(self):
        # backward compat: old templates pass vat_additional_rate directly
        if self.vat_additional_rate <= 0:
            self.vat_additional_rate = round(
                self.city_maintenance_rate + self.edu_surcharge_rate
                + self.local_edu_surcharge_rate, 4
            )


# ============ 1. 土地成本 ============

def calc_land_cost(land: LandParams) -> dict:
    total_gfa = land.total_gfa or land.site_area * land.floor_area_ratio
    premium = land.premium
    deed_tax = round(premium * land.deed_tax_rate, 2)
    above_gfa = total_gfa * 0.7  # 地上面积估算
    city_fee = round(above_gfa * land.city_support_fee_per_sqm / 10000, 2)
    other = land.other_land_cost
    total = round(premium + deed_tax + city_fee + other, 2)
    return {
        "premium": premium,
        "deed_tax": deed_tax,
        "city_support_fee": city_fee,
        "other": other,
        "total": total,
        "cost_per_gfa": round(total / total_gfa * 10000, 2) if total_gfa else 0,
    }


# ============ 2. 建安成本 ============

def calc_construction(products: list[Product]) -> dict:
    items = []
    total_const = 0
    total_gfa = 0
    for p in products:
        cost = round(p.gfa * p.const_cost_per_sqm / 10000, 2)
        items.append({
            "name": p.name,
            "gfa": p.gfa,
            "const_cost_per_sqm": p.const_cost_per_sqm,
            "total": cost,
        })
        total_const += cost
        total_gfa += p.gfa
    return {
        "items": items,
        "total": total_const,
        "avg_cost_per_sqm": round(total_const / total_gfa * 10000, 2) if total_gfa else 0,
    }


# ============ 3. 前期+间接+不可预见费 ============

def calc_other_direct(constr: dict, fees: FeeParams) -> dict:
    base = constr["total"]
    preliminary = round(base * fees.preliminary_rate, 2)
    contingency = round((base + preliminary) * fees.contingency_rate, 2)
    indirect = round((base + preliminary + contingency) * fees.indirect_dev_rate, 2)
    return {
        "preliminary": preliminary,
        "contingency": contingency,
        "indirect_dev": indirect,
        "total": round(preliminary + contingency + indirect, 2),
    }


# ============ 4. 销售收入 ============

def calc_sales(products: list[Product]) -> dict:
    total_revenue = 0
    total_revenue_ex_vat = 0
    items = []
    for p in products:
        if p.type == "车库":
            rev = round(p.parking_spots * p.parking_price / 10000, 2)
            rev_ex = round(p.parking_spots * p.parking_price_ex_vat / 10000, 2)
        else:
            rev = round(p.saleable_area * p.unit_price / 10000, 2)
            rev_ex = round(p.saleable_area * p.unit_price_ex_vat / 10000, 2)
        items.append({
            "name": p.name,
            "revenue": rev,
            "revenue_ex_vat": rev_ex,
        })
        total_revenue += rev
        total_revenue_ex_vat += rev_ex
    return {
        "items": items,
        "total": total_revenue,
        "total_ex_vat": total_revenue_ex_vat,
    }


# ============ 5. 三费 ============

def calc_fees(sales: dict, land_cost: dict, constr: dict,
              other_direct: dict, fees: FeeParams) -> dict:
    """期间费用: 管理 + 营销 + 代建"""
    base = sales["total"]
    management = round(base * fees.management_fee_rate, 2)
    marketing = round(base * fees.marketing_fee_rate, 2)
    agency = round(base * fees.agency_fee_rate, 2)
    return {
        "management": management,
        "marketing": marketing,
        "agency": agency,
        "total": round(management + marketing + agency, 2),
        "total_ex_vat": round(
            (management + marketing + agency) / 1.06, 2
        ),
    }


# ============ 6. 增值税完整链条（P2） ============

def calc_vat_full(sales: dict, land_cost: dict, constr: dict,
                  other_direct: dict, period_fees: dict,
                  products: list[Product], taxes: TaxParams) -> dict:
    """完整增值税链条: 销项(含土地抵减) → 进项(5类) → 应纳 → 附加税

    P&L 用 清算值, 现金流用 预征值
    """
    total_rev = sales["total"]
    premium = land_cost["premium"]

    # --- 土地价款抵减销项税额 ---
    # 可售面积(不含无产权车位)
    saleable_area = sum(p.saleable_area for p in products)
    land_deduction = round(premium, 2)

    # --- 销项税额 ---
    if total_rev <= land_deduction:
        output_vat = 0.0
    else:
        output_vat = round((total_rev - land_deduction) / (1 + taxes.vat_rate) * taxes.vat_rate, 2)
    revenue_ex_vat = round(total_rev - output_vat, 2)

    # --- 进项税额 ---
    def _input_vat(cost, rate, apply_cr=True, apply_ir=True):
        cr = taxes.conversion_rate if apply_cr else 1.0
        ir = taxes.invoice_rate if apply_ir else 1.0
        if cost <= 0:
            return 0.0
        return round(cost * cr * ir / (1 + rate) * rate, 2)

    # 建安 9%
    iv_const = _input_vat(constr["total"], taxes.vat_rate)
    # 前期 6%
    iv_pre = _input_vat(other_direct["preliminary"], taxes.vat_rate_services)
    # 不可预见 9% (同建安)
    iv_cont = _input_vat(other_direct["contingency"], taxes.vat_rate)
    # 间接开发 6%
    iv_ind = _input_vat(other_direct["indirect_dev"], taxes.vat_rate_services)
    # 管理 6% (XLCS: 无取票率)
    iv_mgmt = _input_vat(period_fees["management"], taxes.vat_rate_services, apply_ir=False)
    # 营销 6% (XLCS: 无取票率)
    iv_mkt = _input_vat(period_fees["marketing"], taxes.vat_rate_services, apply_ir=False)

    input_vat_total = round(iv_const + iv_pre + iv_cont + iv_ind + iv_mgmt + iv_mkt, 2)

    # --- 应纳增值税 = max(0, 销项 − 进项) ---
    vat_payable = max(0, round(output_vat - input_vat_total, 2))

    # --- 附加税 ---
    surtax = round(vat_payable * taxes.vat_additional_rate, 2)

    # --- 不含税成本 ---
    constr_ex_vat = round(constr["total"] - iv_const, 2)
    pre_ex_vat = round(other_direct["preliminary"] - iv_pre, 2)
    cont_ex_vat = round(other_direct["contingency"] - iv_cont, 2)
    ind_ex_vat = round(other_direct["indirect_dev"] - iv_ind, 2)
    mgmt_ex_vat = round(period_fees["management"] - iv_mgmt, 2)
    mkt_ex_vat = round(period_fees["marketing"] - iv_mkt, 2)

    return {
        "land_deduction": land_deduction,
        "output_vat": output_vat,
        "revenue_ex_vat": revenue_ex_vat,
        "input_vat": {
            "construction": iv_const,
            "preliminary": iv_pre,
            "contingency": iv_cont,
            "indirect_dev": iv_ind,
            "management": iv_mgmt,
            "marketing": iv_mkt,
            "total": input_vat_total,
        },
        "vat_payable": vat_payable,
        "surtax": surtax,
        "surtax_rate": taxes.vat_additional_rate,
        "cost_ex_vat": {
            "construction": constr_ex_vat,
            "preliminary": pre_ex_vat,
            "contingency": cont_ex_vat,
            "indirect_dev": ind_ex_vat,
            "management": mgmt_ex_vat,
            "marketing": mkt_ex_vat,
            "total": round(constr_ex_vat + pre_ex_vat + cont_ex_vat + ind_ex_vat
                           + mgmt_ex_vat + mkt_ex_vat, 2),
        },
    }


# ============ 7a. 土地增值税清算（P2.5） ============

def calc_land_tax_settlement(sales: dict, land_cost: dict, constr: dict,
                              other_direct: dict, products: list[Product],
                              vat_result: dict, taxes: TaxParams) -> dict:
    """四级超率累进 + 三分法清算

    LAT_LIABILITIES = N
    Deduction = A + B + C + D + E
      A = 取得土地使用权成本
      B = 房地产开发成本(不含三费)
      C = 房地产开发费用 = (A+B)*10%
      D = 与转让相关的税金(附加税)
      E = 加计扣除 = (A+B)*20%
    Excess = Revenue - Deduction
    Rate = 30% if excess/deduction ≤ 50%
           40% if ≤ 100%
           50% if ≤ 200%
           60% if > 200%
    Tax = Excess * Rate - Deduction * 速算
    """
    vat = vat_result or {}
    cv = vat.get("cost_ex_vat", {})

    # dev cost 不含税(不含三费: mgmt/mkt/agency)
    dev_cost = round(
        cv.get("construction", 0) + cv.get("preliminary", 0)
        + cv.get("contingency", 0) + cv.get("indirect_dev", 0), 2
    )

    total_gfa = sum(p.gfa for p in products)
    total_surtax = vat.get("surtax", 0)
    # 可售GFA（不含车库, 土增税中车库一般不分配土地成本）
    saleable_gfa = sum(p.gfa for p in products if p.type != "车库")

    # 分类: 普通住宅/非普通住宅/其他
    ord = [p for p in products if p.type == "住宅"]
    non_ord = [p for p in products if p.type == "商业"]
    other = [p for p in products if p.type == "车库"]

    def _revenue(ps: list[Product]) -> float:
        rev = 0
        for p in ps:
            if p.type == "车库":
                rev += p.parking_spots * p.parking_price / 10000
            else:
                rev += p.saleable_area * p.unit_price / 10000
        return round(rev, 2)

    def _revenue_ex_vat(ps: list[Product]) -> float:
        rev = 0
        for p in ps:
            if p.type == "车库":
                rev += p.parking_spots * p.parking_price_ex_vat / 10000
            else:
                rev += p.saleable_area * p.unit_price_ex_vat / 10000
        return round(rev, 2)

    def _gfa(ps: list[Product]) -> float:
        return sum(p.gfa for p in ps)

    def _calc_lat(revenue_ex_vat: float, product_type: str, gfa_share: float, surtax_share: float) -> dict:
        if revenue_ex_vat <= 0 or gfa_share <= 0:
            return {"revenue": 0, "deduction": 0, "excess": 0, "rate": 0, "tax": 0, "excess_ratio": 0}

        # A: 土地 — 车库一般不分配土地成本, 按可售建面分摊
        land_denom = saleable_gfa if product_type == "车库" else saleable_gfa
        a = round(land_cost["total"] * (0 if product_type == "车库" else gfa_share / saleable_gfa), 2) if saleable_gfa else 0
        # B: 开发成本(按总建面分摊)
        b = round(dev_cost * gfa_share / total_gfa, 2) if total_gfa else 0
        # C: 开发费用
        c = round((a + b) * 0.10, 2)
        # D: 税金
        d = surtax_share
        # E: 加计扣除
        e = round((a + b) * 0.20, 2)

        deduction = round(a + b + c + d + e, 2)
        excess = round(revenue_ex_vat - deduction, 2)
        excess_ratio = max(0, round(excess / deduction, 4)) if deduction > 0 else 0

        if excess <= 0:
            return {"revenue": revenue_ex_vat, "deduction": deduction, "excess": 0, "rate": 0, "tax": 0, "excess_ratio": 0}

        if excess_ratio <= 0.50:
            rate, quick = 0.30, 0
        elif excess_ratio <= 1.00:
            rate, quick = 0.40, 0.05
        elif excess_ratio <= 2.00:
            rate, quick = 0.50, 0.15
        else:
            rate, quick = 0.60, 0.35

        tax = round(excess * rate - deduction * quick, 2)
        return {
            "revenue": revenue_ex_vat, "deduction": deduction,
            "excess": excess, "excess_ratio": excess_ratio,
            "rate": rate, "tax": max(0, tax),
        }

    ord_result = {"type": "普通住宅", "products": [p.name for p in ord]}
    non_ord_result = {"type": "非普通住宅", "products": [p.name for p in non_ord]}
    other_result = {"type": "其他", "products": [p.name for p in other]}

    total_revenue_ex_vat = 0
    types_total = 0

    for ps, result, ptype in [(ord, ord_result, "住宅"), (non_ord, non_ord_result, "商业"), (other, other_result, "车库")]:
        if not ps:
            continue
        rev_ex = _revenue_ex_vat(ps)
        gfa_share = _gfa(ps)
        rev_incl = _revenue(ps)
        surtax_share = round(total_surtax * rev_ex / max(sales.get("total_ex_vat", 1), 1), 2) if total_surtax else 0
        lat = _calc_lat(rev_ex, ptype, gfa_share, surtax_share)
        result.update({
            "revenue_ex_vat": rev_ex,
            "gfa": gfa_share,
            "surtax_share": surtax_share,
            **lat,
        })
        total_revenue_ex_vat += rev_ex
        types_total += lat["tax"]

    total = round(types_total, 2)

    return {
        "total": total,
        "types": [ord_result, non_ord_result, other_result],
        "details": {
            "land_cost": land_cost["total"],
            "dev_cost_ex_vat": dev_cost,
            "total_surtax": total_surtax,
        },
    }


# ============ 7b. 税金计算（P2: 完整税链） ============

def calc_taxes(sales: dict, land_cost: dict, constr: dict,
               other_direct: dict, period_fees: dict,
               products: list[Product], taxes: TaxParams,
               vat_result: dict = None) -> dict:
    """完整税金链: 增值税(清算) + 附加税 + 土增税(预征+清算) + 印花税

    清算 → 利润表,  预征 → 现金流
    """
    total_revenue = sales["total"]
    vat = vat_result or {}

    # --- 增值税 (P2: 用清算值) ---
    vat_payable = vat.get("vat_payable", round(total_revenue * taxes.vat_prepay_rate, 2))
    surtax = vat.get("surtax", round(vat_payable * taxes.vat_additional_rate, 2))

    # --- 土增税预征(现金流) ---
    land_prepay = 0
    for p in products:
        rate = taxes.land_tax_prepay_commercial if p.type == "商业" else taxes.land_tax_prepay_rate
        if p.type == "车库":
            rev = round(p.parking_spots * p.parking_price / 10000, 2)
        else:
            rev = round(p.saleable_area * p.unit_price / 10000, 2)
        land_prepay += round(rev * rate, 2)

    # --- 土增税清算(P2.5) ---
    lat_result = calc_land_tax_settlement(sales, land_cost, constr, other_direct,
                                           products, vat, taxes)
    land_settlement = lat_result["total"]

    # --- 印花税 ---
    stamp = round(total_revenue * taxes.stamp_tax_rate, 2)

    # --- 利润表税金合计(不含增值税本体) ---
    total_pl = round(surtax + land_settlement + stamp, 2)

    # --- 预缴增值税(按月) ---
    prepay_vat_total = round(total_revenue / (1 + taxes.vat_rate) * taxes.vat_prepay_rate, 2)

    # --- 清算找差(交付时补缴) ---
    settlement_diff = round(land_settlement - land_prepay, 2)

    return {
        # 清算(P&L)
        "vat": vat_payable,
        "vat_additional": surtax,
        "land_appreciation": land_settlement,
        "stamp": stamp,
        "total": total_pl,
        # 预征(CF)
        "prepay": {
            "vat_prepay": prepay_vat_total,
            "surtax_prepay": round(prepay_vat_total * taxes.vat_additional_rate, 2),
            "land_prepay": land_prepay,
            "income_tax_prepay": 0,  # computed in cashflow
            "stamp": stamp,
            "total": round(prepay_vat_total + round(prepay_vat_total * taxes.vat_additional_rate, 2) + land_prepay + stamp, 2),
        },
        # 清算找差
        "land_settlement_diff": settlement_diff,
        "land_settlement_detail": lat_result,
        # 不含税替代
        "revenue_ex_vat": vat.get("revenue_ex_vat", sales.get("total_ex_vat", total_revenue)),
        "cost_ex_vat": vat.get("cost_ex_vat", {}),
        "surtax_rate": taxes.vat_additional_rate,
    }


# ============ 7. 现金流 ============

def _prod_revenue(p: Product) -> float:
    return round(
        p.parking_spots * p.parking_price / 10000 if p.type == "车库"
        else p.saleable_area * p.unit_price / 10000, 2
    )


def calc_cashflow(land_cost: dict, constr: dict, other_direct: dict,
                  sales: dict, period_fees: dict, taxes: dict,
                  financing: FinancingParams, timeline: dict,
                  products: list[Product], sales_params: SalesParams,
                  payment_schedule: dict) -> dict:
    """逐月现金流 → IRR/NPV/回正周期 (S-curve + 多期)

    两条现金流:
      - project_cf  = 项目本身(无杠杆), 不含融资
      - equity_cf   = 股东视角, 含权益出资+贷款+还本付息
    """
    months = timeline.get("delivery_month", 30) + 6
    cf = [0.0] * (months + 1)
    has_loan = financing.dev_loan_interest_rate > 0 or financing.bridge_loan_rate > 0
    cf_equity = [0.0] * (months + 1) if has_loan else cf

    const_total = constr["total"]
    presale_start = timeline.get("presale_month", 6)
    const_start = timeline.get("const_start_month", 3)
    sell_period = sales_params.sell_period_months
    delivery = timeline.get("delivery_month", 30)
    total_inv = round(land_cost["total"] + constr["total"] + other_direct["total"] + period_fees["total"], 2)
    loan = 0
    bridge_loan_val = 0

    # 每个产品的S曲线收入
    prod_data = []
    total_rev = 0.0
    for p in products:
        rev = _prod_revenue(p)
        if rev <= 0:
            continue
        total_rev += rev
        start = presale_start + p.presale_month_offset
        w = _s_curve_weights(sell_period)
        prod_data.append({"start": start, "revenue": rev, "weights": w, "marketing_share": 0})
    monthly_revs = [0.0] * (months + 1)

    # --- 支出 ---
    cf[0] -= land_cost["total"]
    pmt_sched = payment_schedule.get("const_pay_timing", [])
    prev_pct = 0
    for t in pmt_sched:
        mo = t["month_offset"]
        pay = round(const_total * (t["cumulative"] - prev_pct), 2)
        if mo < len(cf):
            cf[mo] -= pay
        prev_pct = t["cumulative"]
    if const_start < len(cf):
        cf[const_start] -= other_direct["total"]

    mgmt_mon = round(period_fees["management"] / max(months - const_start, 1), 2)
    for m in range(const_start, months):
        if m < len(cf):
            cf[m] -= mgmt_mon

    # --- 收入 (per-product S-curve + 多期) ---
    for pr in prod_data:
        for i in range(sell_period):
            mo = pr["start"] + i
            if mo >= len(cf):
                break
            month_rev = round(pr["revenue"] * pr["weights"][i], 2)
            monthly_revs[mo] += month_rev
            cp = sales_params.front_payment_ratio
            if cp > 0 and mo < len(cf):
                cf[mo] += round(month_rev * cp, 2)

    for pr in prod_data:
        for i in range(sell_period):
            mo = pr["start"] + i + sales_params.mortgage_release_delay
            if mo >= len(cf):
                break
            month_rev = round(pr["revenue"] * pr["weights"][i], 2)
            cm = sales_params.mortgage_ratio
            if cm > 0 and mo < len(cf):
                cf[mo] += round(month_rev * cm, 2)

    # --- 营销费 (per-product S-curve) ---
    mkt_total = period_fees["marketing"]
    if mkt_total > 0:
        rev_total = sum(pr["revenue"] for pr in prod_data)
        for pr in prod_data:
            pr["marketing_share"] = mkt_total * pr["revenue"] / rev_total if rev_total else 0
            for i in range(sell_period):
                mo = pr["start"] + i
                if mo < len(cf):
                    cf[mo] -= round(pr["marketing_share"] * pr["weights"][i], 2)

    # --- 税金(随销售支付: 预缴口径, S-curve) ---
    prepay = taxes.get("prepay", {})
    prepay_total_cf = prepay.get("total", taxes["total"])
    rev_total_all = sum(pr["revenue"] for pr in prod_data)
    for m in range(months + 1):
        if monthly_revs[m] > 0 and rev_total_all > 0:
            cf[m] -= round(prepay_total_cf * monthly_revs[m] / rev_total_all, 2)

    # --- 土增税清算找差(交付时补缴) ---
    settlement_diff = taxes.get("land_settlement_diff", 0)
    if settlement_diff > 0 and delivery < len(cf):
        cf[delivery] -= settlement_diff

    # --- 所得税: 预缴(跟S-curve) + 汇算清缴找差 ---
    profit_bt = round(sales["total"] - total_inv - taxes["total"], 2)
    total_income_tax = round(max(0, profit_bt) * 0.25, 2)
    prepaid_tax = 0.0
    if total_income_tax > 0 and rev_total_all > 0:
        for m in range(months + 1):
            if monthly_revs[m] > 0:
                it = round(total_income_tax * monthly_revs[m] / rev_total_all, 2)
                cf[m] -= it
                prepaid_tax += it
    # 汇算清缴: 多退少补 (在交付+3月)
    income_tax_diff = round(total_income_tax - prepaid_tax, 2)
    settle_mo = delivery + 3
    if abs(income_tax_diff) > 0.01 and settle_mo < len(cf):
        cf[settle_mo] -= income_tax_diff

    # --- 杠杆现金流 (equity_cf) ---
    if cf_equity is not cf:
        # 权益出资
        non_land_cost = total_inv - land_cost["total"]
        equity = round(land_cost["total"] + non_land_cost * financing.equity_ratio, 2)
        equity_land_only = round(total_inv * financing.equity_ratio, 2)
        equity = max(equity, equity_land_only)
        cf_equity = [0.0] * (months + 1)
        cf_equity[0] -= equity

        # --- 前融(桥贷): 补充土地款缺额 ---
        bridge_loan = 0
        bridge_interest = 0
        if financing.bridge_loan_ratio > 0 and financing.bridge_loan_rate > 0:
            bridge_loan = round(land_cost["total"] * financing.bridge_loan_ratio, 2)
            cf_equity[0] += bridge_loan  # 拿地时放款
            bridge_mi = round(financing.bridge_loan_rate / 12, 6)
            for m in range(1, min(financing.bridge_loan_term, len(cf_equity))):
                bridge_interest += round(bridge_loan * bridge_mi, 2)
                cf_equity[m] -= round(bridge_loan * bridge_mi, 2)
            repay_mo = min(financing.bridge_loan_term, len(cf_equity) - 1)
            cf_equity[repay_mo] -= bridge_loan
            bridge_loan_val = bridge_loan

        # --- 开发贷 ---
        # 剩余投资缺口 = 总投 - 权益 - 前融
        loan = round(max(0, total_inv - equity - bridge_loan), 2)
        if loan > 0 and financing.dev_loan_interest_rate > 0:
            cf_equity[const_start] += loan
            dev_mi = round(financing.dev_loan_interest_rate / 12, 6)
            for m in range(const_start, min(const_start + financing.dev_loan_term_months, len(cf_equity))):
                cf_equity[m] -= round(loan * dev_mi, 2)
            repay_mon = round(loan / max(sell_period, 1), 2)
            for m in range(sell_period):
                idx = const_start + m + 1
                if idx < len(cf_equity):
                    cf_equity[idx] -= repay_mon

        # 项目运营现金流
        for m in range(1, months + 1):
            cf_equity[m] += cf[m]
    else:
        equity = total_inv

    # --- 指标 ---
    def _calc_irr(arr):
        if not any(v != 0 for v in arr):
            return 0
        # numpy-financial IRR 要求至少一个正一个负
        pos = sum(1 for v in arr if v > 0)
        neg = sum(1 for v in arr if v < 0)
        if pos == 0 or neg == 0:
            return 0
        return round(npf.irr(arr), 6)

    project_irr = _calc_irr(cf)
    equity_irr = _calc_irr(cf_equity)

    def _calc_metrics(arr):
        cum = 0
        peak = 0
        peak_m = 0
        payback = None
        for m, v in enumerate(arr):
            cum += v
            if cum < peak:
                peak = cum
                peak_m = m
            if payback is None and cum >= 0 and m > 0:
                payback = m
        return round(abs(peak), 2), peak_m, payback

    peak_d, peak_m, payback = _calc_metrics(cf)
    eq_peak_d, eq_peak_m, eq_payback = _calc_metrics(cf_equity) if cf_equity is not cf else (peak_d, peak_m, payback)

    return {
        "project_cf": cf,
        "equity_cf": cf_equity,
        "project_irr": project_irr,
        "equity_irr": equity_irr,
        "npv_8": round(npf.npv(0.08, cf), 2),
        "peak_deficit": peak_d,
        "peak_month": peak_m,
        "payback_month": payback,
        "equity_peak_deficit": eq_peak_d,
        "equity_peak_month": eq_peak_m,
        "equity_payback_month": eq_payback,
        "total_investment": total_inv,
        "equity": equity,
        "loan": loan,
        "bridge_loan": bridge_loan_val,
    }


# ============ 8. 盈利汇总 ============

def calc_profit_summary(sales: dict, land_cost: dict, constr: dict,
                        other_direct: dict, period_fees: dict,
                        taxes: dict, vat_result: dict, cf_result: dict,
                        tax_params: TaxParams) -> dict:
    """P2: 利润表改为不含税口径

    营业收入 = 不含税收入 (含税 − 销项)
    营业成本 = 土地(含税) + 建安(不含税) + 前期(不含税) + ...
    税金及附加 = 附加税 + 印花税 + 土增税
    """
    rev = taxes.get("revenue_ex_vat", sales["total"])
    cv = taxes.get("cost_ex_vat", {})
    cx = cv.get("total", constr["total"] + other_direct["total"] + period_fees["total"])

    total_cost = round(land_cost["total"] + cx + taxes["vat_additional"] + taxes["land_appreciation"] + taxes["stamp"], 2)
    profit_bt = round(rev - total_cost, 2)
    income_tax = round(max(0, profit_bt) * tax_params.income_tax_rate, 2)
    net_profit = round(profit_bt - income_tax, 2)
    net_margin = round(net_profit / rev, 4) if rev else 0

    return {
        "total_revenue_ex_vat": rev,
        "total_cost_ex_vat": total_cost,
        "profit_before_tax": profit_bt,
        "income_tax": income_tax,
        "net_profit": net_profit,
        "net_margin": net_margin,
        "total_investment": cf_result.get("total_investment", 0),
        "roi": round(net_profit / cf_result.get("total_investment", 1), 4),
    }


# ============ 9. 主函数 ============

def run_model(config: dict) -> dict:
    land = LandParams(**config["land"])
    products = [Product(**p) for p in config["products"]]
    fees = FeeParams(**config["fees"])
    fin = FinancingParams(**config["financing"])
    sales_params = SalesParams(**config["sales"])
    taxes = TaxParams(**config["taxes"])
    timeline = config["timeline"]
    payment_schedule = config.get("payment_schedule", {})

    # 流水线
    land_cost = calc_land_cost(land)
    constr = calc_construction(products)
    other = calc_other_direct(constr, fees)
    sales = calc_sales(products)
    period_fees = calc_fees(sales, land_cost, constr, other, fees)

    # P2: 增值税完整链条
    vat_result = calc_vat_full(sales, land_cost, constr, other, period_fees, products, taxes)
    tax_result = calc_taxes(sales, land_cost, constr, other, period_fees,
                            products, taxes, vat_result)
    cf = calc_cashflow(land_cost, constr, other, sales, period_fees,
                       tax_result, fin, timeline, products, sales_params,
                       payment_schedule)
    profit = calc_profit_summary(sales, land_cost, constr, other,
                                 period_fees, tax_result, vat_result, cf, taxes)

    return {
        "land_cost": land_cost,
        "construction": constr,
        "other_direct": other,
        "sales": sales,
        "period_fees": period_fees,
        "vat": vat_result,
        "taxes": tax_result,
        "cashflow": cf,
        "profit": profit,
    }


@engine("kaifa_v1")
def run(config: dict, plan_id: str = None) -> dict:
    """平台入口"""
    return run_model(config)


if __name__ == "__main__":
    import sys, yaml
    path = sys.argv[1] if len(sys.argv) > 1 else "templates/kaifa.yaml"
    with open(path) as f:
        cfg = yaml.safe_load(f)
    result = run_model(cfg)
    p = result["profit"]
    cf = result["cashflow"]
    v = result["vat"]
    print(f"{'='*60}")
    print(f"项目: {cfg['project']['name']}")
    print(f"{'='*60}")
    print(f"\n土地成本:   {result['land_cost']['total']:.0f} 万元")
    print(f"  出让金:   {result['land_cost']['premium']:.0f}")
    print(f"  契税:     {result['land_cost']['deed_tax']:.0f}")
    print(f"  配套费:   {result['land_cost']['city_support_fee']:.0f}")
    print(f"\n建安成本:   {result['construction']['total']:.0f} 万元")
    print(f"前期+其他:  {result['other_direct']['total']:.0f} 万元")
    print(f"三费合计:   {result['period_fees']['total']:.0f} 万元")
    print(f"  管理费:   {result['period_fees']['management']:.0f}")
    print(f"  营销费:   {result['period_fees']['marketing']:.0f}")
    print(f"\n销售收入:   {result['sales']['total']:.0f} 万元 (含税)")
    print(f"  不含税:   {v['revenue_ex_vat']:.0f} 万元")
    print(f"\n增值税链:")
    print(f"  土地抵减:   {v['land_deduction']:.0f}")
    print(f"  销项税额:   {v['output_vat']:.0f}")
    print(f"  进项税额:   {v['input_vat']['total']:.0f}")
    print(f"    建安:     {v['input_vat']['construction']:.0f}")
    print(f"    前期:     {v['input_vat']['preliminary']:.0f}")
    print(f"    管理/营销: {v['input_vat']['management']+v['input_vat']['marketing']:.0f}")
    print(f"  应纳增值税: {v['vat_payable']:.0f}")
    print(f"  附加税:     {v['surtax']:.0f} (税率{v['surtax_rate']*100:.0f}%)")
    t = result["taxes"]
    print(f"\n税金(P&L):   {t['total']:.0f} 万元")
    print(f"  附加税:    {t['vat_additional']:.0f}")
    print(f"  土增税:    {t['land_appreciation']:.0f}")
    print(f"  印花税:    {t['stamp']:.0f}")
    if "land_settlement_detail" in t:
        print(f"\n土增税清算:")
        for ty in t["land_settlement_detail"]["types"]:
            if ty["gfa"] <= 0:
                continue
            nm = ty["type"]
            if ty["products"]:
                nm += f"({'/'.join(ty['products'])})"
            print(f"  {nm}:")
            print(f"    收入(不含税): {ty['revenue_ex_vat']:.0f} 万元")
            print(f"    扣除合计:     {ty['deduction']:.0f} 万元")
            print(f"    增值额:       {ty['excess']:.0f} 万元 (率: {ty['excess_ratio']*100:.1f}%)")
            print(f"    适用税率:     {ty['rate']*100:.0f}%")
            print(f"    应纳税额:     {ty['tax']:.0f} 万元")
    print(f"\n  土增预征(CF): {t['prepay']['land_prepay']:.0f} 万元")
    print(f"  清算找差:    {t['land_settlement_diff']:.0f} 万元")
    print(f"\n{'='*60}")
    print(f"不含税收入:   {p['total_revenue_ex_vat']:.0f} 万元")
    print(f"不含税成本:   {p['total_cost_ex_vat']:.0f} 万元")
    print(f"利润总额:     {p['profit_before_tax']:.0f} 万元")
    print(f"所得税:       {p['income_tax']:.0f} 万元")
    print(f"净利润:       {p['net_profit']:.0f} 万元")
    print(f"净利率:       {p['net_margin']*100:.1f}%")
    print(f"总投资:       {p['total_investment']:.0f} 万元")
    print(f"ROI:          {p['roi']*100:.1f}%")
    print(f"\n现金流指标:")
    p_irr = cf['project_irr']; e_irr = cf['equity_irr']
    print(f"项目 IRR:      {p_irr*100:.2f}%/月 ({(1+p_irr)**12-1:.1%}/年)")
    print(f"权益 IRR:      {e_irr*100:.2f}%/月 ({(1+e_irr)**12-1:.1%}/年)")
    print(f"NPV(8%):       {cf['npv_8']:.0f} 万元")
    print(f"资金峰值:      {cf['peak_deficit']:.0f} 万元 (第{cf['peak_month']}月)")
    print(f"回正周期:      第{cf['payback_month']}个月" if cf['payback_month'] else "  未回正")
    print(f"权益出资:      {cf['equity']:.0f} 万元")
    print(f"开发贷:        {cf['loan']:.0f} 万元")
    if cf.get('bridge_loan', 0) > 0:
        print(f"前融(桥贷):    {cf['bridge_loan']:.0f} 万元 (利率{cfg['financing']['bridge_loan_rate']*100:.0f}%)")
    print(f"权益回正:      {cf.get('equity_payback_month', 0)}个月")
