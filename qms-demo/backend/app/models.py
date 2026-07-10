import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


def uid() -> str:
    return uuid.uuid4().hex


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(128))
    is_active: Mapped[int] = mapped_column(Integer, default=1)


class Role(Base):
    __tablename__ = "roles"
    code: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(64))


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    code: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(256))
    description: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Section(Base):
    __tablename__ = "sections"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    code: Mapped[str] = mapped_column(String(64))
    name: Mapped[str] = mapped_column(String(256))


class UserProject(Base):
    __tablename__ = "user_projects"
    __table_args__ = (UniqueConstraint("user_id", "project_id", "section_id", "role_code"),)
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    section_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    role_code: Mapped[str] = mapped_column(ForeignKey("roles.code"))


class WbsNode(Base):
    __tablename__ = "wbs_nodes"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    section_id: Mapped[str] = mapped_column(ForeignKey("sections.id"), index=True)
    parent_id: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(256))
    code: Mapped[str] = mapped_column(String(128), index=True)
    node_type: Mapped[str] = mapped_column(String(32))  # unit/div/item/process
    specialty: Mapped[str] = mapped_column(String(32), default="")
    path: Mapped[str] = mapped_column(String(512), default="")
    level: Mapped[int] = mapped_column(Integer, default=1)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    default_template_codes: Mapped[list] = mapped_column(JSON, default=list)


class FormTemplate(Base):
    __tablename__ = "form_templates"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    code: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(256))
    kind: Mapped[str] = mapped_column(String(32))  # structured | grid
    specialty: Mapped[str] = mapped_column(String(32), default="")
    schema_json: Mapped[dict] = mapped_column(JSON, default=dict)


class FormInstance(Base):
    __tablename__ = "form_instances"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    template_id: Mapped[str] = mapped_column(ForeignKey("form_templates.id"))
    wbs_id: Mapped[str] = mapped_column(ForeignKey("wbs_nodes.id"), index=True)
    section_id: Mapped[str] = mapped_column(String(32), index=True)
    project_id: Mapped[str] = mapped_column(String(32), index=True)
    title: Mapped[str] = mapped_column(String(256))
    status: Mapped[str] = mapped_column(String(32), default="draft")
    data_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_by: Mapped[str] = mapped_column(String(32))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProcessTask(Base):
    __tablename__ = "process_tasks"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    form_instance_id: Mapped[str] = mapped_column(ForeignKey("form_instances.id"), index=True)
    wbs_id: Mapped[str] = mapped_column(String(32), index=True)
    section_id: Mapped[str] = mapped_column(String(32), index=True)
    project_id: Mapped[str] = mapped_column(String(32), index=True)
    title: Mapped[str] = mapped_column(String(256))
    status: Mapped[str] = mapped_column(String(32), default="draft")
    assignee_role: Mapped[str] = mapped_column(String(32), default="qc")
    created_by: Mapped[str] = mapped_column(String(32))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TaskAction(Base):
    __tablename__ = "task_actions"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    task_id: Mapped[str] = mapped_column(ForeignKey("process_tasks.id"), index=True)
    actor_id: Mapped[str] = mapped_column(String(32))
    action: Mapped[str] = mapped_column(String(32))
    comment: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class FileObject(Base):
    __tablename__ = "file_objects"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    project_id: Mapped[str] = mapped_column(String(32), index=True)
    filename: Mapped[str] = mapped_column(String(256))
    stored_path: Mapped[str] = mapped_column(String(512))
    content_type: Mapped[str] = mapped_column(String(128), default="")
    size: Mapped[int] = mapped_column(Integer, default=0)
    uploaded_by: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    user_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    username: Mapped[str] = mapped_column(String(64), default="")
    action: Mapped[str] = mapped_column(String(64))
    detail: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
