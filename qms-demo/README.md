# 公路工程质检文控 Demo（阶段 0–3）

可运行的 MVP：登录/RBAC/多标段 → WBS → 质检填报 → 监理签认 → 待办首页。

表格版式可对照目标系统：http://fjhmtd.com:15123/glaf/login.html （施工六标全角色 / 888888）

## 快速启动

```bash
cd qms-demo
chmod +x scripts/run.sh
./scripts/run.sh
```

浏览器打开：http://127.0.0.1:8088/

API 文档：http://127.0.0.1:8088/docs

## Demo 账号

| 用户 | 密码 | 角色 |
|------|------|------|
| qc01 | 888888 | 质检员（施工六标） |
| jl01 | 888888 | 监理 |
| sg01 | 888888 | 施工员 |
| admin | admin123 | 管理员 |
| yz01 | 888888 | 业主 |

## 演示路径

1. 用 `qc01` 登录 → 工程划分 → 在分项/工序上点「开表 SB-43 / SB-100」
2. 填写并「提交监理」
3. 退出，用 `jl01` 登录 → 首页待办 → 签认或退回
4. 若退回，再用 `qc01` 修改后重提

## 目录

```text
qms-demo/
  docs/           # 阶段0：PRD / ER / 字段字典
  backend/app/    # FastAPI + SQLite
  frontend/       # Vue3 单页
  scripts/run.sh
```

## 已覆盖计划项

- 阶段0：PRD、ER、状态机、施表字典、Top50 清单
- 阶段1：JWT 登录、RBAC、多标段隔离、附件、审计
- 阶段2：WBS 树 CRUD、Excel 导入导出、专业→用表映射
- 阶段3：双模板（结构化+网格）、填报校验、审批流、待办统计
