"""FastAPI 入口 - 暴露模板/测算/存档 API"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from engines import list_templates, load_template
from services.calculator import calculate, calculate_all_plans
from services.storage import save_record, list_records, get_record, delete_record

app = FastAPI(title="投资测算平台")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class CalcRequest(BaseModel):
    template_id: str
    params: dict
    plan_id: Optional[str] = None


class SaveRequest(BaseModel):
    name: str
    template_id: str
    params: dict
    results: dict


@app.get("/api/templates")
def api_list_templates():
    return list_templates()


@app.get("/api/templates/{template_id}")
def api_get_template(template_id: str):
    try:
        return load_template(template_id)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))


@app.post("/api/calculate")
def api_calculate(req: CalcRequest):
    try:
        params = req.params
        if not params:
            tpl = load_template(req.template_id)
            params = tpl
        if req.plan_id:
            return calculate(req.template_id, params, req.plan_id)
        return calculate_all_plans(req.template_id, params)
    except Exception as e:
        raise HTTPException(400, str(e))


@app.post("/api/records")
def api_save_record(req: SaveRequest):
    rid = save_record(req.name, req.template_id, req.params, req.results)
    return {"id": rid}


@app.get("/api/records")
def api_list_records(template_id: Optional[str] = None):
    return list_records(template_id)


@app.get("/api/records/{rid}")
def api_get_record(rid: int):
    r = get_record(rid)
    if not r:
        raise HTTPException(404, "记录不存在")
    return r


@app.delete("/api/records/{rid}")
def api_delete_record(rid: int):
    if not delete_record(rid):
        raise HTTPException(404, "记录不存在")
    return {"ok": True}
