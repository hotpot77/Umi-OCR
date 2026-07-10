# GLAF API 与运行时速查

补充 `README.md` 的接口层笔记，便于后续抓包对照与自研 API 设计。

## 认证

```http
GET  /glaf/mx/login/getLoginSecurityKey
→ {"x_y":"...","x_z":"..."}

POST /glaf/mx/login/doLogin?x=<urlencode(username)>&responseDataType=json
Content-Type: application/x-www-form-urlencoded

x=<username>&y=<x_y + password + x_z>
→ 成功后 Set-Cookie: JSESSIONID, GLAF_COOKIE, GLAF_JWT_COOKIE
→ 或 HTML 跳转 /glaf/mx/my/home
```

密码混淆（前端）：

```text
y = x_y + plaintextPassword + x_z
```

会话探活：

```http
GET /glaf/mx/user_status
→ {"user_status":"SUCCESS","user_id_md5":"..."}
```

## 主壳

```text
/glaf/mx/my/home
/glaf/mx/my/home/main      # frameset
/glaf/mx/my/home/top
/glaf/mx/my/home/left      # 菜单由父页注入 menudata
/glaf/mx/my/home/content
/glaf/mx/my/home/footer
```

业务页统一入口：

```text
/glaf/mx/form/page/viewPage?id={pageId}
```

## 数据面

| 用途 | 路径 |
|------|------|
| 菜单 | `POST /glaf/mx/form/menuData/data` |
| 表格 | `POST /glaf/mx/form/data/gridData` |
| 树表 | `POST /glaf/mx/form/treelist/gridData` |
| 下拉 | `POST /glaf/mx/form/combo/comboboxData` |
| 数据集 | `GET /glaf/mx/dataset/allJSON?id=` |
| 附件上传 | `/glaf/mx/form/attachment?method=upload&to=to_db&randomParent=` |
| 附件下载 | `/glaf/mx/form/attachment?method=download&from=to_db&id=` |
| 流程提交 | `POST /glaf/mx/form/workflow/defined/submit` |
| Activiti 任务 | `/glaf/mx/activiti/task?processInstanceId=` |
| 服务编排 | `/glaf/mx/serviceorchest/serviceProcess/runProcess` |

常见 POST JSON：

```json
{"params":"{}","id":"<id>","rid":"<id>"}
```

## 前端事件（规则引擎）

从 `bootstrap.extend.all.min.js` 可见的页面动作包括：

- `mtLogin` / `mtSubmit` / `mtAssign0` / `mtBack0`
- `mtReject0` / `mtCancel0` / `mtStop0` / `mtActive0`
- 打开子页、附件、CA 登录相关扩展

登录页 `pageed` 将按钮 click 编排为：取用户名/密码 → `mtLogin`。

## Cookie

| Cookie | 含义 |
|--------|------|
| `JSESSIONID` | Resin 会话 |
| `GLAF_COOKIE` | 应用票据 |
| `GLAF_JWT_COOKIE` | JWT（HS256） |

## 服务器指纹

- `Server: nginx`
- 错误页：`Resin/4.0.65`，`Server: 'app-0'`
- Java 包名：`com.glaf.serviceorchest...`
