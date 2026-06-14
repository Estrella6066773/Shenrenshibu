# 冒烟测试执行记录（UAT）



| 字段 | 值 |

|------|-----|

| 状态 | 持续维护 |

| 最后更新 | 2026-06-14（batch 十一项：UAT-001~003/010/011/036/050/112） |

| 用例来源 | [交付-核心循环冒烟测试.md](交付-核心循环冒烟测试.md) |



## 自动化（无需手动 Play）



| 编号 | 命令 / 入口 | 最近结果 | 日期 |

|------|-------------|----------|------|

| **预检总表** | `python Docs/程序设计/05-交付/verify-uat-preflight.py` | **通过** | 2026-06-14 |

| UAT-036a | `python Docs/程序设计/05-交付/verify-assignment-daily-scene.py` | **通过** | 2026-06-14 |

| UAT-110/111（静态） | 预检总表含 Editor 菜单与搭建入口 | **通过** | 2026-06-14 |

| REQ-MSG-005（静态） | 预检总表含 `SortSessionList` | **通过** | 2026-06-14 |

| UAT-001~003 | PlayMode `CoreBusGateUat001PlayModeTests`（3 项） | **通过** | 2026-06-14 |

| UAT-010/050/112 | PlayMode `CoreLoopUat010050112PlayModeTests`（3 项） | **通过** | 2026-06-14 |

| UAT-011 | EditMode `CoreLoopUat011EditModeTests` | **通过** | 2026-06-14 |

| UAT-115 | `python Docs/程序设计/05-交付/verify-uat-data-assets.py` | **通过** | 2026-06-14 |

| UAT-036a′ | EditMode 测试（3 项含 UAT-011） | **通过** | 2026-06-14 |

| UAT-036b | PlayMode 测试（8 项） | **通过** | 2026-06-14 |



## 一键验收（神人事部 Unity）



| 方式 | 说明 |

|------|------|

| **菜单** | **神人事部 → 验收 → 运行全部 UAT-036 测试**（EditMode 3 + PlayMode 8，合计 **11** 项） |

| **batch** | `powershell -File Docs/程序设计/05-交付/run-uat036-tests.ps1`（须先关闭占用本工程的 Unity 实例） |

| **GUI 触发** | `powershell -File Docs/程序设计/05-交付/request-uat036-gui-run.ps1`（Editor 已打开时；读 `Temp/uat036-run.result`） |



日志：`Logs/uat036-batch-exec.log`（检索 `[UAT-036 batch]`）。



## 人工 Play（待勾选）



| 编号 | 通过 | 执行人 | 日期 | 备注 |

|------|:----:|--------|------|------|

| UAT-001 ~ UAT-003 | ☑ | 自动化 | 2026-06-14 | PlayMode |

| UAT-010 | ☑ | 自动化 | 2026-06-14 | PlayMode 跨天 |

| UAT-011 | ☑ | 自动化 | 2026-06-14 | EditMode 幂等键静态检 |

| UAT-012 ~ UAT-035 | ☐ | | | |

| UAT-036 | ☑ | 自动化 | 2026-06-14 | PlayMode 2 项 + 场景预检 |

| UAT-040 ~ UAT-114 | ☐ | | | |

| UAT-115 | ☑ | 自动化 | 2026-06-14 | `verify-uat-data-assets.py` |

| UAT-050 | ☑ | 自动化 | 2026-06-14 | PlayMode `ApplyStressDelta` |

| UAT-112 | ☑ | 自动化 | 2026-06-14 | PlayMode Bootstrap |

| UAT-116 ~ UAT-126 | ☐ | | | |



## MCP 说明



须先在该 Unity 实例中打开 **D:/Unity/神人事部**；若 MCP 连的是其他工程（如机魂），`run_tests` 不会验收本仓库。

