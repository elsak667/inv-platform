"""引擎注册机制 - 加新测算类型只需 @engine("xxx") 装饰"""
import yaml
from pathlib import Path
from typing import Callable

_ENGINES: dict[str, Callable] = {}
_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


def engine(engine_id: str):
    def deco(fn: Callable):
        _ENGINES[engine_id] = fn
        return fn
    return deco


def get_engine(engine_id: str) -> Callable:
    if engine_id not in _ENGINES:
        raise KeyError(f"引擎未注册: {engine_id}")
    return _ENGINES[engine_id]


def load_template(template_id: str) -> dict:
    p = _TEMPLATES_DIR / f"{template_id}.yaml"
    if not p.exists():
        raise FileNotFoundError(f"模板不存在: {template_id}")
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f)


def list_templates() -> list[dict]:
    out = []
    for p in sorted(_TEMPLATES_DIR.glob("*.yaml")):
        with open(p, encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        out.append({
            "id": cfg["meta"]["id"],
            "name": cfg["meta"]["name"],
            "version": cfg["meta"].get("version", "1.0"),
            "description": cfg["meta"].get("description", ""),
        })
    return out


from . import baozufang  # noqa: E402,F401  触发 @engine 注册
from . import kaifa  # noqa: E402,F401
from . import zulin  # noqa: E402,F401
