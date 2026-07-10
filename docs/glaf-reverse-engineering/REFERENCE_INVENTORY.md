# 行业内外可参考 / 可互用产品与代码清单

> 目的：为自研「公路工程质检 + 文控」类系统提供可落地的参考与复用清单。  
> 范围：开源仓库、低代码底座、工作流/表单/表格组件、文档与签章、国内外商业对标、AI 辅助。  
> 原则：**学业务与交互，复用通用引擎；行业规则与施表模板需自建。**  
> 调研日期：2026-07-10（星标数为当时 GitHub 近似值，会变动）

---

## 0. 怎么用这份清单

按开发阶段选型，而不是「全部引入」：

| 阶段 | 优先看 |
|------|--------|
| MVP 底座 | 若依 / JeecgBoot + Warm-Flow/Flowable + MinIO |
| 质检表（类 Excel） | Univer / FortuneSheet（或商业 SpreadJS） |
| 结构化表单 | form-create / Formily / form-js |
| 文控归档 | Paperless-ngx / Mayan（参考）或自研元数据层 |
| 签章 | 开放签（评估 AGPL）或商业 CA |
| 业务对标 | GLAF、华岩、恒智天成、筑业、海特；海外 Procore/ACC/Fieldwire |
| BIM 后置 | Speckle / web-ifc（赋能，非首期） |

**许可证提醒**：AGPL（MinIO、ONLYOFFICE、开放签、Steedos 等）对 SaaS/网络提供服务有传染风险，商用前必须法务评估；Apache/MIT 更适合作为产品内核依赖。

---

## 1. 强烈建议优先评估（可直接支撑开发）

### 1.1 国内快速开发底座（Java + Vue）

| 名称 | 链接 | License | Stars≈ | 可复用点 | 建议用法 |
|------|------|---------|--------|----------|----------|
| **RuoYi-Vue** | https://github.com/yangzongzhuan/RuoYi-Vue | MIT | 3.1k | 登录权限、代码生成、后台骨架 | **首选脚手架**，其上做 WBS/质检模块 |
| **JeecgBoot** | https://github.com/jeecgboot/JeecgBoot | Apache-2.0 | 47k | Online 表单、报表、代码生成 | 表单/报表密集时优先；流程相对轻 |
| **Warm-Flow** | https://github.com/dromara/warm-flow | Apache-2.0 | 0.6k | 轻量审批（7 表）、仿钉钉设计器 | **签认流首选**；比 Flowable 更易落地 |
| **oa-flow-pms** | https://gitee.com/anan6527/oa-flow-pms | 见仓库 | - | 若依 + Warm-Flow + uni-app 工程 OA | 参考「工程项目管理 + 移动端」拼装方式 |
| **form-create** | https://github.com/xaboy/form-create | MIT | 7.1k | JSON 驱动动态表单 + 设计器 | 结构化施表（养护记录类） |
| **Formily** | https://github.com/alibaba/formily | MIT | 12.6k | 高性能 JSON Schema 表单 | 复杂联动/校验表单 |
| **vxe-table** | https://github.com/x-extends/vxe-table | MIT | 8.6k | 大数据表格、树表 | WBS 列表、任务台账 |

**建议组合（MVP）**：

```text
RuoYi-Vue (或 JeecgBoot)
  + Warm-Flow（工序签认审批）
  + form-create（结构化表）
  + Univer/FortuneSheet（网格实测表）
  + MinIO（附件，注意 AGPL）或自建 S3 兼容存储
  + PostgreSQL
```

### 1.2 类 Excel 表格引擎（对标 GLAF 的 SpreadJS）

| 名称 | 链接 | License | Stars≈ | 说明 |
|------|------|---------|--------|------|
| **Univer** | https://github.com/dream-num/univer | Apache-2.0 | 13.8k | Luckysheet 官方继任；可嵌入 + 服务端算表；**首选开源替代** |
| **FortuneSheet** | https://github.com/ruilisi/fortune-sheet | MIT | 3.6k | Luckysheet TS 分支，React/Vue 友好 |
| **Handsontable** | https://github.com/handsontable/handsontable | 双许可 | 22k | 体验好，商用需买许可 |
| **SpreadJS（商业）** | 葡萄城 | 商业 | - | GLAF/R 平台同款路线；预算允许可直接买，省适配成本 |

**建议**：MVP 用 Univer；若客户强依赖 Excel 版式/打印，评估 SpreadJS 商业版 ROI。

### 1.3 工作流引擎

| 名称 | 链接 | License | 适用 |
|------|------|---------|------|
| **Warm-Flow** | 见上 | Apache-2.0 | 国内审批、轻量签认（推荐首期） |
| **Flowable** | https://github.com/flowable/flowable-engine | Apache-2.0 | 复杂 BPMN、与 Jeecg/RuoYi 生态成熟 |
| **Camunda 7 CE** | https://github.com/camunda/camunda-bpm-platform | Apache-2.0 | 已 EOL，仅作参考；新项目看 Camunda 8 |
| **form-js** | Camunda Forms | 开源 | 流程任务表单 JSON Schema |
| **WorkFlow-Engine (有生博乐)** | https://github.com/risesoft-y9/WorkFlow-Engine | GPL-3.0 | 机关/单位流程实践，注意 GPL |
| **驰骋 CCFast / Ruoyi-JFlow** | https://github.com/ccbpm/CCFast | GPL-3.0 | 老牌流程+表单，信创场景可参考 |

GLAF 实测有 Activiti 痕迹 → 自研选 **Flowable 或 Warm-Flow** 即可兼容同类模型。

---

## 2. 建筑 / 工程领域开源（可参考业务，慎直接当产品内核）

| 名称 | 链接 | License | Stars≈ | 可借鉴 | 局限 |
|------|------|---------|--------|--------|------|
| **OpenConstructionERP** | https://github.com/datadrivenconstruction/OpenConstructionERP | AGPL-3.0 | 0.5k | CDE 文档流、检查清单、NCR、Punch List、质量门 | 偏欧美 BOQ/造价；AGPL；非中国公路施表 |
| **road-engineering-inspection** | https://github.com/Gan-Xing/road-engineering-inspection | - | 低 | 桩号问题闭环、图片对比验收 | 玩具级，仅作交互原型 |
| **inspection_ai_pilot** | https://github.com/ck-unifr/inspection_ai_pilot | MIT | 低 | 规范 RAG + IoT Mock + 自动判定报告 | AI 演示，非业务系统 |
| **DDC Skills for AI Agents** | https://github.com/datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction | MIT | 0.2k | 建造领域 AI Agent 技能清单 | 方法论，非系统 |

**结论**：海外开源强在「检查清单 / CDE / NCR」抽象；中国公路「施表 + 评定 + 文控归档」几乎没有可直接 fork 的完整开源产品，**必须自建领域层**。

---

## 3. 文档管理 / 文控 / 档案（可互用或参考）

| 名称 | 链接 | License | Stars≈ | 用法建议 |
|------|------|---------|--------|----------|
| **Paperless-ngx** | https://github.com/paperless-ngx/paperless-ngx | GPL-3.0 | 43k | OCR、标签、归档检索；可作「档案库」旁路，不宜当业务主库 |
| **Mayan EDMS** | https://github.com/mayan-edms/Mayan-EDMS | GPL/见站 | 0.8k | 元数据、工作流、分类；学模型，或 API 对接 |
| **Alfresco Community** | https://github.com/Alfresco/alfresco-community-repo | LGPL-3.0 | 0.2k | 企业 ECM/记录管理参考；偏重，不建议 MVP 引入 |
| **ONLYOFFICE Docs** | https://github.com/ONLYOFFICE/DocumentServer | AGPL-3.0 | 6.7k | 在线预览/编辑 Office；打印前预览可考虑 |
| **MinIO** | https://github.com/minio/minio | AGPL-3.0 | 61k | 对象存储事实标准；注意 AGPL，或用兼容实现 |

**自研文控建议**：业务库自建（WBS 挂接 + 表单实例 + 元数据），对象存 MinIO/S3；归档检索可后期对接 Paperless/Mayan，而不是反过来。

---

## 4. 电子签章 / CA

| 名称 | 链接 | License | 说明 |
|------|------|---------|------|
| **开放签 kaifangqian-base** | https://github.com/kaifangqian/kaifangqian-base | AGPL-3.0 | 手写签、印章、关键字定位；可学前端交互；商用注意 AGPL + CA 云盾 |
| 法大大 / e签宝 / 契约锁 等 | 商业 | - | 生产环境更稳妥，按项目对接 API |
| 国密算法库（BouncyCastle 等） | 开源组件 | - | 自建签章时的算法层 |

GLAF 有 NetCA / 本地 CA 客户端痕迹 → 自研应 **预留签章 SPI**，首期可用图片签/开放签演示，试点再接正式 CA。

---

## 5. 低代码 / 无代码平台（对标 GLAF R 平台思路）

| 名称 | 链接 | License | 建议 |
|------|------|---------|------|
| **NocoBase** | https://github.com/nocobase/nocobase | 开源+商业 | 数据模型驱动，适合快速搭后台；注意协议分层 |
| **Steedos 华炎魔方** | https://github.com/steedos/steedos-platform | AGPL-3.0 | 对象/流程/权限一体；AGPL 需谨慎 |
| **Appsmith** | https://github.com/appsmithorg/appsmith | Apache-2.0 | 内部工具/管理屏，不适合当核心业务壳 |
| **JeecgBoot** | 见上 | Apache-2.0 | 国内最接近「表单+报表低代码」的务实选择 |

**建议**：不要首期重做 GLAF 级无编码平台；用 Jeecg/NocoBase **加速配置层**，核心质检域仍用代码掌控。

---

## 6. BIM / 模型互用（后置能力）

| 名称 | 链接 | License | 用途 |
|------|------|---------|------|
| **ThatOpen web-ifc** | https://github.com/ThatOpen/engine_web-ifc | MPL-2.0 | 浏览器读 IFC |
| **Speckle** | https://github.com/specklesystems | 多仓 | AEC 数据互通中间层 |
| Autodesk ACC / BIM 360 | 商业 | - | 文档+模型协同对标 |

与华闽通达「不做 BIM，为 BIM 赋能」一致：**先有 WBS/质检数据，再挂模型**。

---

## 7. 国内外商业产品（业务对标，非代码复用）

### 7.1 国内（公路质检/资料强相关）

| 产品/厂商 | 对标价值 |
|-----------|----------|
| **华闽通达 GLAF / R 平台** | 本项目主对标：WBS+文控+质检表 |
| **华岩** | 质检资料 + 电子档案一体化 |
| **恒智天成** | 公路资料软件、地方用表覆盖广 |
| **筑业** | 资料编制与标准用表 |
| **海特科技** | 质检评定数字化、移动填报 |
| **广联达数字项目管理** | 总控/计量/平台化参考 |
| **鲁班 / iworks** | 同环境已分析：微服务总控与质检待办（见 `docs/iworks-system-analysis.md`） |

### 7.2 海外（学交互与模块边界）

| 产品 | 对标价值 |
|------|----------|
| **Procore** | 现场协同、质量安全、文档、移动端 |
| **Autodesk Construction Cloud** | 文档版本、RFI/提交物、图纸协同 |
| **Fieldwire** | 工地任务、整改、检查清单、图纸标注 |
| **Oracle Aconex** | 多方文控、责任留痕 |
| **InEight / HCSS** | 大型基建管控与现场数据 |

**可抄的不是界面皮肤，而是**：检查清单闭环、提交物状态机、移动优先、版本单一事实源。

---

## 8. 按能力映射到自研模块

| 自研模块 | 可复用/参考 | 必须自建 |
|----------|-------------|----------|
| 账号权限 | RuoYi / Jeecg | 标段数据范围规则 |
| WBS 树 | vxe-table 树 + 自研模型 | 公路编码、专业类型、用表映射 |
| 工序签认流 | Warm-Flow / Flowable | 施工/监理双轨状态机 |
| 结构化施表 | form-create / Formily | 施表字段与校验 |
| 网格实测表 | Univer / FortuneSheet / SpreadJS | 测点规则、合格率计算 |
| 待办首页 | 流程引擎任务 API | 跨模块聚合口径 |
| 文件管控 | MinIO + 自研元数据；参考 Paperless | WBS 挂接、四性元数据 |
| 打印 PDF | ONLYOFFICE / 自研模板 / Excel 导出 | 贴近纸质施表版式 |
| 电子签章 | 开放签 / 商业 CA | 证书策略、法律责任 |
| 统计评定 | 自研 + 预聚合 | F80 评定规则 |
| 移动填报 | uni-app（oa-flow-pms 参考） | 离线与现场体验 |
| AI 辅助 | inspection_ai_pilot 思路 | 规范库与提示词治理 |

---

## 9. 推荐「技术购物车」（按优先级）

### A. 开箱可组 MVP（推荐）

1. RuoYi-Vue（MIT）  
2. Warm-Flow（Apache-2.0）  
3. form-create（MIT）  
4. Univer（Apache-2.0）  
5. PostgreSQL + Redis  
6. 对象存储：MinIO（评估 AGPL）或云厂商 S3  

### B. 增强项（试点后）

7. Flowable（复杂流程时升级）  
8. 开放签或商业 CA  
9. Paperless-ngx / Mayan（归档检索旁路）  
10. uni-app 移动端  
11. web-ifc / Speckle（BIM 挂接）  

### C. 仅作对标、不引入代码

- GLAF、华岩、恒智天成、筑业、海特  
- Procore、ACC、Fieldwire  
- OpenConstructionERP（学质量门与 CDE，慎用 AGPL 内核）  

---

## 10. 风险与选型红线

1. **不要指望 GitHub 上有「中国公路施表完整开源系统」**——调研显示几乎空白。  
2. **AGPL 组件**（MinIO、ONLYOFFICE、开放签、Steedos、OpenConstructionERP）商用前必须确认合规策略。  
3. **低代码平台**可加速，但不能替代 WBS/评定领域模型。  
4. **表格引擎**是体验关键路径：尽早 POC「施表100 类网格 + 打印」。  
5. **海外工程 ERP** 的质量模块 ≈ 检查清单/NCR，与国内「评定用表体系」不是同一产品，避免错误对标。  

---

## 11. 下一步行动（可执行）

1. 用 RuoYi + Warm-Flow 搭空壳，导入一份合同段 WBS Demo。  
2. 用 form-create 做 1 张结构化施表，用 Univer 做 1 张网格施表。  
3. 跑通「填报 → 监理退回/签认 → 待办」。  
4. 同步建立《施表模板库》资产（对标恒智/筑业/华岩的用表覆盖，而不是抄代码）。  
5. 法务评审 MinIO/签章组件许可证。  

---

## 12. 相关文档

- 系统逆向总览：`docs/glaf-reverse-engineering/README.md`  
- 开发计划：`docs/glaf-reverse-engineering/DEVELOPMENT_PLAN.md`  
- API 笔记：`docs/glaf-reverse-engineering/API_NOTES.md`  
- 对照系统（鲁班/iworks）：`docs/iworks-system-analysis.md`（若分支已合并）
