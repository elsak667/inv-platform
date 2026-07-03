"""测算调度 - 选模板 → 取引擎 → 跑计算 → 返回结果"""
from engines import get_engine, load_template


def calculate(template_id: str, params: dict, plan_id: str = None) -> dict:
    """单次测算"""
    tpl = load_template(template_id)
    engine_id = tpl["meta"]["engine"]
    fn = get_engine(engine_id)
    result = fn(params, plan_id)
    return result


def calculate_all_plans(template_id: str, params: dict) -> dict:
    """所有方案对比"""
    tpl = load_template(template_id)
    engine_id = tpl["meta"]["engine"]
    fn = get_engine(engine_id)
    result = fn(params, None)
    return result
