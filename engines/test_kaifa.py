import yaml, pathlib
from .kaifa import run_model

HERE = pathlib.Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "templates" / "kaifa.yaml"
DATA = None


def _data():
    global DATA
    if DATA is None:
        with open(TEMPLATE) as f:
            DATA = run_model(yaml.safe_load(f))
    return DATA


def test_demo_project():
    r = _data()
    cf = r["cashflow"]
    p = r["profit"]
    assert p["net_profit"] > 0
    assert 0.20 < p["net_margin"] < 0.35
    assert cf["project_irr"] > 0
    assert cf["equity_irr"] > 0
    assert cf["equity"] >= r["land_cost"]["total"]
    assert cf["loan"] > 0
    assert cf["peak_deficit"] > 0
    assert cf["payback_month"] is not None


def test_land_cost_covers_equity():
    r = _data()
    assert r["cashflow"]["equity"] >= r["land_cost"]["total"]


def test_irr_converges():
    r = _data()
    eq = r["cashflow"]["equity_cf"]
    import numpy_financial as npf
    npv_low = npf.npv(0, eq)
    npv_high = npf.npv(0.10, eq)
    assert npv_low > 0, f"NPV at 0% should be positive, got {npv_low}"
    assert npv_high < 0, f"NPV at 10% should be negative, got {npv_high}"


def test_vat_chain():
    v = _data()["vat"]
    assert v["output_vat"] > 0
    assert v["land_deduction"] > 0
    assert v["input_vat"]["total"] > 0
    assert v["vat_payable"] >= 0
    assert v["vat_payable"] == v["output_vat"] - v["input_vat"]["total"]
    assert v["surtax"] > 0
    assert v["revenue_ex_vat"] < _data()["sales"]["total"]


def test_profit_ex_vat():
    p = _data()["profit"]
    assert p["total_revenue_ex_vat"] < _data()["sales"]["total"]
    assert p["profit_before_tax"] > 0


def test_land_tax_settlement():
    """P2.5: 土增税清算≥预征"""
    t = _data()["taxes"]
    assert t["land_appreciation"] >= t["prepay"]["land_prepay"]
    assert t["land_settlement_diff"] >= 0
    d = t["land_settlement_detail"]
    assert d["total"] == t["land_appreciation"]
    assert len(d["types"]) == 3
    # 普通住宅增值率≤50% → 30%税率 (土地成本全部分配至住宅, 车库不摊)
    ord_t = [x for x in d["types"] if x["type"] == "普通住宅"][0]
    assert 0.10 < ord_t["excess_ratio"] < 0.50
    assert ord_t["rate"] == 0.30
