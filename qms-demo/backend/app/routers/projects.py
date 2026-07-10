from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..auth import get_current_user, assert_project_access, write_audit, user_memberships

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("")
def list_projects(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    mids = user_memberships(db, user)
    if any(m.role_code == "admin" for m in mids):
        projects = db.query(models.Project).all()
    else:
        pids = {m.project_id for m in mids}
        projects = db.query(models.Project).filter(models.Project.id.in_(pids)).all() if pids else []
    out = []
    for p in projects:
        sections = db.query(models.Section).filter(models.Section.project_id == p.id).all()
        out.append({
            "id": p.id,
            "code": p.code,
            "name": p.name,
            "description": p.description,
            "sections": [{"id": s.id, "code": s.code, "name": s.name} for s in sections],
        })
    return out


@router.post("")
def create_project(body: schemas.ProjectCreate, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # only admin
    if not any(m.role_code == "admin" for m in user_memberships(db, user)):
        raise HTTPException(403, "仅管理员可创建项目")
    if db.query(models.Project).filter(models.Project.code == body.code).first():
        raise HTTPException(400, "项目编码已存在")
    p = models.Project(code=body.code, name=body.name, description=body.description)
    db.add(p)
    db.flush()
    for s in body.sections or [{"code": "SG1", "name": "施工一标"}]:
        db.add(models.Section(project_id=p.id, code=s.get("code", "SG1"), name=s.get("name", "标段")))
    db.add(models.UserProject(user_id=user.id, project_id=p.id, section_id=None, role_code="admin"))
    write_audit(db, user, "project.create", f"{p.code} {p.name}")
    db.commit()
    return {"id": p.id, "code": p.code, "name": p.name}


@router.get("/{project_id}")
def get_project(project_id: str, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    assert_project_access(db, user, project_id)
    p = db.get(models.Project, project_id)
    if not p:
        raise HTTPException(404, "项目不存在")
    sections = db.query(models.Section).filter(models.Section.project_id == p.id).all()
    return {
        "id": p.id,
        "code": p.code,
        "name": p.name,
        "description": p.description,
        "sections": [{"id": s.id, "code": s.code, "name": s.name} for s in sections],
    }
