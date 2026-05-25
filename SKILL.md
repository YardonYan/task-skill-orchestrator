---
name: task-skill-orchestrator
author: Yardon (https://github.com/YardonYan)
description: |
  Decompose complex user requests into a dependency-aware DAG of subtasks,
  dispatch them in parallel waves to multiple Sub Agents, and aggregate results.
  Use when the user asks to handle multiple things at once, split a large task,
  or when a request naturally breaks into independent sub-goals with dependencies.
  将复杂用户需求拆解为有依赖关系的子任务 DAG，分波次并行派发给多个 Sub Agent 执行，最后汇总结果。
  触发词：并行处理、同时做、拆任务、多线并进、批量执行、复杂任务拆解、一起做、同时处理、分头行动、并行执行、多任务、编排、编排任务、拆解任务。
license: Apache-2.0
created: 2026-05-25
updated: 2026-05-25
version: '1.0.0'
based-on:
  - name: parallel-task
    author: am-will
    url: https://github.com/am-will/codex-skills
    description: Pioneered wave-based parallel task orchestration with dependency management
tags:
  - parallel
  - dag
  - orchestration
  - task-scheduling
  - multi-agent
---

# Task Orchestrator v1.0.0

> **Stop doing one thing at a time. Decompose, parallelize, orchestrate.**
> **不要一次只做一件事。拆解、并行、编排。**

## Platform Requirements / 平台要求

This skill is designed for **OpenClaw** and uses `sessions_spawn` for sub-agent dispatching. It requires the following Sub Agents to be available:

本技能专为 **OpenClaw** 设计，使用 `sessions_spawn` 进行子 Agent 派发。需要以下 Sub Agent 可用：

| Sub Agent | Role / 角色 |
|-----------|-------------|
| `file-agent` | File search, read, process, generate, convert / 文件操作 |
| `search-agent` | Deep search, research, data gathering / 深度搜索调研 |
| `browser` | Web browsing, form filling, login / 网页交互 |
| `app-agent` | App download, install, operate / 应用操作 |
| `computer-agent` | System settings, config, info query / 系统操作 |

> **Note**: This skill can be adapted for other platforms (Claude Code, etc.) by replacing `sessions_spawn` with the platform's equivalent parallel dispatch mechanism. See `scripts/orchestrate.py` for a platform-agnostic DAG engine.
> **注意**：本技能可适配其他平台（Claude Code 等），只需将 `sessions_spawn` 替换为对应平台的并行派发机制。平台无关的 DAG 引擎见 `scripts/orchestrate.py`。

## Overview / 概述

This skill guides the decomposition of complex user requests into a dependency-aware Directed Acyclic Graph (DAG) of atomic subtasks. It then plans execution waves using topological sorting, dispatches independent subtasks in parallel within each wave, and aggregates results into a unified deliverable.

本技能指导将复杂用户需求拆解为有依赖关系的有向无环图（DAG），通过拓扑排序规划执行波次，每波内并行派发独立子任务，最后汇总为统一交付成果。

**Acknowledgement / 致谢**: This skill is adapted from [parallel-task by am-will](https://github.com/am-will/codex-skills) (1.2K+ installs on skills.sh), which pioneered wave-based parallel task orchestration with dependency management. The four-phase pipeline, DAG-based decomposition, and wave planning methodology are derived from parallel-task, extended with multi-agent routing, result aggregation, and platform-specific dispatch integration. Sincere thanks to am-will for open-sourcing this foundational work.

本技能改编自 [am-will 的 parallel-task](https://github.com/am-will/codex-skills)（skills.sh 上 1.2K+ 安装），它开创了基于波次的并行任务编排与依赖管理方法。四阶段流水线、基于 DAG 的拆解和波次规划方法论源自 parallel-task，并扩展了多 Agent 路由、结果汇总和平台特定派发集成。衷心感谢 am-will 开源这一基础性工作。

## When to Use This Skill / 适用场景

| Scenario / 场景 | Example / 示例 |
|------|------|
| Multi-source information gathering / 多方信息汇聚 | 「调研 A、B、C 三家公司的市场数据，最后汇总对比」 |
| Parallel file processing / 多文件并行处理 | 「把这三个文件夹里的 PDF 都转成 Word」 |
| Multi-domain compound tasks / 多领域复合任务 | 「帮我整理桌面文件 + 清理系统垃圾 + 备份重要文档」 |
| Large task decomposition / 大任务拆分 | 「写一篇关于 AI Agent 的全景技术文章」 |
| Batch independent operations / 批量独立操作 | 「把这 10 张图片全部压缩并重命名」 |

## Core Workflow / 核心流程

### Phase 1: Analyze & Decompose / 阶段一：分析拆解

1. **Understand the request / 理解需求**: Parse the user's original request. Identify the final deliverable.

2. **Atomic decomposition / 原子拆分**: Break the request into atomic subtasks. Each subtask must satisfy:
   - **Single responsibility / 单一职责**: One subtask does exactly one thing.
   - **Self-contained / 可独立执行**: The task description is complete; no external context needed to begin.
   - **Verifiable output / 有明确产出**: Each subtask produces a checkable artifact.

3. **Classify subtasks / 子任务分类**:
   - **Independent / 独立任务**: Requires no output from other subtasks. Can execute immediately.
   - **Dependent / 依赖任务**: Requires another subtask's output as input.

4. **Granularity rule / 粒度原则**:
   - One subtask maps to one Sub Agent (file-agent / browser / search-agent / app-agent / computer-agent).
   - If a subtask spans two different agent domains, split it further.
   - Optimal range: 3–7 subtasks. More than that increases coordination overhead.

### Phase 2: Build the DAG / 阶段二：构建依赖图

1. **Identify dependencies / 识别依赖关系**: For each pair of subtasks (A, B), determine if a dependency exists:
   - **Data dependency / 数据依赖**: B needs A's output file or data.
   - **Temporal dependency / 时序依赖**: B must run after A (e.g., "download then install").
   - **Logical dependency / 逻辑依赖**: B's decisions depend on A's results.

2. **Construct the DAG / 构建 DAG**: Build a directed acyclic graph using task IDs as nodes and dependency edges.

3. **Validate the DAG / 验证 DAG**:
   - No cycles. If a cycle is found, the decomposition is wrong — re-decompose.
   - Every node is reachable. No orphan nodes.
   - At least one entry node (in-degree = 0) and one exit node (out-degree = 0).

### Phase 3: Wave Planning & Parallel Dispatch / 阶段三：波次规划与并行派发

1. **Topological layering (Wave planning) / 拓扑分层**:
   - Wave 0: All nodes with in-degree 0 (no dependencies — can run in parallel immediately).
   - Wave N: After removing nodes from waves 0 through N-1, the new nodes with in-degree 0.
   - All subtasks within the same wave MUST be dispatched in parallel in a single assistant message.

2. **Parallel dispatch rules / 并行派发规则**:
   - All `sessions_spawn` calls for the same wave must be issued in ONE assistant message for true parallelism.
   - Waves execute strictly sequentially: wait for ALL tasks in the current wave to complete before dispatching the next wave.
   - Maximum 5 parallel `sessions_spawn` calls per wave (OpenClaw framework constraint).

3. **Present the execution plan / 展示执行计划**: Always show the user the plan before executing.

   ```
   Decomposition complete. N subtasks, M waves.

   Wave 0 (parallel): [Task 1] [Task 2] ...
   Wave 1 (parallel, depends on Wave 0): [Task 3] ...
   Wave 2 (aggregation): [Final merge task]

   Dependencies: [Task 3] depends on [Task 1] + [Task 2]
   Proceed with execution?
   ```

### Phase 4: Verify & Aggregate / 阶段四：验收与汇总

1. **Per-wave verification / 逐波验收**: After each wave completes, verify:
   - Every subtask has a real result or a clear failure reason.
   - Subtasks that require file artifacts have valid file paths.

2. **Failure handling / 失败处理**:
   - Single task failure: If the failed task is not a dependency for later tasks, skip it and continue. If it IS a dependency, pause and report to the user.
   - Each failed task may be retried once (adjust parameters or agent strategy).

3. **Result aggregation / 结果汇总**:
   - Collect all subtask outputs.
   - Merge into the final deliverable according to the user's original request.
   - If file artifacts are involved, declare them with the appropriate output format.

## Agent Matching Guide / Sub Agent 匹配指南

| Subtask Type / 子任务类型 | OpenClaw Agent / API |
|-----------|---------|
| File search/read/process/generate/convert / 文件操作 | `sessions_spawn(agentId="file-agent", ...)` |
| Web browsing/form filling/login / 网页交互 | `sessions_spawn(agentId="browser", ...)` |
| Deep search/research/data gathering / 深度搜索调研 | `sessions_spawn(agentId="search-agent", ...)` |
| App/software download/install/operate / 应用操作 | `sessions_spawn(agentId="app-agent", ...)` |
| System settings/config/info query / 系统操作 | `sessions_spawn(agentId="computer-agent", ...)` |
| Simple facts (weather/stock/etc.) / 简单事实查询 | Use `web_search` tool directly |

## Critical Constraints / 关键约束

1. **Self-contained task descriptions / 派发任务必须自包含**: Each subtask's description must contain ALL context needed. Never use phrases like "refer to Wave 0 results." If a preceding task's output (file path, data) is needed, explicitly include it.

2. **Intermediate artifact passing / 中间产物传递**: If Task A produces an output that Task B consumes, explicitly include A's output paths/data in B's task description.

3. **Result-oriented / 结果导向**: Task descriptions should state the final goal, not prescribe step-by-step instructions to the Sub Agent.

4. **Don't over-decompose / 不要过度拆分**: If a single Sub Agent can handle multiple related sub-goals, merge them into one dispatch. Don't fragment into unnecessary micro-tasks.

## Example / 示例

**User request**:
「帮我调研特斯拉、比亚迪、蔚来三家公司的 2025 年市场份额、核心技术和最新财报，最后汇总成对比报告」

**Phase 1 — Decomposition**:
- T1: Research Tesla 2025 market share, core tech, financials → `search-agent`
- T2: Research BYD 2025 market share, core tech, financials → `search-agent`
- T3: Research NIO 2025 market share, core tech, financials → `search-agent`
- T4: Aggregate three research results into comparison report → `file-agent`

**Phase 2 — DAG**:
```
T1 ──┐
T2 ──┼──→ T4
T3 ──┘
```
T1/T2/T3 are mutually independent (Wave 0). T4 depends on all three (Wave 1).

**Phase 3 — Execution Plan**:
```
Decomposition complete. 4 subtasks, 2 waves.

Wave 0 (parallel, 3 tasks):
  ① Research Tesla 2025 market share, core tech, financials
  ② Research BYD 2025 market share, core tech, financials
  ③ Research NIO 2025 market share, core tech, financials

Wave 1 (aggregation, depends on all Wave 0):
  ④ Merge three research results into comparison report

Proceed with execution?
```

**Phase 4 — Execution**:
- Round 1: Dispatch T1/T2/T3 in parallel to 3 search-agents.
- Wait for all three to return.
- Pass T1/T2/T3 result summaries as context. Dispatch T4 to file-agent.
- Output the final comparison report.