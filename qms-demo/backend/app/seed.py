from sqlalchemy.orm import Session
from . import models
from .auth import hash_password

SPECIALTY_TEMPLATES = {
    "路基": ["SB-100", "SB-43"],
    "桥梁": ["SB-43"],
    "隧道": ["SB-43"],
    "路面": ["SB-100"],
}

TEMPLATE_DEFS = [
    {
        "code": "SB-43",
        "name": "施表-43 混凝土构件养护记录",
        "kind": "structured",
        "specialty": "桥梁",
        "schema_json": {
            "fields": [
                {"key": "project_name", "label": "工程名称", "type": "string", "required": True},
                {"key": "contractor", "label": "施工单位", "type": "string", "required": True},
                {"key": "supervisor_org", "label": "监理单位", "type": "string", "required": False},
                {"key": "unit_name", "label": "单位工程", "type": "string", "required": True},
                {"key": "div_name", "label": "分部工程", "type": "string", "required": True},
                {"key": "component_name", "label": "构件名称", "type": "string", "required": True},
                {"key": "pour_date", "label": "浇筑日期", "type": "date", "required": True},
                {
                    "key": "cure_method",
                    "label": "养护方式",
                    "type": "multi",
                    "options": ["覆盖", "喷雾", "蓄水", "洒水"],
                    "required": True,
                },
                {"key": "start_time", "label": "开始养护时间", "type": "datetime", "required": True},
                {"key": "ambient_temp", "label": "环境温度℃", "type": "number", "required": False},
                {"key": "remark", "label": "备注", "type": "text", "required": False},
                {"key": "recorder", "label": "记录人", "type": "string", "required": True},
            ]
        },
    },
    {
        "code": "SB-100",
        "name": "施表-100 路基路面平整度检测原始记录",
        "kind": "grid",
        "specialty": "路基",
        "schema_json": {
            "fields": [
                {"key": "project_name", "label": "工程名称", "type": "string", "required": True},
                {"key": "stake_from", "label": "起桩号", "type": "string", "required": True},
                {"key": "stake_to", "label": "止桩号", "type": "string", "required": True},
                {"key": "instrument", "label": "仪器", "type": "string", "required": False},
                {"key": "design_limit", "label": "允许偏差(mm)", "type": "number", "required": True, "default": 10},
                {
                    "key": "points",
                    "label": "测点读数(mm)",
                    "type": "grid",
                    "columns": 10,
                    "required": True,
                },
                {"key": "conclusion", "label": "结论", "type": "string", "required": False, "readonly": True},
            ],
            "rules": {"pass_if_abs_max_le": "design_limit"},
        },
    },
]


def seed_all(db: Session):
    if db.query(models.User).first():
        return

    roles = [
        ("admin", "系统管理员"),
        ("owner", "业主"),
        ("supervisor", "监理"),
        ("qc", "质检员"),
        ("worker", "施工员"),
        ("archivist", "资料员"),
    ]
    for code, name in roles:
        db.add(models.Role(code=code, name=name))

    users = [
        ("admin", "admin123", "系统管理员"),
        ("qc01", "888888", "质检员-张工"),
        ("jl01", "888888", "监理-李工"),
        ("sg01", "888888", "施工员-王工"),
        ("yz01", "888888", "业主代表"),
    ]
    user_map = {}
    for username, pwd, display in users:
        u = models.User(username=username, password_hash=hash_password(pwd), display_name=display)
        db.add(u)
        db.flush()
        user_map[username] = u

    for t in TEMPLATE_DEFS:
        db.add(models.FormTemplate(**t))

    project = models.Project(
        code="NT-DEMO",
        name="南天高速示范合同段（Demo）",
        description="阶段0-3 质检文控闭环演示项目，用表对齐交通部通用施表",
    )
    db.add(project)
    db.flush()

    sec6 = models.Section(project_id=project.id, code="SG6", name="施工六标")
    sec7 = models.Section(project_id=project.id, code="SG7", name="施工七标")
    db.add_all([sec6, sec7])
    db.flush()

    memberships = [
        (user_map["admin"].id, project.id, None, "admin"),
        (user_map["yz01"].id, project.id, None, "owner"),
        (user_map["jl01"].id, project.id, None, "supervisor"),
        (user_map["qc01"].id, project.id, sec6.id, "qc"),
        (user_map["sg01"].id, project.id, sec6.id, "worker"),
    ]
    for uid, pid, sid, role in memberships:
        db.add(models.UserProject(user_id=uid, project_id=pid, section_id=sid, role_code=role))

    # Sample WBS for 施工六标
    def add_node(parent, name, code, ntype, specialty, level, templates=None):
        node = models.WbsNode(
            section_id=sec6.id,
            parent_id=parent.id if parent else None,
            name=name,
            code=code,
            node_type=ntype,
            specialty=specialty,
            level=level,
            path=(f"{parent.path}/{code}" if parent else code),
            sort_order=level,
            default_template_codes=templates or SPECIALTY_TEMPLATES.get(specialty, []),
        )
        db.add(node)
        db.flush()
        return node

    u1 = add_node(None, "路基工程", "SG6-LJ-01", "unit", "路基", 1)
    d1 = add_node(u1, "路床", "SG6-LJ-01-01", "div", "路基", 2)
    i1 = add_node(d1, "K89+710~K90+200 上路床", "SG6-LJ-01-01-001", "item", "路基", 3, ["SB-100"])
    add_node(i1, "平整度检测", "SG6-LJ-01-01-001-01", "process", "路基", 4, ["SB-100"])

    u2 = add_node(None, "桥梁工程", "SG6-QL-01", "unit", "桥梁", 1)
    d2 = add_node(u2, "下部结构", "SG6-QL-01-01", "div", "桥梁", 2)
    i2 = add_node(d2, "1#墩身", "SG6-QL-01-01-001", "item", "桥梁", 3, ["SB-43"])
    add_node(i2, "混凝土养护", "SG6-QL-01-01-001-01", "process", "桥梁", 4, ["SB-43"])

    u3 = add_node(None, "隧道工程", "SG6-SD-01", "unit", "隧道", 1)
    d3 = add_node(u3, "洞身开挖", "SG6-SD-01-01", "div", "隧道", 2)
    add_node(d3, "YK72+266 左洞", "SG6-SD-01-01-001", "item", "隧道", 3, ["SB-43"])

    db.commit()
