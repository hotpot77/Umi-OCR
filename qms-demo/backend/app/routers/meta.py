from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..auth import get_current_user, user_memberships

router = APIRouter(prefix="/api/meta", tags=["meta"])


@router.get("/audit")
def audit_logs(limit: int = 50, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not any(m.role_code == "admin" for m in user_memberships(db, user)):
        return []
    rows = db.query(models.AuditLog).order_by(models.AuditLog.created_at.desc()).limit(limit).all()
    return [
        {
            "id": r.id,
            "username": r.username,
            "action": r.action,
            "detail": r.detail,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


@router.get("/state-machine")
def state_machine():
    return {
        "states": ["draft", "submitted", "rejected", "approved", "archived"],
        "transitions": [
            {"from": "draft", "to": "submitted", "action": "submit", "roles": ["qc", "worker"]},
            {"from": "submitted", "to": "approved", "action": "approve", "roles": ["supervisor"]},
            {"from": "submitted", "to": "rejected", "action": "reject", "roles": ["supervisor"]},
            {"from": "rejected", "to": "draft", "action": "edit", "roles": ["qc", "worker"]},
            {"from": "rejected", "to": "submitted", "action": "submit", "roles": ["qc", "worker"]},
            {"from": "approved", "to": "archived", "action": "archive", "roles": ["archivist", "admin"]},
        ],
    }
