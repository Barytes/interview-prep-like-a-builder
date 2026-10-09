# Prepare for Interviews Like a Builder

像 builder 一样准备面试：理解目标岗位的工作，学会所需知识，参与完成能演示、能解释、能继续改进的项目。

从 `prep-me` 开始，告诉 Codex 你要准备什么或继续做什么。它选择教学或做项目，沿用学习记录；你对教学方式的评价由 `note-feedback` 单独保存。

## 技能入口

| Skill | 用途 |
| --- | --- |
| [prep-me：帮我准备面试](skills/prep-me/SKILL.md) | 选择并衔接当前任务 |
| [teach-me：教我](skills/teach-me/SKILL.md) | 认识岗位、讲解、练习和补课 |
| [build-with-me：和我一起做项目](skills/build-with-me/SKILL.md) | 选题、需求、方案、实现、验收和改进 |
| [track-progress：记录目标和进度](skills/track-progress/SKILL.md) | 读取和保存学习记录，提供共同教学约定 |
| [note-feedback：记下反馈](skills/note-feedback/SKILL.md) | 保存用户评价，整理全局改进项 |
| [save-trace：保存本次会话](skills/save-trace/SKILL.md) | 显式调用时归档当前会话及运行信息 |

技能在当前 Codex 对话中执行。两个教学 skill 可直接使用，公共学习记录通过 `track-progress` 维护。`save-trace` 关闭隐式调用，只有用户明确调用时才执行归档。

## 使用方法

```bash
git clone https://github.com/Barytes/interview-prep-like-a-builder.git
```

在 Codex 中打开仓库，读取 [AGENTS.md](AGENTS.md)，例如：

```text
请使用 skills/prep-me/SKILL.md，
以 tests/roles/Tencent-WorkBuddy-Agent-Harness/岗位JD.md 为目标，
先帮助我认识加入团队后的工作，再安排学习和项目。
我的相关经验：……
准备期限与每周投入：……
```

需要保存会话时，明确调用：

```text
请使用 skills/save-trace/SKILL.md，
将当前测试会话归档到 WorkBuddy 岗位的 runs 目录。
```

环境已发现技能时可用 `$prep-me` 或 `$save-trace`。分发时提供六个 skill、根目录 AGENTS.md 和 CONTEXT.md，记录位置由使用方工作目录约定。

## 三种记录

| 记录 | 保存什么 | 维护者 |
| --- | --- | --- |
| 学习记录 | 准备目标、岗位与项目说明、学习表现与进度 | `track-progress` |
| 会话记录（trace）及运行信息 | 实际对话、工具事件、模型、harness、技能版本与归档范围 | 显式调用 `save-trace` |
| 教学反馈（feedback） | 用户评价、偏好、改进建议及处理进展 | `note-feedback` |

学习记录仍保存为 `MISSION.md`、`WORLD_MODEL.md` 和 `PROGRESS.md`。一轮岗位准备可跨多次对话，继续准备时共用记录。

一个测试会话（run）对应一个 Codex 会话 ID，可包含多个任务和技能切换。同一会话重复归档更新相同目录，保留历次归档信息与技能快照；每次保存截至调用时已经落盘的内容。

trace 中的评价原话是对话事实，归档不会自动生成教学反馈或评分。全局教学反馈通过事件 ID 引用已有归档；尚未归档时先保存原话与会话出处。

术语见 [CONTEXT.md](CONTEXT.md)，位置见 [记录存放约定](docs/learning-state.md)，字段与导出范围见 [归档说明](skills/save-trace/references/archive.md)。

## 项目结构

```text
AGENTS.md                     开发与测试职责
CONTEXT.md                    术语与定义
skills/                       六个技能及各自参考文件
tests/
  README.md                   岗位资料与记录索引
  save-trace/                 归档脚本测试
  roles/<岗位>/
    岗位JD.md
    sources/                  来源快照
    learning-state/           学习记录
    runs/                     显式归档时创建
      <日期>-<会话ID>/
        run.md                运行信息阅读视图
        run.json              运行信息与历次归档
        trace.jsonl           会话事件
        conversation.md       对话阅读视图
        skill-snapshot/       各次归档时的技能快照
docs/
  feedback.md                 全局教学反馈与改进项
  learning-state.md           记录位置
  handoff.md                  当前交接
  history/                    历史材料
```

归档脚本仅使用 Python 3.9+ 标准库，不调用模型 API。验证命令：

```bash
python3 -m unittest discover -s tests/save-trace -v
```

三个岗位的资料见 [岗位索引](tests/README.md)，当前优先 WorkBuddy。历史 OpenAI 学习记录用于复盘，原版技能见 [历史归档](docs/history/README.md)。
