from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..auth import get_current_user, assert_project_access, allowed_section_ids, user_memberships, write_audit

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


def _role_set(db: Session, user: models.User, project_id: str) -> set[str]:
    return {m.role_code for m in user_memberships(db, user) if m.project_id == project_id or m.role_code == "admin"}


@router.get("")
def list_tasks(
    project_id: str,
    tab: str = Query("todo", pattern="^(todo|done|rejected|all)$"),
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assert_project_access(db, user, project_id)
    roles = _role_set(db, user, project_id)
    allowed = allowed_section_ids(db, user, project_id)
    q = db.query(models.ProcessTask).filter(models.ProcessTask.project_id == project_id)
    if allowed is not None:
        q = q.filter(models.ProcessTask.section_id.in_(allowed))

    if tab == "todo":
        if "supervisor" in roles or "admin" in roles or "owner" in roles:
            q = q.filter(models.ProcessTask.status == "submitted")
        elif "qc" in roles or "worker" in roles:
            q = q.filter(models.ProcessTask.status.in_(["draft", "rejected"]))
        else:
            q = q.filter(models.ProcessTask.status == "submitted")
    elif tab == "done":
        q = q.filter(models.ProcessTask.status.in_(["approved", "archived"]))
    elif tab == "rejected":
        q = q.filter(models.ProcessTask.status == "rejected")

    rows = q.order_by(models.ProcessTask.updated_at.desc()).limit(200).all()
    return [_task(t, db) for t in rows]


@router.get("/stats")
def task_stats(project_id: str, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    assert_project_access(db, user, project_id)
    allowed = allowed_section_ids(db, user, project_id)
    q = db.query(models.ProcessTask).filter(models.ProcessTask.project_id == project_id)
    if allowed is not None:
        q = q.filter(models.ProcessTask.section_id.in_(allowed))
    all_rows = q.all()
    roles = _role_set(db, user, project_id)
    if "supervisor" in roles or "admin" in roles or "owner" in roles:
        todo = sum(1 for t in all_rows if t.status == "submitted")
    else:
        todo = sum(1 for t in all_rows if t.status in ("draft", "rejected"))
    return {
        "todo": todo,
        "done": sum(1 for t in all_rows if t.status in ("approved", "archived")),
        "rejected": sum(1 for t in all_rows if t.status == "rejected"),
        "all": len(all_rows),
        "item_done": sum(1 for t in all_rows if t.status == "approved"),
        "process_done": sum(1 for t in all_rows if t.status == "approved"),
    }


@router.post("/{task_id}/action")
def task_action(task_id: str, body: schemas.TaskActionIn, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.get(models.ProcessTask, task_id)
    if not task:
        raise HTTPException(404, "任务不存在")
    assert_project_access(db, user, task.project_id, roles=["admin", "supervisor", "owner"])
    if task.status != "submitted":
        raise HTTPException(400, "仅待审任务可签认/退回")
    if body.action not in ("approve", "reject"):
        raise HTTPException(400, "action 必须为 approve 或 reject")
    inst = db.get(models.FormInstance, task.form_instance_id)
    if body.action == "approve":
        task.status = "approved"
        if inst:
            inst.status = "approved"
        db.add(models.TaskAction(task_id=task.id, actor_id=user.id, action="approve", comment=body.comment or "签认通过"))
        write_audit(db, user, "task.approve", task.title)
    else:
        task.status = "rejected"
        task.assignee_role = "qc"
        if inst:
            inst.status = "rejected"
        db.add(models.TaskAction(task_id=task.id, actor_id=user.id, action="reject", comment=body.comment or "退回修改"))
        write_audit(db, user, "task.reject", task.title)
    db.commit()
    return _task(task, db)


@router.get("/{task_id}")
def get_task(task_id: str, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.get(models.ProcessTask, task_id)
    if not task:
        raise HTTPException(404, "任务不存在")
    assert_project_access(db, user, task.project_id)
    return _task(task, db, with_history=True)


def _task(t: models.ProcessTask, db: Session, with_history: bool = False) -> dict:
    data = {
        "id": t.id,
        "title": t.title,
        "status": t.status,
        "assignee_role": t.assignee_role,
        "form_instance_id": t.form_instance_id,
        "wbs_id": t.wbs_id,
        "section_id": t.section_id,
        "project_id": t.project_id,
        "updated_at": t.updated_at.isoformat() if t.updated_at else None,
    }
    if with_history:
        actions = (
            db.query(models.TaskAction)
            .filter(models.TaskAction.task_id == t.id)
            .order_by(models.TaskAction.created_at.asc())
            .all()
        )
        data["history"] = [
            {
                "action": a.action,
                "comment": a.comment,
                "actor_id": a.actor_id,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in actions
        ]
    return data
