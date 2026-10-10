# 岗位与项目说明

## 岗位依据

目标岗位以真实用户任务表现为反馈，改进 WorkBuddy Harness；要求研究、工程落地和评测能力。完整职责与要求见 [岗位 JD](../../岗位JD.md)。

## 学习清单与顺序

以下为教师建议，随用户表现调整：

2026-10-09 调整：先通过近期 Harness 实践进行难到易的诊断，再决定以下内容的讲解顺序与深度；执行循环入门已能口头解释，暂不重复讲解。

1. Agent 执行循环：模型输入与输出、工具调用、结果回传、下一轮决策和结束条件。
2. 模型与推理：Transformer、token、推理过程、Prefix Cache。
3. 上下文工程：信息组织、Context Compaction、任务约束与状态保留。
4. 工具工程：工具描述与参数、Programmatic Tool Calling、Skills、MCP。
5. 长期任务与协作：Agent Memory、Long-Horizon、Multi-Agent Coordination。
6. 评测与改进：任务验收、数据集、基线与对比、回归、Harness Self-Evolution。
7. 系统工程：Rust/Go/C++ 中一门静态语言、并发、性能、故障恢复，以及上述机制的工程实现。

## 第一课：工具调用与执行循环

教学设定：用户要求 Agent 读取销售 CSV 并生成报告。示意工具 `read_file` 由模型提出调用，Harness 调度实际工具执行，再把结果或错误送入下一次模型调用。示意调用与结果不是实际运行记录，也不是 WorkBuddy 内部实现。

真实工程背景：Anthropic 在 2026-04-08 发布的工程文章中说明，最初把 session、Harness 与 sandbox 放进同一容器，容器故障会导致会话丢失；随后将它们拆分为可独立恢复的组件。文章将 Harness 描述为调用模型并将工具调用路由至相关基础设施的循环。它是相邻团队的历史工程案例，用于解释机制，不作为腾讯内部架构依据。

- [Anthropic 工程文章](https://www.anthropic.com/engineering/managed-agents)，发布 2026-04-08，查阅 2026-10-09；实质更新日期未知。
- [Claude 工具调用官方文档](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)，查阅 2026-10-09；发布与实质更新日期未知。客户端工具由应用执行，并以 `tool_result` 回传模型。
- [WorkBuddy 创建任务文档](https://www.codebuddy.cn/docs/workbuddy/Create-Task)，查阅 2026-10-09；发布与实质更新日期未知，提供销售数据分析及报告等场景。

学习重点：工具实际执行与模型生成调用是两段过程；结果必须正确关联并进入后续输入，后续决策才能依据实际发生的事情调整。结束条件也需要结合任务成果检查。

岗位项目尚未选择，当前不设项目方案或验收成果。

## 当前诊断安排

根据用户指定，先给综合设计与验证题，再按表现检查异步执行、上下文与推理性能、工具与状态处理等机制。每次一题，不在作答前给标准答案。

近期资料（均查阅于 2026-10-09）：

- [STITCH 论文 v1](https://arxiv.org/html/2609.38912v1)，发布于 2026-09-30 UTC；提出从失败轨迹开发可复用机制，再由模型选择、确定性编译器组成任务适配 Harness。证据状态：研究方案与作者实验；不是腾讯生产实现，也未在本轮复现。
- [Codex PR #49075](https://github.com/openai/codex/pull/49075)，创建并合并于 2026-09-28 UTC（北京时间 2026-09-29），合并提交 `3749d1eff7df4ac9a0e2d32099813ba56500b930`；处理子 Agent 在环境尚未准备完成时丢失环境选择的问题。证据状态：已合并实现及作者列出的回归覆盖；本轮未运行代码。
- [Codex Issue #52555](https://github.com/openai/codex/issues/52555)，报告日期 2026-10-09；用户记录长会话高缓存比例下仍出现首 token 延迟。证据状态：用户测量报告，问题开放，原因未确认；标题与附件中的应用版本字段存在差异，不据此作统一版本归因。

第一道综合题依据 STITCH 的任务适配组合思路构造：固定模型与工具，开发集 100 个任务上的成功数从 62 提升到 78，平均 token 从 20k 增至 30k；组件开发和结果汇报使用同一批任务。机制包括上下文压缩、并行子 Agent、失败后重试。示例轨迹中，压缩丢失原始文件不得修改的约束，并行子 Agent 覆盖同一输出文件。所有题目数据和轨迹均为教学设定，不是论文实验或 WorkBuddy 实测。

作答任务：判断当前结果支持什么结论、决定是否上线；提出机制如何被选择和组合的具体设计；设计验证有效性与成本的实验。后续按回答降到单机制问题或继续追问，不把未回答方向判为不会。

## 2026-10-10：按诊断结果调整教学

用户已提出检查压缩任务中的约束遗漏比例、多 Agent 编排失败分布，但明确自报不懂具体实现和实验设计。当前顺序改为：上下文压缩的实现与任务规范保存 → 子任务依赖、独立产物和统一合并 → 单机制验证与完整任务实验 → 返回任务适配组件选择。

本轮教师提出的最小架构（教学方案，未实现或运行，也不作为腾讯内部实现）：

- 将已核对的任务目标、输入、约束和交付要求保存在独立的任务规范中；用户修改需求时更新其版本。每轮组织模型请求时加入当前任务规范、进度、压缩摘要和完整最近交互。
- 压缩替换较旧历史在活跃上下文中的表示，原始事件记录保留。保存任务规范和实际注入模型输入是不同步骤；文件只读等要求还要通过工具或执行环境落实。
- 主 Agent 分配有明确输入、输出和依赖的子任务；每个子 Agent 有自己的模型上下文，并把成果写入独立任务与尝试目录。合并程序或负责合并的 Agent 是最终报告的唯一写入者。文件锁只能串行化写入，不能自动合并语义内容。
- 验证先检查机制操作和实际效果，再检查任务成果。压缩回放采用同一历史输入；编排验证控制两名工作者的写入时序。完整任务用原压缩/改进压缩与原编排/改进编排四组，固定组件选择和重试机制，以区分两个改动及其交互。
- 开发任务与评测任务分开；模型、初始数据与环境固定，每次独立恢复状态，重复并交错运行。记录真实成果验收、约束违例、各机制触发情况、总 token、费用和耗时；保留逐任务的改善和退化。组件选择的价值需要另用固定组件库比较选择策略。
- 压缩任务的观察失败率会受任务长度和难度影响，不能直接作为压缩因果效果。题目中的 62→78 为开发集结果，总 token 20k→30k 增加 50%，尚不能推出未见任务表现或上线收益。

资料：2026-10-10 重读 [STITCH v1](https://arxiv.org/html/2609.38912v1) 的机制验证、组合契约与开发/评测任务划分；另读 [Anthropic 上下文工程文章](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)（发布 2025-09-29）和 [多 Agent 研究系统文章](https://www.anthropic.com/engineering/multi-agent-research-system)（发布 2025-06-13）。两篇旧文章用于历史实现机制，近期研究仍以 STITCH 为依据；文章的实质更新日期未知。本轮未复现作者系统或实验。

下一道机制问题采用有依赖的报告流程：A 计算统计表；B 根据 A 的表格生成图表；C 独立整理术语说明。请用户判断可立即并行的任务、B 的启动条件与最终报告的写入者。该流程为教学设定。

## 2026-10-10：业界实现与小 loop 接入

以下为上一版教学安排，用户已明确否定其碎片化组织；保留为历史记录，不作为当前课程结构。

用户请求深入实现机制，本轮教学采用以下映射。供应商 API 与开源项目事实来自下列一手资料，接口骨架和接入顺序为教师建议，未实现、运行或测量。

- 上下文管理：在工具结果进入活跃上下文前保存大结果并提供可检索引用；模型请求前计入指令、工具定义、历史和输出预留的预算。采用独立原始事件、当前任务规范、进度和活跃窗口，压缩在完整工具交互边界进行。后台压缩只替换快照覆盖的前缀，保留快照之后的尾部，并核对快照与当前状态的关系。
- 原生压缩适配：OpenAI Responses 支持 `context_management=[{"type":"compaction","compact_threshold":...}]` 和独立 `responses.compact`。独立接口返回完整的下一上下文窗口，包含不透明压缩项，不手动裁剪其返回窗口。Claude 新按需压缩使用 beta `compact-2026-09-04` 与 `compaction={"type":"summarize"}`，返回可读但带签名的块，按协议原样传回；不把各供应商压缩块强制转成统一摘要字符串。
- 子 Agent：保留父 Agent 控制权，子 Agent 运行独立会话，接收明确任务、规范版本、输入引用、能力与交付约定。同步工具可直接等待最终结果；后台任务须返回真实 task ID，另行支持查询、等待、更新与取消。任务注册表独立于聊天历史，父上下文压缩后仍能恢复运行中任务。初版使用隔离会话，必要时再加入显式 fork 模式。
- 产物与恢复：子任务/尝试使用独立目录，按实际权限约束写入范围；验收成果后由父 Agent 或确定性合并器写最终输出。并发槽位、递归深度和共享总预算由调度器控制。进程内 `asyncio` 任务不等于持久化执行，后续可用数据库记录、租约及恢复机制补齐。

均查阅于 2026-10-10；文档发布与实质更新日期未知，除另有注明：

- [OpenAI compaction](https://developers.openai.com/api/docs/guides/compaction) 与 [orchestration](https://developers.openai.com/api/docs/guides/agents/orchestration)。
- [Claude 按需压缩](https://platform.claude.com/docs/en/build-with-claude/compaction-on-demand) 与 [后台压缩](https://platform.claude.com/docs/en/build-with-claude/compaction-background)，当前接口为 beta。
- [Claude Agent SDK subagents](https://code.claude.com/docs/en/agent-sdk/subagents)，当前文档包含独立与 fork 上下文、后台运行以及嵌套、并发与费用限制。
- [Deep Agents 上下文工程文章](https://www.langchain.com/blog/context-management-for-deepagents)，发布于 2026-01-28；历史阈值用于说明分层机制，不当作所有当前版本的默认值。
- [Deep Agents summarization 源码](https://github.com/langchain-ai/deepagents/blob/2caefbcc8637982e9683b38ca77f95a2d9e85bc5/libs/deepagents/deepagents/middleware/summarization.py)，固定提交 `2caefbcc8637982e9683b38ca77f95a2d9e85bc5`，提交时间 2026-09-22 UTC。读取到模型调用前的参数缩减、历史卸载、摘要事件和输入预算检查，未运行代码。
- [Deep Agents subagents](https://docs.langchain.com/oss/python/deepagents/subagents) 与 [async subagents](https://docs.langchain.com/oss/python/deepagents/async-subagents)，后者将任务元数据保存于独立的 `async_tasks` 状态通道，避免对话压缩丢失子任务。

## 2026-10-10：依据 F004 重写

当前课程先逐个解释完整系统，再讲教师建议的渐进实现，不混同产品核心、供应商接口和扩展示例。实现部分重新从最小 loop 开始，每次改动说明新增状态、调用位置、模型下一次实际看到的输入及设计原因。

- Codex：固定提交 `806d9732c974bc8a51b8317c1bd8985544fe627c`（2026-10-10 UTC），读取 `session/turn.rs`、`compact_remote_v2*.rs`、`compact.rs`、`context_manager/history.rs` 与 `agent/control`、`multi_agents_v2`。区分原生 V2 压缩项、普通模型摘要回退和 feature flag 下跳过摘要的上下文重置分支；子 Agent 使用自己的会话、共享运行时注册表与邮箱，不以 OpenAI Agents SDK handoff 代替。
- Claude Code：读取产品文档 `how-claude-code-works`、`context-window`、`memory`、`hooks`、`troubleshooting`、`sub-agents`。说明公开确认的先清理旧工具输出、结构化摘要、重新注入规则/环境/运行中任务信息与独立子会话；闭源部分不虚构内部类和算法。
- Pi：当前官方仓库 `earendil-works/pi`，固定提交 `42a3497d03ad17e308a2299fa824727894f2c0ec`（2026-10-09 UTC）。主 coding-agent 的压缩记录保存摘要及 `firstKeptEntryId`，由 JSONL 会话树构造当前模型视图；官方 `examples/extensions/subagent` 通过独立 Pi 进程执行 single/parallel/chain，示例的 `--no-session` 不提供持久化子任务恢复。

均查阅于 2026-10-10；本课证据为当前文档与固定提交的静态源码阅读，未运行或测量这些系统。压缩与编排的教师代码仍为教学实现，不作为腾讯内部方案。
