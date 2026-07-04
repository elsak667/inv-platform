"""对照 XLCS 验证引擎输出"""
import sys, pathlib, yaml
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from engines.kaifa import run_model

XLCS = {
    "sales_incl": 163938, "sales_excl": 151366,
    "land_cost": 58571, "const_cost": 47793,
    "prelim": 2795, "period": 9497,
    "vat": 4977, "surtax": 726, "lat": 4977,
    "income_tax": 7817, "net_profit": 18827, "net_margin": 0.124,
}

cfg = {
    "meta": {"id": "xlcs", "name": "验证", "engine": "kaifa_v1", "version": "1.0", "description": ""},
    "project": {"name": "验证", "city": "绍兴", "city_tier": 3},
    "land": {"site_area": 56000, "construction_area": 56000, "floor_area_ratio": 2.0,
             "total_gfa": 144224, "premium": 56000, "deed_tax_rate": 0.03,
             "city_support_fee_per_sqm": 60, "other_land_cost": 0},
    "products": [
        {"name": "高层", "type": "住宅", "gfa": 110656, "saleable_area": 110656,
         "unit_price": 14000, "const_cost_per_sqm": 3284, "decoration": "毛坯"},
        {"name": "车库", "type": "车库", "gfa": 33568, "saleable_area": 0,
         "parking_spots": 1007, "parking_price": 100000, "const_cost_per_sqm": 3329, "decoration": "毛坯"},
    ],
    "fees": {"management_fee_rate": 0.016, "marketing_fee_rate": 0.021, "agency_fee_rate": 0.03,
             "preliminary_rate": 0.02, "contingency_rate": 0.02, "indirect_dev_rate": 0.01},
    "financing": {"equity_ratio": 0.35, "dev_loan_interest_rate": 0.05, "dev_loan_term_months": 12,
                  "dev_loan_to_value": 0.50, "bridge_loan_ratio": 0, "bridge_loan_rate": 0, "bridge_loan_term": 12},
    "sales": {"sell_period_months": 16, "front_payment_ratio": 0.30, "mortgage_ratio": 0.70, "mortgage_release_delay": 3},
    "taxes": {"vat_rate": 0.09, "vat_rate_services": 0.06, "vat_prepay_rate": 0.03,
              "conversion_rate": 0.85, "invoice_rate": 1.0,
              "city_maintenance_rate": 0.07, "edu_surcharge_rate": 0.03, "local_edu_surcharge_rate": 0.02,
              "land_tax_prepay_rate": 0.02, "land_tax_prepay_commercial": 0.03,
              "income_tax_rate": 0.25, "stamp_tax_rate": 0.0005},
    "timeline": {"land_paid": 0, "const_start_month": 3, "presale_month": 3,
                 "structure_topped_month": 9, "completion_month": 18, "delivery_month": 24},
    "payment_schedule": {"const_pay_timing": [
        {"month_offset": 3, "cumulative": 0.15}, {"month_offset": 9, "cumulative": 0.65},
        {"month_offset": 18, "cumulative": 0.90}, {"month_offset": 24, "cumulative": 1.00}]},
}



r = run_model(cfg)
p = r["profit"]
cf = r["cashflow"]
v = r["vat"]
t = r["taxes"]

print(f"{'指标':<22} {'XLCS':>10} {'引擎':>10} {'偏差':>10}  {'说明'}")
print(f"{'─'*80}")
pairs = [
    ("销售(含税)", XLCS["sales_incl"], r["sales"]["total"], ""),
    ("销售(不含税)", XLCS["sales_excl"], v["revenue_ex_vat"], ""),
    ("土地成本", XLCS["land_cost"], r["land_cost"]["total"], ""),
    ("建安(含税)", XLCS["const_cost"], r["construction"]["total"], "≈ 高层3284+车库3329"),
    ("前期费用", XLCS["prelim"], r["other_direct"]["total"], "XLCS固定值 vs 引擎%费率"),
    ("三费(含税)", XLCS["period"], r["period_fees"]["total"], "XLCS管理费60%资本化"),
    ("增值税", XLCS["vat"], v["vat_payable"], "进项计算差异"),
    ("附加税", XLCS["surtax"], v["surtax"], "城建税7% vs 5%"),
    ("土增税", XLCS["lat"], t["land_appreciation"], "分摊方式差异"),
    ("所得税", XLCS["income_tax"], p["income_tax"], "随利润变动"),
    ("净利润", XLCS["net_profit"], p["net_profit"], ""),
    ("净利率", XLCS["net_margin"], p["net_margin"], ""),
]
for name, x, y, note in pairs:
    d = y - x
    pct = f"{(d/x*100):+.1f}%" if x else "-"
    print(f"{name:<22} {x:>10.0f} {y:>10.0f} {pct:>10}  {note}")

print(f"\nIRR: {(1+cf['project_irr'])**12-1:.1%}/年 (XLCS税后~20%)")
print(f"\n差异来源:")
print(f"  1. 前期费用: 引擎用费率计算, XLCS用固定值")
print(f"  2. 管理费: 引擎全额期间费用, XLCS 60%资本化")
print(f"  3. 城建税率: 引擎5%/7%可配, XLCS视城市7或5")
print(f"  4. 土增税分摊: 引擎GFA比例分摊, XLCS按产品类型细分")
