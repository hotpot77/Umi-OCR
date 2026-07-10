import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..config import settings
from .. import models
from ..auth import get_current_user, assert_project_access, write_audit

router = APIRouter(prefix="/api/files", tags=["files"])


@router.post("/upload")
async def upload_file(project_id: str, file: UploadFile = File(...), user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    assert_project_access(db, user, project_id)
    suffix = Path(file.filename or "bin").suffix
    fid = uuid.uuid4().hex
    dest = settings.upload_dir / f"{fid}{suffix}"
    content = await file.read()
    dest.write_bytes(content)
    obj = models.FileObject(
        id=fid,
        project_id=project_id,
        filename=file.filename or dest.name,
        stored_path=str(dest),
        content_type=file.content_type or "",
        size=len(content),
        uploaded_by=user.id,
    )
    db.add(obj)
    write_audit(db, user, "file.upload", obj.filename)
    db.commit()
    return {"id": obj.id, "filename": obj.filename, "size": obj.size}


@router.get("")
def list_files(project_id: str, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    assert_project_access(db, user, project_id)
    rows = db.query(models.FileObject).filter(models.FileObject.project_id == project_id).order_by(models.FileObject.created_at.desc()).all()
    return [{"id": f.id, "filename": f.filename, "size": f.size, "content_type": f.content_type} for f in rows]


@router.get("/{file_id}/download")
def download_file(file_id: str, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    obj = db.get(models.FileObject, file_id)
    if not obj:
        raise HTTPException(404, "文件不存在")
    assert_project_access(db, user, obj.project_id)
    return FileResponse(obj.stored_path, filename=obj.filename)
