from datetime import datetime, timedelta
from typing import Annotated
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from .config import settings
from .database import get_db
from . import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8")[:72], bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8")[:72], hashed.encode("utf-8"))
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> models.User:
    cred_exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录或令牌无效")
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str | None = payload.get("sub")
        if not username:
            raise cred_exc
    except JWTError as e:
        raise cred_exc from e
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not user.is_active:
        raise cred_exc
    return user


def user_memberships(db: Session, user: models.User) -> list[models.UserProject]:
    return db.query(models.UserProject).filter(models.UserProject.user_id == user.id).all()


def assert_project_access(db: Session, user: models.User, project_id: str, roles: list[str] | None = None) -> models.UserProject:
    q = db.query(models.UserProject).filter(
        models.UserProject.user_id == user.id,
        models.UserProject.project_id == project_id,
    )
    rows = q.all()
    admin = db.query(models.UserProject).filter(
        models.UserProject.user_id == user.id, models.UserProject.role_code == "admin"
    ).first()
    if not rows and not admin:
        raise HTTPException(403, "无项目访问权限")
    if not rows:
        return admin
    if roles:
        for r in rows:
            if r.role_code in roles or r.role_code == "admin":
                return r
        if admin:
            return admin
        raise HTTPException(403, f"需要角色: {roles}")
    return rows[0]


def allowed_section_ids(db: Session, user: models.User, project_id: str) -> set[str] | None:
    """None means all sections."""
    memberships = [m for m in user_memberships(db, user) if m.project_id == project_id or m.role_code == "admin"]
    if any(m.role_code == "admin" or m.role_code == "owner" or m.section_id is None for m in memberships):
        return None
    return {m.section_id for m in memberships if m.section_id}


def write_audit(db: Session, user: models.User | None, action: str, detail: str = ""):
    db.add(models.AuditLog(
        user_id=user.id if user else None,
        username=user.username if user else "",
        action=action,
        detail=detail,
    ))
