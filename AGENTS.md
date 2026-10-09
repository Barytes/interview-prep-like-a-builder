# 项目约定

本仓库用于开发和试用面试准备 skills。修改技能、文档或目录时承担开发职责；实际帮助用户准备岗位时承担测试职责。坚持 strong opinion, weakly held：直接表达观点，根据新事实调整。

用语以 [CONTEXT.md](CONTEXT.md) 为准。调用 skill 时使用环境提供的技能调用能力；文件式环境通过 [技能索引](README.md#技能入口) 读取相应 `SKILL.md` 并执行，已读取且未变化的内容直接复用。

## 开发职责

先理解目录和术语，再修改相关文件。保持提示词简短，公共流程维护一份，参考资料按需读取。

| 位置 | 职责 |
| --- | --- |
| `CONTEXT.md` | 项目术语与定义 |
| `skills/prep-me/` | 统一入口，选择并衔接当前任务 |
| `skills/teach-me/`、`skills/build-with-me/` | 教学、做项目及教学判断 |
| `skills/track-progress/` | 学习记录、共同教学约定与学习记录格式 |
| `skills/note-feedback/` | 教学反馈及全局改进项 |
| `skills/save-trace/` | 显式归档会话记录与运行信息，包含导出脚本 |
| `docs/feedback.md` | 全局教学反馈；开发时读取相关改进项 |
| `docs/learning-state.md` | 各类记录的存放位置 |
| `tests/roles/` | 岗位资料、学习记录和显式归档的 runs；索引见 `tests/README.md` |
| `tests/save-trace/` | 归档脚本测试，使用临时目录与模拟日志 |
| `docs/handoff.md`、`docs/history/` | 当前交接与历史材料 |

用户要求改进技能时，查阅相关教学反馈；修改后通过 `note-feedback` 更新改进项，效果由实际使用中的用户反馈确认。

## 测试职责

帮助用户像 builder 一样准备面试：认识岗位、学会知识、参与完成能演示且能解释的项目。

默认使用 `prep-me`，也可直接使用两个教学 skill。`track-progress` 维护学习记录，`note-feedback` 整理用户评价，`save-trace` 仅在用户显式调用时归档会话。

trace 保存发生过的对话与工具事件，feedback 保存用户评价及改进进展，二者通过事件引用关联。其他 skill 的调用和教学反馈记录不触发会话归档。位置见 [存放约定](docs/learning-state.md)。
