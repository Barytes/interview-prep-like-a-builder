# 岗位资料、学习记录与会话归档

三个岗位分别保存 JD、来源快照和学习记录。当前优先推进 WorkBuddy；正式开始教学时再确定项目期限、投入与首版范围。

| 岗位与 JD | JD 来源状态 | 试用与项目状态 |
| --- | --- | --- |
| [腾讯深圳 WorkBuddy — Agent Harness 研发工程师](roles/Tencent-WorkBuddy-Agent-Harness/岗位JD.md) | 2026-10-09 取得官方接口原文；岗位更新于 2026-09-21 | [2026-10-09 开始学习 JD 所需知识](roles/Tencent-WorkBuddy-Agent-Harness/learning-state/2026-10-09/MISSION.md)，已能口头解释基础工具结果问题；2026-10-10 根据诊断讲解上下文压缩、多 Agent 编排与实验设计；项目未确定 |
| [腾讯深圳 TAB 实验中台 — 数据科学](roles/Tencent-TAB-Data-Science/岗位JD.md) | 保留 2026-09-09 采集的官方接口原文；岗位更新于 2026-07-09；2026-10-09 刷新未成功 | 已选岗位样本；新版试用未开始 |
| [OpenAI — Applied AI Engineer, Codex Core Agent](roles/OpenAI-Applied-AI-Engineer-Codex-Core-Agent/岗位JD.md) | 2026-10-09 读取官方页面；保留 2026-10-07 的中文摘要 | 存在下方历史学习记录；新版试用未开始 |

## OpenAI 历史试用

[2026-10-07-1h-fresh](roles/OpenAI-Applied-AI-Engineer-Codex-Core-Agent/learning-state/2026-10-07-1h-fresh/MISSION.md) 中保留了 [岗位与项目说明](roles/OpenAI-Applied-AI-Engineer-Codex-Core-Agent/learning-state/2026-10-07-1h-fresh/WORLD_MODEL.md) 和 [进度](roles/OpenAI-Applied-AI-Engineer-Codex-Core-Agent/learning-state/2026-10-07-1h-fresh/PROGRESS.md)，最后更新至 2026-10-09。原索引“仅保留 JD，新测试未开始”已与文件事实不符，本索引据实际文件修正。

这些记录保存当时的教学与用户表达，供复盘使用。新课的掌握情况依据新课中的表达和行动判断，原来的 1 小时时间预算保持历史语境。

## 怎样使用与验证

从 [prep-me](../skills/prep-me/SKILL.md) 开始，也可直接调用两个教学 skill。[track-progress](../skills/track-progress/SKILL.md) 保存学习记录并读取本轮教学反馈，[note-feedback](../skills/note-feedback/SKILL.md) 将教学评价保存在同目录的 `FEEDBACK.md`。WorkBuddy 的已有评价见 [本轮反馈](roles/Tencent-WorkBuddy-Agent-Harness/learning-state/2026-10-09/FEEDBACK.md)。

用户显式调用 [save-trace](../skills/save-trace/SKILL.md) 时，才在目标岗位的 `runs/` 中归档会话记录。一个 run 对应一个会话 ID，再次调用更新原归档；具体位置见 [存放约定](../docs/learning-state.md)。

会话记录保留实际对话、工具事件和运行信息，本轮教学反馈引用其中的具体事件。skill 开发的 [公共改进项](../docs/feedback.md) 再引用具体反馈。归档过程不评分、不生成改进项。

归档脚本测试位于 `tests/save-trace/`，用临时目录与模拟日志验证导出行为。教学效果由实际使用中的用户表现与反馈判断。
