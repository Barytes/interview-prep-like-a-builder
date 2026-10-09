# 当前交接：显式归档与教学反馈

日期：2026-10-09（Asia/Shanghai）。项目：`interview-prep-like-a-builder`。工作分支：`codex/split-interview-prep-skills`。

## 当前组织

[prep-me](../skills/prep-me/SKILL.md) 选择任务；两个教学 skill 执行教学或做项目；[track-progress](../skills/track-progress/SKILL.md) 保存学习记录。

[note-feedback](../skills/note-feedback/SKILL.md) 仅整理用户评价与改进项。[save-trace](../skills/save-trace/SKILL.md) 仅在用户显式调用时归档当前 Codex 会话，保存运行信息、对话及工具事件，生成阅读视图。二者通过事件引用关联，不互相触发。

[CONTEXT.md](../CONTEXT.md) 定义测试会话（run）、会话记录（trace）、归档和运行信息。此前按任务维护 trials 的方案已由按会话 ID 归档 runs 取代，此前未生成实际 trials 文件。

## 接下来做什么

先推进 WorkBuddy 岗位准备。用户对 personal agent 感兴趣，具体项目尚未决定，正式开始时结合准备期限和投入确定范围。

[全局教学反馈](feedback.md) 保存开发要求及改进项，实际教学效果由用户后续试用反馈确认。需要留存测试会话时，由用户显式调用 save-trace；本次开发对话不自动归档到岗位。

## 迁移与来源

源项目为 `/Users/beiyanliu/Desktop/12 week year`。迁入材料包括原技能、方法与交接，以及三个岗位 JD。完整旧版见 [历史材料](history/README.md)，JD 与来源状态见 [岗位索引](../tests/README.md)。

WorkBuddy JD 于 2026-10-09 从腾讯官方接口取得，OpenAI JD 同日从官方页面读取。TAB 官方接口当时返回 HTTP 500，保留 2026-09-09 的采集记录，当前开放情况待查。原始迁移说明见 [交接原文](history/材料/handoff-2026-10-09-独立项目迁移.md)。

## 验证

归档脚本的 8 项测试通过，覆盖逐轮模型、工具事件、反馈文件不变、重复归档、未提交文件快照、日志尾部写入及旧记录保护。当前会话日志另做只读解析检查，未在岗位目录中生成 run。

六个 skill 均通过格式验证；70 个本地 Markdown 链接及锚点有效。save-trace 的隐式调用已关闭，其余技能保持原调用方式；教学效果仍待真实试用。
