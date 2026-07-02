# Unity 资源与数据目录

| 字段 | 内容 |
|------|------|
| 状态 | 已定稿（基线） |
| 最后更新 | 2026-05-26 |
| 关联 | [实现-数据资产布局](../04-实现/实现-数据资产布局.md)、[仓库布局.md](../../仓库布局.md) |

## Assets 编号目录

| 目录 | 用途 |
|------|------|
| `01_Scripts/` | 全部 C#；按功能模块分子文件夹 |
| `02_Arts/` | 美术 |
| `03_Prefab/` | 预制体 |
| `04_Data/` | **运行时策划数据主目录**（SO、对话、邮件事件等） |
| `05_Scenes/` | 场景（`主菜单` Build 0、`主场景` Build 1） |
| `06_Animation/` | 动画 |

文档：`Docs/`（仓库根，Git 管理，不导入 Unity）。

## `04_Data` 分区（摘要）

| 区域 | 路径模式 | 用途 |
|------|-----------|------|
| 对话与剧情 | `04_Data/对话dat/` | 频道、角色库、剧情演出 |
| 消息系统 | `04_Data/MessageSystem/` | 邮件事件、模板库 |
| 标签 | `04_Data/标签系统/` | `EmployeeTagSO` 等 |
| 压力 | `04_Data/压力系统/` | 压力事件定义 |

完整表见 `Docs/03-程序设计/04-实现/实现-数据资产布局.md`。

## `04_Data` 与菜单常量

`ShenRenShiBuAssetMenu` 的通用创建入口已统一指向 `Assets/04_Data/`。新增 SO 应按模块落入下列正式目录，不再使用 `Assets/00_Data/` 作为默认创建目标。

| 类型 | 默认路径 |
|------|----------|
| 标签 | `04_Data/标签系统/标签类型/` |
| 简历模板 | `04_Data/简历系统/Templates/` |
| 委托 | `04_Data/委托系统/` |
| 证件照 | `04_Data/证件照/` |
| 对话与剧情 | `04_Data/对话dat/` |
| 邮件 | `04_Data/MessageSystem/` |

## 脚本模块 ↔ 数据

| 模块 | 典型 SO / 数据路径 |
|------|-------------------|
| Employee | `04_Data/标签系统/` |
| Assignment | `04_Data/` 下委托相关（见 IMPL） |
| MessageSystem | `04_Data/MessageSystem/` |
| DialogSystem | `04_Data/对话dat/` |
| Stress | `04_Data/压力系统/` |

## 测试程序集

| asmdef | 路径 | 用途 |
|--------|------|------|
| `_01_Scripts` | `01_Scripts/_01_Scripts.asmdef` | 运行时代码主程序集 |
| `_01_Scripts.Editor` | `01_Scripts/Editor/` | 编辑器工具 |
| `PlayModeTests` | `01_Scripts/Tests/PlayMode/PlayModeTests.asmdef` | PlayMode UAT |
| `Tests.Editor` | `01_Scripts/Tests/Editor/Tests.Editor.asmdef` | EditMode UAT |

## 仓库卫生记录

| 项 | 建议 |
|----|------|
| `Assets/MailTemplateDatabaseSO.cs` 根目录散落 | 迁入 `04_Data/MessageSystem/` 或 `01_Scripts` 旁路并删根目录副本 |
| `Assets/00_OldDocs/` | 2026-06-29 已确认空目录并删除 |
| `Assignment/Docs/TaskInteractionEffectSystem.md` | 2026-06-29 已迁入 [任务内交互效果](../02-运行时逻辑/任务内交互效果.md) |
| 根目录 `a.aseprite`、`b.aseprite` | 2026-06-29 已移入 `Assets/02_Arts/` |

## 修订记录

| 日期 | 说明 |
|------|------|
| 2026-05-26 | 初稿：对齐 `实现-数据资产布局` 与仓库布局 |
| 2026-06-29 | `ShenRenShiBuAssetMenu` 创建路径收敛到 `04_Data`；补充测试 asmdef 对照 |
