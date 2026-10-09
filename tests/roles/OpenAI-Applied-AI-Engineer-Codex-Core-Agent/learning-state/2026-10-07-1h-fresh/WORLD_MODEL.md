# 本次工作模型与证据

查阅日期：2026-10-07。本次独立读取当前 skill、状态协议、本地 JD 与官方 JD；未读取旧聊天、记忆或旧课程状态。以下来源均为本次联网取得。

## 岗位事实

[官方 JD](https://openai.com/careers/applied-ai-engineer-codex-core-agent-san-francisco/)：Core Agent 团队负责核心执行、模型与工具接口、共享基础设施、使用反馈及 tokens、时延、可靠性、成本、容量。Applied AI Engineer 与研究、基础设施、产品协作；工作包含真实任务中的 agent 行为、评估与回归、提示/工具策略/上下文实验、生产失败、真实任务数据与端到端质量标准。

## 从业者工作资料

1. [Building Codex with Tibo Sottiaux](https://newsletter.pragmaticengineer.com/p/building-codex-with-tibo-sottiaux/)，发布 2026-09-09。受访者为 Codex 共同创建者，访谈时领导 OpenAI Core Products & Platform。公开访谈页面的工作描述：团队利用内部系统上下文帮助新人理解谁在做什么、决策缘由；harness 随模型进展调整；新模型成熟后会移除部分原有辅助机制。页面公开部分已读；不声称阅读不可见的完整访谈。
2. [Software Engineering Daily 访谈逐字稿](https://softwareengineeringdaily.com/wp-content/uploads/2026/01/SED1898-OpenAI.txt)，[节目页](https://softwareengineeringdaily.com/podcasts/openai-and-codex-with-thibault-sottiaux-and-ed-bayes/)，节目页发布日期 2026-01-29。人物为当时的 Codex 工程负责人 Thibault Sottiaux 与产品设计师 Ed Bayes。录制时间未明确，稿内谈及 GPT-5.2 刚发布，不能将谈话中的“昨天”推断为 2026-01-28。具体工作描述：约 24:07，产品、工程、研究共同讨论，将研究手段引入 harness，并将 harness 相关内容用于训练；约 07:03，设计师处理 sandbox 权限、命令批准与用户控制的体验；约 35:08，新工程师借 Codex 理解代码，向同事提出更高价值的问题。该来源用于工作方式和机制，不作为当前模型版本依据。
3. [Codex 团队官方 AMA](https://www.reddit.com/r/codex/comments/1us9ty9/ama_with_openais_codex_team/)，帖子明确标注活动 2026-07-10（网页相对年龄不完全一致，以正文活动日期记录）。身份清单：Janvi Kalra / Codex Research；Dominik Kundel / Developer Experience — Codex；Kath Koverec / Codex Product Manager。用户报告 Windows sandbox 命令反复受阻、替换命令并浪费时间与 tokens；Dominik 回复引导通过 /feedback 提供上下文。Kath 说明团队历史上日常开发测试偏 Mac，随后加强 Windows 测试反馈与平台体验。这是当时的用户报告和团队回复，不代表问题在今天仍普遍存在。

## 教学编排

以 Windows 开发者的编码任务在命令执行阶段受阻为统一场景，编排“入职后的一天”。用户请求示例、时序、具体调查分工及交付包是教学假设，不是内部工单或个人真实日程。先解释工作怎样到来、员工与研究/基础设施/产品分别讨论什么、结果交付关系；取得用户自己的岗位认识后，才展开失败轨迹、实验与评估机制。

用户自己的模型（2026-10-08）：处理 Codex 在用户真实任务中的失败并提高任务成功率；根据产品设计实现功能并评估当前模型/harness 下的质量；与研究合作整合新模型，测试其表现并调整 harness；可能按战略需求改善长程任务，如断点续跑、云端运行；harness 能力与模型、运行环境和基础设施紧密相关，最终希望改善用户体验。

教师反馈：用户已连接真实任务、模型、harness、基础设施和体验。补充岗位参与定义行为、接口和质量标准，不能将其限定为接收产品设计后实现；进一步需要从观察到的失败机制推导改动选择，并区分机制正确性与端到端任务结果。用户举出的战略与长程任务方案作为候选假设，不视为公司已采纳的决策。

## 后续候选近期变化

本次访问 [官方 changelog](https://learn.chatgpt.com/docs/changelog)，截至 2026-10-07，覆盖近 7 天与近 30 天可见记录。2026-10-01 Codex CLI 0.160.0 包含 Windows sandbox PowerShell fallback 与长路径权限修复；2026-10-05 0.160.1 包含远程 stdio MCP 启动时 Windows 环境变量保留修复。最新可见 CLI 版本为 0.160.1。第一阶段尚不展开这两个机制。

公开动作只能确认具体发布，不能将其推断为已量化改善任务解决率或内部战略动机。尚未读对应 PR/源码、未运行或测量；选择工程案例后需要读取具体实现。本次不以单个补丁推断公司整体当前战略，当前战略结论未建立。

## 第二阶段：运行环境状态与 agent 行为（2026-10-08）

沿用户对运行环境的理解，继续“任务在执行阶段受阻”的主题，选择一个具体的近期环境继承修复；不展开完整多 agent 架构。

- [官方 PR #49075](https://github.com/openai/codex/pull/49075)：2026-09-28 合并，Codex CLI 0.160.0 于 2026-10-01 收录。失败条件是环境仍准备中时创建子 agent，旧逻辑遗漏该环境选择。修复保存生成子 agent 时的环境快照，传播初始配置完成或失败，并保留等待关系。
- [提交 3749d1e](https://github.com/openai/codex/commit/3749d1e)：已读取 patch 中 environment_selection.rs 与 session/environment.rs。旧 from_snapshot 只复用 Ready；改后保留 Starting，等待原始配置结果。配置结果经 session 验证，只作用于仍 Pending 的继承选择，避免覆盖子会话独立配置。连接与配置均就绪后才能完成环境解析。
- [测试请求快照](https://raw.githubusercontent.com/openai/codex/3749d1e/codex-rs/core/tests/suite/snapshots/all__suite__scenarios__subagent_inherits_pending_environment.snap)：子 agent 看到 starting，调用 wait_for_environment，收到 ready 后获得环境配置。该快照展示测试场景中的模型输入/工具交互，不代表生产任务成功率测量。
- [官方 changelog](https://learn.chatgpt.com/docs/changelog)，2026-10-08 重新访问，近 7 天与近 30 天可见条目均已检查；最新可见 CLI 仍为 2026-10-05 的 0.160.1，最新总表条目 2026-10-07。这里只确认案例发布背景，不由补丁推断公司战略。

教学中的具体用户任务为示例。状态流转解释基于上述代码与测试快照；本次未执行 Codex、测试、模型评估或生产测量。

用户随后回答：认为修复无效，因为用户仍要求子 agent 在给定环境工作；提出父 agent 监控启动，成功后再 spawn。

反馈依据：父等待就绪是可规避原缺陷的替代同步设计。环境最终启动失败时，两种设计都不具备执行条件，不能用这一结果判定继承修复无效；上一题单独给出的失败分支也不足以验收整个修复。应检查环境最终成功的分支，在同模型、同任务与相同准备时序下验证子 agent 是否保留绑定并收到配置。

设计取舍作为教学推理：若子 agent 全部工作依赖已就绪环境，父先等待可简化时序；若准备期间可做有用工作，提前创建可能利用等待时间，但收益需要测量。不能将这项潜在收益说成 PR 已公开的选择动机或实际测量。

2026-10-09 用户追问：子 agent 自身是否是部署在云实例中的运行时，是否与准备中的工作环境不同；等待目标环境为何成为问题；“改善”是否指任务开始、完成和产物通过验收；这项 commit 为什么与岗位准备有关。

教学修订：用户识别了两个环境概念，任务验收标准也成立。前面的解释没有先区分会话与目标执行环境，且将一个较窄的环境继承修复展开为多轮验收题，偏离一小时岗位准备的重点。先补足架构和工作价值连接，再收束该 commit；不将用户的合理质疑记录为单纯不理解局部与整体。

## 会话与执行环境的澄清（2026-10-09）

本次重新访问官方文档（OpenAI Docs）：

- [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)：子 agent 是受委托处理任务的 agent，其工作在 agent thread 中；Codex 维护创建、消息、等待和结果汇总。子 agent 有自己的模型与工具工作；这不意味着每个子 agent 必须有一台专属云实例。
- [Codex App Server](https://learn.chatgpt.com/docs/app-server)：thread、turn、item 是不同对象；创建会话与执行命令是不同接口，执行环境有独立连接与检查接口。用于解释会话生命周期与工具环境的区分，不将 app-server 内每个 thread 宣称为独立进程。
- [Codex CLI](https://learn.chatgpt.com/docs/cli)：CLI 可读写本地仓库并运行本机工具，也可提交到云端配置的环境。用于说明工具执行位置并不由“子 agent”这个名称决定。

教学模型：模型推理所需计算、维护会话与动作循环的 harness、执行文件/命令操作的工作环境是三层关系。第 1 秒建立子会话，第 5 秒目标环境连接与配置就绪，没有逻辑矛盾。环境准备不必等于新虚拟机启动。

“改善”范围澄清：该补丁直接检查环境绑定与状态传递；用户提出的开始/结束/产物验收是完整任务标准。判断补丁效果需要其直接机制的证据；判断岗位价值还要连接完整任务的质量、时间与成本。

案例重要性：对环境生命周期实现的维护者有具体价值；公开证据没有给出该补丁的生产影响规模，也不能据此认定为岗位面试重点。它可用于说明模型能力依赖系统提供执行条件；一小时准备不宜继续深挖该局部补丁。

下一步收束这个案例，回到真实编码任务的 agent 行为、轨迹和评估。当前不要求用户继续回答原先的差异验收题。

## 编码任务的验收选择与 agent 评估（2026-10-09）

承接用户的“任务开始、结束、产物通过验收”标准，转向环境正常但修复未达到用户目标的情况。

- [官方 Prompting 文档：Fix a bug](https://learn.chatgpt.com/docs/prompting)：本次经 OpenAI Docs 读取正文。公开教学示例为设置页点击 Save 显示 Saved，但刷新后设置重置；提供复现步骤、API 不变约束，并要求修复后重跑复现及最小相关检查。页面无明确发布日期，查阅日期 2026-10-09；只用于稳定工作机制，不作为近期战略证据。
- [Testing Agent Skills Systematically with Evals](https://developers.openai.com/blog/eval-skills)：发布 2026-01-22，作者 Dominik Kundel、Gabriel Chua，本次重新联网读取正文。描述以任务输入、执行轨迹和产物、可比较检查来评估 agent skill；区分结果、过程、风格与效率目标，从真实失败扩展小评估集。这是公开的工程方法，不是 Core Agent 内部流程或最新战略的证明。

教学编排：假设用户提供了完整刷新复现，agent 读取前端与保存接口、调整请求参数、运行以模拟 API 为基础的组件测试，但没有重跑刷新步骤；交付后独立检查仍复现失败。该执行轨迹为教师假设，不声称是实际生产工单、已运行的 Codex 轨迹或官方事故。

工作连接：应用回归测试检查给定补丁是否正确；agent 评估从故障仓库和原始任务开始，让 agent 自行产生补丁，再独立验收产物。轨迹可以定位遗漏复现与验收选择，但具体根因及干预收益仍待验证。候选改动涉及提示、工具和上下文；在多项任务上比较结果、耗时与 tokens 后判断是否值得采用。
