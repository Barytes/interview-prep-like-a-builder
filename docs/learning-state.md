# 学习记录、会话记录与教学反馈放在哪里

术语见 [CONTEXT.md](../CONTEXT.md)。三种记录各自维护：

| 内容 | 位置 | 维护者 |
| --- | --- | --- |
| 岗位 JD 与来源 | `tests/roles/<岗位>/岗位JD.md` 及 `sources/` | 开发 |
| 一轮岗位准备的学习记录 | `tests/roles/<岗位>/learning-state/<准备编号>/` | `track-progress` |
| 测试会话的归档 | `tests/roles/<岗位>/runs/<日期>-<会话ID>/` | 用户显式调用 `save-trace` |
| 全局教学反馈与改进项 | `docs/feedback.md` | `note-feedback` |
| 岗位项目成果 | 岗位目录的 `projects/<项目>/`，或用户指定位置 | `build-with-me` |

准备编号可以采用开始日期，同名目录添加序号。通过 [岗位索引](../tests/README.md) 找到学习记录；新建、重新开始或结束一轮准备后同步索引。

同一轮岗位准备共用学习记录。同一测试会话以会话 ID 标识，显式归档时创建 runs 目录，再次调用更新同一归档。技能切换和学习进度更新不触发归档。

会话记录保存发生过的对话和工具事件；教学反馈保存用户评价、建议和改进进展。已有归档时反馈引用具体事件，没有归档时先保留原话和会话出处。

格式见 [学习记录](../skills/track-progress/references/state.md)、[会话归档](../skills/save-trace/references/archive.md) 和 [教学反馈](../skills/note-feedback/references/records.md)。
