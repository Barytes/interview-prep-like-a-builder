# 归档说明

## 找到本次会话

使用当前 Codex 会话 ID，在 `$CODEX_HOME/sessions/` 或默认 `~/.codex/sessions/` 查找对应 rollout JSONL；已归档日志也可能位于 `archived_sessions/`。以文件内 `session_meta.id` 核对，使用准确路径。岗位不明确时向用户确认，日志不可取得时说明缺失，不用回忆重写对话。

本仓库的岗位目录为 `tests/roles/<岗位>/`。该目录需已存在。技能仓库是含 `skills/`、`AGENTS.md`、`CONTEXT.md` 的根目录。

```bash
python3 skills/save-trace/scripts/save_trace.py   --source /absolute/path/to/rollout.jsonl   --session-id <完整会话ID>   --repo /absolute/path/to/skill-repo   --role-dir /absolute/path/to/tests/roles/岗位   --task '本次在学什么或做什么'
```

可追加 `--skill-used teach-me` 等已知技能，以及 `--learning-dir /absolute/path`。这些是调用者提供的信息，不用于推定每个回合实际加载了什么。

## 生成文件

一次测试会话对应 `runs/<上海日期>-<完整会话ID>/`，重复调用更新相同目录：

| 文件 | 内容 |
| --- | --- |
| `run.md` | 运行信息的阅读视图、任务与归档范围 |
| `run.json` | 会话 ID、逐轮模型与配置、harness、历次归档和技能版本信息 |
| `trace.jsonl` | 按源日志顺序导出的会话事件，含稳定事件 ID 与源行号 |
| `conversation.md` | 用户和助手文本的阅读视图，标题锚点对应事件 ID |
| `skill-snapshot/<内容哈希>/` | 各次归档时的技能及共同约定快照，相同内容复用 |

生成文件由脚本维护，人工教学反馈保存在全局反馈文件，通过 `conversation.md#事件ID` 或 trace 事件 ID 引用。本技能不修改反馈文件。

## 版本与覆盖范围

Git commit、文件是否有未提交修改和内容快照均标明“归档时”。会话开始时日志记录的 Git 信息另存；早期实际加载的技能版本未知时保留未知。多次归档保留各次版本，技能快照覆盖技能仓库的 `skills/`、`AGENTS.md` 和 `CONTEXT.md`。

模型与配置按回合保存；`cli_version` 按源字段含义记录，不当作桌面应用版本。脚本不需要网络或模型 API。

导出范围是用户与助手可见文本、工具调用及结果、会话与逐轮运行信息。系统及开发者消息、内部推理、压缩摘要不导出，非文本媒体保留占位。它是源日志的选定事件导出，不宣称涵盖未落盘或无法取得的内容。

每次只读取调用时已经落盘的日志。尚未写完整的最后一行留待下次；旧日志被修改或截断时停止更新并保留已有归档。修改日志格式后先检查解析结果，未知事件类型会在运行信息中列出。
