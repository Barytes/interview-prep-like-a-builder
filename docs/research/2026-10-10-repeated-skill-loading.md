# 同一会话反复加载 Skill：研究与工程证据

调研日期：2026-10-10（Asia/Shanghai）。检索与实际打开的一手资料截至此日。本文是文献与实现文档核查，没有运行本仓库的教学对照实验，没有更新学习记录或归档会话。

## 判断

**同一会话可以反复执行某个 Skill 规定的流程；“每次都重新把相同 SKILL.md 全文追加到上下文”不应作为默认的性能增强手段。** 较合理的默认是首次加载、继续复用、在确有缺失或内容变化时补读，并在关键步骤重申当前相关的少量要求。这是根据下列机制与证据形成的工程判断，不是已经证明适用于所有模型的定律。

截至本次检索，没有找到对“长程 Agent 会话中，同一份未变化的 SKILL.md 已在当前历史中，再追加 N 份完整副本”进行充分隔离、跨模型验证的直接实验。已经有更接近问题的 Skill 加载研究，也有单次 Prompt 重复的正结果和小样本 Agent 指令重复的未检出结果。它们需要分别解读。

## 先区分四件事

| 行为 | 上下文发生什么 | 对问题的含义 |
| --- | --- | --- |
| 沿用已读 Skill 执行下一轮教学/检查 | 可以继续使用当前上下文已有的指令 | 同一个流程可以执行多次，不要求重新读取文件 |
| 重新读取相同 SKILL.md | 如果工具结果原样进入历史，会新增一份文本 | 是否去重、裁剪、保留取决于 Harness；不能仅由 UI 调用次数确定 |
| 压缩、清除工具结果或开启新上下文后补载 | 恢复当前上下文缺失的指令 | 这是恢复信息，不等同于在完整历史中堆积副本 |
| 执行 Skill 内的脚本，或用独立 Agent 执行有输入输出契约的流程 | 执行程序或在另一个上下文完成子任务 | 更接近用户所说的函数抽象；读取 Skill 正文本身没有执行完其流程 |

OpenAI 的 Skills 文档描述：先提供 name、description、path，模型决定使用后读取完整 Markdown；Anthropic 的设计也明确区分元数据、正文、按需参考文件与可执行脚本。这支持把普通文件式 Skill 理解为按需加载的操作说明。[OpenAI Skills](https://developers.openai.com/api/docs/guides/tools-skills)、[Anthropic Agent Skills，2025-10-16](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)。

**只读取一次，并不等于后续推理看不到 Skill。** 如果 Harness 继续携带此前历史，原先那一份正文仍属于后续每次有效模型输入；重新执行 `cat` 并将输出追加进历史，一般是新增另一份正文。跨请求沿用同一份内容，与在一份历史中追加多个副本，需要分开衡量。压缩或工具结果清除会改变这一前提。

## 最相关的实验证据

### 1. Skill Blocks：研究何时加载 Skill 的不同部分

**来源与日期**：[Skill Blocks: How Should an Agent Load Its Skill?](https://arxiv.org/html/2608.14943v1)，Hironobu Nakasuji，arXiv v1，2026-08-14。这是预印本。

**实验**：相同可用内容的 Full、Skill Block、Reference、Hybrid 四种包装，覆盖 SearchQA、SpreadsheetBench、ALFWorld、ScienceWorld 和合成 SynthProc。Full 每次请求提供全文；其他方案保留核心并按需取得细节。主实验是 GitHub Copilot 端点，配置记作 GPT-5.5；部分历史日志没有服务方确认的模型标识。

**结果**：ScienceWorld 主集 n=84，约 6K-token、16 项流程的 Skill 通常每 episode 只需一项；Skill Block 和 Hybrid 的缓存折算输入分别减少 62.5% 和 52.8%。短且持续需要的 ALFWorld Skill（约 1K，n=42）节省较小；计入输出成本后更接近持平。SearchQA 中强制倾向加载的 Skill Block 反而增加输入 48.4%。

**边界**：质量配对检验未检出差异，不是证明等效或无退化。缓存折算按 cache read 的 0.1 倍计算，不是通用账单；部分测试集被反复用于开发，推断是探索性的。它比较完整常驻与条件加载，**没有比较会话历史中一份全文与多份相同全文副本**，也未测量墙钟延迟。它支持根据相关内容比例和加载开销选择策略，不能支持“多读几次增强能力”。

### 2. Google Research：重复整个单次 Prompt 确实可能提升准确率

**来源与日期**：[Prompt Repetition Improves Non-Reasoning LLMs](https://arxiv.org/html/2512.14982v1)，Leviathan、Kalman、Matias，2025-12-17；实验实际在 2025 年 2—3 月通过官方 API 运行。这是预印本。

**实验**：把一次输入从 `<QUERY>` 变成 `<QUERY><QUERY>`；7 个模型为 Gemini 2.0 Flash/Lite、GPT-4o/mini、Claude 3 Haiku/3.7 Sonnet、DeepSeek V3。任务含 ARC、OpenBookQA、GSM8K、MMLU-Pro、MATH 和两个位置检索任务。

**结果**：要求不推理时，70 个模型与任务组合中 47 个显著获胜、0 个显著退步，显著门槛为 McNemar p<0.1。鼓励 step-by-step 的较小子集是 5 胜、1 负、22 平。输出长度基本不变；很长的 Claude 输入出现延迟增加。

**边界**：这是把完整题目紧接重复的单次推理研究；不包含多轮工具 Agent、Skill 重读、现代推理模型的长会话。它反驳“重复一定有害”，不能证明“重复 Skill 一定有帮助”。论文所讨论的 causal-mask 解释不构成长程 Agent 重读收益的因果证据。

### 3. Clouâtre：Agent 指令重复的小样本尝试没有检出收益

**一手来源**：[作者博客](https://clouatre.ca/posts/prompt-repetition-agent-evaluation/)（2026-02-23，页面更新为 2026-10-04）、[实验仓库](https://github.com/clouatre-labs/prompt-repetition-experiments)、[Zenodo v1.0.9 数据页](https://zenodo.org/records/20768092)（2026-06-19）。Zenodo 所指预印本页面本次无法通过浏览工具打开，因此不把其全文列为已核验。

**实验**：Claude Haiku 4.5、temperature 0.5、extended thinking 关闭，在 Goose 的工程任务 Agent 中比较一次指令与原文重复两次。每个实验每组约 5 次运行；不是在同一聊天中反复调用文件读取。

**结果与版本边界**：博客主体仍写 20 次运行、两个实验，受接近/达到满分的评分上限影响；仓库与数据页记 30 次运行、三个实验，第三项 Kotlin 任务还存在评分要求与 runner 提示不匹配。都报告未检出任务成功率提升。并发限制导致批次不平衡，延迟比较受到混杂；仓库还提示 token 变化方向随实验反转。

**可用结论**：这是直接尝试把 Prompt 重复推广到 Agent 的一手小样本资料，但样本、评分与基础设施问题使它不足以证明无效、等效、性能提高或成本提高。博客对机制和任务类别的强推断不在本文采用的结论范围内。

## 一手工程建议与实现行为

### 4. Manus：有意重述当前目标，更新的是 todo

[Context Engineering for AI Agents: Lessons from Building Manus](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)，Yichao Ji，2025-07-18。作者称复杂任务平均约 50 次工具调用，Manus 更新 todo.md，把当前目标与计划重新放到上下文末尾，以减少偏离。这是生产团队的机制与经验说明，没有在文章中公开这一策略的隔离对照指标。

这里重复的对象是**动态变化的目标、已完成事项和下一步**，不是一份 Skill 的全部通用说明。本文据此推断：在教学关键步骤重申“依据本次回答调整难度、一次一个问题”等相关要求，比每轮重读所有入口、共同协议、参考文档更值得优先测试。

### 5. Anthropic：只加入需要的内容；compact 后会有恢复策略

[Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) 是持续更新的官方文档，未标发布日期；本次核验于 2026-10-10。它明确说已加载 Skill 的每个 token 都与历史和当前请求竞争，建议只加入模型尚无的信息，并按需读取参考资料。这是作者建议，不是重复加载实验。

[Claude Code context window](https://code.claude.com/docs/en/context-window) 当前官方实现说明（正文提及 v2.1.198）称：compact 总结会话后，已调用的 Skill 正文会重新注入；每项上限 5,000 tokens，总上限 25,000 tokens，超预算先去除旧 Skill，长 Skill 保留开头。读取/编辑文件最多重新读取 5 个，超过 5,000 tokens 的文件可能只保留路径。

因此，压缩后补载内容是合理恢复机制，但这些具体上限是 Claude Code 行为，不能当作 Codex 的已核验实现。看见三次读取事件，也不能只凭事件数量断言在同一未压缩窗口保留三份全文。

## OpenAI 的对应口径

- [Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)，2026-09-11：读取 Skill 会占用上下文、更接近 compaction，并可能加入当前不适用的指导。多流程 Skill 应以最小 root 路由到支持文件/脚本；旧模型所需的过度 recipe 在新模型上可能妨碍表现。是模型特定工程建议，没有重复加载 ablation。
- [Skills guide](https://developers.openai.com/api/docs/guides/tools-skills)，持续更新文档：对 Responses API shell，提供 name/description/path 后模型读取正文；此机制支持“说明进入上下文”的解释，不能推广成每个产品相同的保留、去重与压缩行为。
- [Prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching)，持续更新文档：复用的是相同前缀的 KV 状态。**缓存降低相同前缀的重复计算，并不意味着在后面重新追加的相同文本会自动去重或不占上下文。** 后半句是由其前缀机制得到的推断，不是本仓库实测。
- [Testing Agent Skills Systematically with Evals](https://developers.openai.com/blog/eval-skills)，2026-01-22：区分 outcome、process、style、efficiency；调用 Skill 属于过程指标，是否完成任务与 token 开销需要独立验收。

## 本仓库可采用的默认与待验证项

本仓库 [AGENTS.md](../../AGENTS.md) 已明确约定：“已读取且未变化的内容直接复用。”这个默认与上述按需披露的方向一致。本文未修改它或任何 Skill。

建议按三种情况处理：

1. 当前上下文中已经有未变化的 Skill：继续执行相应流程，关键时刻重申当前相关的少量规则。
2. 已压缩/清除、关键指令无法确认，或 Skill 文件已变化：补读缺失的部分；如原始正文确实丢失，可以重读全文。
3. 当前任务需要新分支或新参考资料：只读取新资料；可确定执行的重复操作优先交给已有脚本。

这些是待任务验证的默认，不能用 Skill 调用次数评价教学效果。若要验证本仓库，应固定模型、任务、材料、推理设置和上下文状态，比较“一次加载并复用”“每阶段重读全文”“只补充当前规则”“压缩后恢复”四种策略。先验收用户是否能解释/迁移知识、教学是否依据学习表现调整，再比较读取次数、输入/输出 token、延迟和压缩次数；不要把“执行了读取”当成教学成功。

所有网页与论文结果只代表本次读到的版本；本文没有声称完成全部相关文献的系统综述。
