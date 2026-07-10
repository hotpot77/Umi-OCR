from datetime import datetime
from pydantic import BaseModel, Field


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: str
    username: str
    display_name: str
    roles: list[dict] = []


class ProjectCreate(BaseModel):
    code: str
    name: str
    description: str = ""
    sections: list[dict] = Field(default_factory=list)


class ProjectOut(BaseModel):
    id: str
    code: str
    name: str
    description: str
    sections: list[dict] = []


class WbsCreate(BaseModel):
    section_id: str
    parent_id: str | None = None
    name: str
    code: str
    node_type: str = "item"
    specialty: str = ""
    sort_order: int = 0
    default_template_codes: list[str] = []


class WbsUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    specialty: str | None = None
    sort_order: int | None = None
    parent_id: str | None = None
    default_template_codes: list[str] | None = None


class FormInstanceCreate(BaseModel):
    template_code: str
    wbs_id: str
    title: str | None = None
    data: dict = Field(default_factory=dict)


class FormInstanceSave(BaseModel):
    data: dict
    submit: bool = False


class TaskActionIn(BaseModel):
    action: str  # approve | reject
    comment: str = ""
