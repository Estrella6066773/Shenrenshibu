---
id: LORE-OBS-002
title: 观测：人事部KPI与街面压力迹象
domain: observation
type: behavioral-signal
status: draft
stability: medium
source: 组织记录
confidence: B
owner: worldbuilding
review_cycle: monthly
links:
  relates_to: [LORE-ENT-ORG-001, LORE-REL-001, LORE-ENT-CHR-002]
  depends_on: [LORE-ENT-ORG-001]
  contradicts: []
visibility:
  author: full
  role: partial
  player: partial
  system: full
---

## 定义

- 本词条归纳玩家在人事部语境下**可感知、可量化或可对标的压力迹象**，为任务生成与 UI 表现提供观测层接口；不新增科室职权，四科真值仍以 `LORE-ENT-ORG-001` 与 `LORE-REL-001` 为准。

## 可观测现象

- **预算线**：服务科工单积压与财务科「预算冻结」弹窗、临时收费项增多同向出现；民生窗口关闭时段拉长。
- **秩序线**：防卫科封控区扩大与「临时通行证」发放规则变严；街面盘查抽样率上升。
- **人力线**：人力科绩效提醒频率上升、编组强制打散重组；玩家调度界面出现「监察关注」标记类 UI 隐喻。
- **冲突外化**：科室间互相抄送、驳回理由模板化、部长办公室传唤频率可作为四科张力升压的轻量信号。

## 验证与溯源

- 上述迹象应与 `LORE-REL-001` 中财务—服务、人力—防卫冲突链一致；玩家为管理者 AI 时的个人压力节点见 `LORE-ENT-CHR-002`。

[投放注记]
- audience: 作者 | 角色 | 玩家 | 系统
- window: 人事部主线交互起
- channel: 内网邮件 / KPI 仪表盘 / 科室广播 / 任务 debuff 文案
- distortion: 对外宣传口可仍称「卓越运营」「安全赋能」
