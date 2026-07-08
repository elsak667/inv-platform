"""FastAPI 入口 - 暴露模板/测算/存档/导出 API"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional

from engines import list_templates, load_template
from services.calculator import calculate, calculate_all_plans
from services.storage import save_record, list_records, get_record, delete_record
from services.report import generate_report as _gen_report, generate_ppt_outline as _gen_outline, generate_report_llm as _gen_report_llm
from services.export_xlsx import export_zulin as _export_zulin

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


class ReportRequest(BaseModel):
    params: dict
    mode: str = "template"  # template | llm


class ExportRequest(BaseModel):
    params: Optional[dict] = None
    record_id: Optional[int] = None  # 若从存档导出, 传 id 直接用存档 results


@app.get("/api/templates")
def api_list_templates():
    try:
        return list_templates()
    except Exception as e:
        raise HTTPException(500, f"加载模板列表失败: {e}")


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


@app.post("/api/report/{template_id}")
def api_generate_report(template_id: str, req: ReportRequest):
    """生成分析报告 + PPT 大纲"""
    try:
        params = req.params
        if not params or "meta" not in params:
            tpl = load_template(template_id)
            if not params:
                params = tpl
            else:
                params["meta"] = tpl["meta"]
        result = calculate_all_plans(template_id, params)
        if req.mode == "llm":
            md = _gen_report_llm(params, result)
        else:
            md = _gen_report(params, result)
        outline = _gen_outline(params, result)
        return {"markdown": md, "outline": outline}
    except Exception as e:
        raise HTTPException(400, str(e))


@app.post("/api/export/{template_id}")
def api_export(template_id: str, req: ExportRequest):
    """导出测算表 Excel

    两种模式:
    1. 传 params → 现算现导
    2. 传 record_id → 从存档取 results 直接导(不重算)
    """
    try:
        tpl = load_template(template_id)

        if req.record_id:
            rec = get_record(req.record_id)
            if not rec:
                raise HTTPException(404, "存档记录不存在")
            # 存档 params 可能只是部分覆盖, 用模板做底合并
            saved_params = rec.get("params", {})
            if isinstance(saved_params, str):
                import json
                saved_params = json.loads(saved_params)
            params = {**tpl, **saved_params}
            result = rec.get("results")
            if not result:
                result = calculate_all_plans(template_id, params)
            elif isinstance(result, str):
                import json
                result = json.loads(result)
        else:
            params = req.params or tpl
            if "meta" not in params:
                params = {**tpl, **params}
            result = calculate_all_plans(template_id, params)

        if template_id == "zulin":
            data = _export_zulin(params, result)
        else:
            raise HTTPException(400, f"模板 {template_id} 暂不支持导出")
        from urllib.parse import quote
        filename = f"{params.get('project', {}).get('name', template_id)}_测算表.xlsx"
        encoded = quote(filename)
        return Response(
            content=data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=\"{encoded}\"; filename*=UTF-8''{encoded}",
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, str(e))
