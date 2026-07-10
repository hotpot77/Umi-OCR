from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..auth import verify_password, create_access_token, get_current_user, user_memberships, write_audit

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=schemas.TokenOut)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(400, "用户名或密码错误")
    token = create_access_token({"sub": user.username})
    write_audit(db, user, "login", "用户登录")
    db.commit()
    return schemas.TokenOut(access_token=token)


@router.get("/me", response_model=schemas.UserOut)
def me(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    roles = []
    for m in user_memberships(db, user):
        role = db.get(models.Role, m.role_code)
        roles.append({
            "role_code": m.role_code,
            "role_name": role.name if role else m.role_code,
            "project_id": m.project_id,
            "section_id": m.section_id,
        })
    return schemas.UserOut(id=user.id, username=user.username, display_name=user.display_name, roles=roles)
