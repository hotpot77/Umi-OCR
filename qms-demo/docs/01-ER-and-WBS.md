# 领域模型 ER（阶段 0）

```mermaid
erDiagram
  PROJECT ||--o{ SECTION : has
  PROJECT ||--o{ USER_PROJECT : grants
  USER ||--o{ USER_PROJECT : joins
  ROLE ||--o{ USER_PROJECT : assigns
  SECTION ||--o{ WBS_NODE : roots
  WBS_NODE ||--o{ WBS_NODE : parent
  WBS_NODE ||--o{ FORM_INSTANCE : binds
  FORM_TEMPLATE ||--o{ FORM_INSTANCE : shapes
  WBS_NODE ||--o{ PROCESS_TASK : spawns
  FORM_INSTANCE ||--o| PROCESS_TASK : linked
  PROCESS_TASK ||--o{ TASK_ACTION : history
  USER ||--o{ TASK_ACTION : acts
  PROJECT ||--o{ AUDIT_LOG : records
  PROJECT ||--o{ FILE_OBJECT : stores

  PROJECT {
    string id PK
    string name
    string code
  }
  SECTION {
    string id PK
    string project_id FK
    string name
    string code
  }
  USER {
    string id PK
    string username
    string password_hash
    string display_name
  }
  ROLE {
    string code PK
    string name
  }
  USER_PROJECT {
    string user_id FK
    string project_id FK
    string section_id FK
    string role_code FK
  }
  WBS_NODE {
    string id PK
    string section_id FK
    string parent_id FK
    string name
    string code
    string node_type
    string specialty
    string path
    int level
    int sort_order
  }
  FORM_TEMPLATE {
    string id PK
    string code
    string name
    string kind
    json schema_json
  }
  FORM_INSTANCE {
    string id PK
    string template_id FK
    string wbs_id FK
    string status
    json data_json
  }
  PROCESS_TASK {
    string id PK
    string form_instance_id FK
    string wbs_id FK
    string title
    string status
    string assignee_role
    string section_id
  }
  TASK_ACTION {
    string id PK
    string task_id FK
    string actor_id FK
    string action
    string comment
  }
  FILE_OBJECT {
    string id PK
    string project_id FK
    string filename
    string path
  }
  AUDIT_LOG {
    string id PK
    string user_id
    string action
    string detail
  }
```

## WBS 节点类型

| node_type | 含义 | 层级建议 |
|-----------|------|----------|
| unit | 单位工程 | 1 |
| div | 分部工程 | 2 |
| item | 分项工程 | 3 |
| process | 工序 | 4 |

## 部位 → 默认用表映射（Demo）

| specialty | 默认模板 |
|-----------|----------|
| 路基 | 施表-100 平整度、施表-43 养护 |
| 桥梁 | 施表-43 养护 |
| 隧道 | 施表-43 养护 |
