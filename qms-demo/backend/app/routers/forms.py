from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..auth import get_current_user, assert_project_access, allowed_section_ids, write_audit
from ..models import uid

router = APIRouter(prefix="/api/forms", tags=["forms"])


def validate_and_enrich(template: models.FormTemplate, data: dict) -> tuple[dict, list[str]]:
    errors = []
    schema = template.schema_json or {}
    fields = schema.get("fields", [])
    out = dict(data or {})
    for f in fields:
        key = f["key"]
        val = out.get(key)
        if f.get("required") and (val is None or val == "" or val == []):
            errors.append(f"{f['label']}为必填项")
        if f.get("type") == "number" and val not in (None, "") and not isinstance(val, (int, float)):
            try:
                out[key] = float(val)
            except Exception:
                errors.append(f"{f['label']}必须为数字")
    if template.kind == "grid":
        points = out.get("points") or []
        if not isinstance(points, list) or len(points) < 1:
            errors.append("测点读数不能为空")
        else:
            try:
                nums = [float(x) for x in points]
                out["points"] = nums
                limit = float(out.get("design_limit") or 0)
                mx = max(abs(x) for x in nums) if nums else 0
                out["conclusion"] = "合格" if mx <= limit else f"不合格(最大偏差{mx})"
            except Exception:
                errors.append("测点读数格式错误")
    return out, errors


@router.get("/templates")
def list_templates(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(models.FormTemplate).order_by(models.FormTemplate.code).all()
    return [
        {"id": t.id, "code": t.code, "name": t.name, "kind": t.kind, "specialty": t.specialty, "schema_json": t.schema_json}
        for t in rows
    ]


@router.get("/templates/{code}")
def get_template(code: str, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    t = db.query(models.FormTemplate).filter(models.FormTemplate.code == code).first()
    if not t:
        raise HTTPException(404, "模板不存在")
    return {"id": t.id, "code": t.code, "name": t.name, "kind": t.kind, "specialty": t.specialty, "schema_json": t.schema_json}


@router.post("/instances")
def create_instance(body: schemas.FormInstanceCreate, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    wbs = db.get(models.WbsNode, body.wbs_id)
    if not wbs:
        raise HTTPException(404, "WBS 不存在")
    section = db.get(models.Section, wbs.section_id)
    assert_project_access(db, user, section.project_id, roles=["admin", "qc", "worker"])
    allowed = allowed_section_ids(db, user, section.project_id)
    if allowed is not None and wbs.section_id not in allowed:
        raise HTTPException(403, "无该标段权限")
    tpl = db.query(models.FormTemplate).filter(models.FormTemplate.code == body.template_code).first()
    if not tpl:
        raise HTTPException(404, "模板不存在")
    data, errors = validate_and_enrich(tpl, body.data)
    # allow create even with empty draft; only soft-check
    title = body.title or f"{tpl.name} / {wbs.name}"
    inst = models.FormInstance(
        id=uid(),
        template_id=tpl.id,
        wbs_id=wbs.id,
        section_id=wbs.section_id,
        project_id=section.project_id,
        title=title,
        status="draft",
        data_json=data,
        created_by=user.id,
    )
    db.add(inst)
    db.flush()
    task = models.ProcessTask(
        id=uid(),
        form_instance_id=inst.id,
        wbs_id=wbs.id,
        section_id=wbs.section_id,
        project_id=section.project_id,
        title=title,
        status="draft",
        assignee_role="qc",
        created_by=user.id,
    )
    db.add(task)
    db.flush()
    db.add(models.TaskAction(id=uid(), task_id=task.id, actor_id=user.id, action="create", comment="创建表单实例"))
    write_audit(db, user, "form.create", title)
    db.commit()
    db.refresh(inst)
    db.refresh(task)
    return {"instance": _inst(inst, tpl), "task_id": task.id, "warnings": errors}


@router.get("/instances/{instance_id}")
def get_instance(instance_id: str, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    inst = db.get(models.FormInstance, instance_id)
    if not inst:
        raise HTTPException(404, "实例不存在")
    assert_project_access(db, user, inst.project_id)
    tpl = db.get(models.FormTemplate, inst.template_id)
    return _inst(inst, tpl)


@router.put("/instances/{instance_id}")
def save_instance(instance_id: str, body: schemas.FormInstanceSave, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    inst = db.get(models.FormInstance, instance_id)
    if not inst:
        raise HTTPException(404, "实例不存在")
    assert_project_access(db, user, inst.project_id, roles=["admin", "qc", "worker"])
    if inst.status not in ("draft", "rejected"):
        raise HTTPException(400, f"当前状态 {inst.status} 不可编辑")
    tpl = db.get(models.FormTemplate, inst.template_id)
    data, errors = validate_and_enrich(tpl, body.data)
    if body.submit and errors:
        raise HTTPException(400, {"message": "校验失败", "errors": errors})
    inst.data_json = data
    task = db.query(models.ProcessTask).filter(models.ProcessTask.form_instance_id == inst.id).first()
    if body.submit:
        inst.status = "submitted"
        if task:
            task.status = "submitted"
            task.assignee_role = "supervisor"
            db.add(models.TaskAction(task_id=task.id, actor_id=user.id, action="submit", comment="提交监理签认"))
        write_audit(db, user, "form.submit", inst.title)
    else:
        inst.status = "draft" if inst.status != "rejected" else "draft"
        if task and task.status == "rejected":
            task.status = "draft"
            task.assignee_role = "qc"
        write_audit(db, user, "form.save", inst.title)
    db.commit()
    return {"instance": _inst(inst, tpl), "errors": errors}


def _inst(inst: models.FormInstance, tpl: models.FormTemplate | None) -> dict:
    return {
        "id": inst.id,
        "title": inst.title,
        "status": inst.status,
        "wbs_id": inst.wbs_id,
        "section_id": inst.section_id,
        "project_id": inst.project_id,
        "data": inst.data_json,
        "template": {
            "id": tpl.id if tpl else None,
            "code": tpl.code if tpl else None,
            "name": tpl.name if tpl else None,
            "kind": tpl.kind if tpl else None,
            "schema_json": tpl.schema_json if tpl else {},
        },
    }
