<div align="center">

<img src="assets/dag-waves.png" alt="task-skill-orchestrator — 拆解、并行、编排" width="100%">

**不要一次只做一件事。拆解、并行、编排。**

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](CHANGELOG.md)
[![Stars](https://img.shields.io/github/stars/YardonYan/task-skill-orchestrator?style=social)](https://github.com/YardonYan/task-skill-orchestrator)
[![平台](https://img.shields.io/badge/平台-OpenClaw%20·%20Claude%20Code%20·%20Cursor-orange.svg)](#平台)
[![依赖](https://img.shields.io/badge/依赖-仅标准库-brightgreen.svg)](#文件结构)

**中文** · [English](README.en.md)

</div>

---

> 把一个复杂需求拆成有依赖关系的子任务 DAG，按波次并行派发给多个 Sub Agent 执行，最后汇总成统一交付物。

Stop doing one thing at a time. Decompose, parallelize, orchestrate.

## 目录

- [解决什么问题](#解决什么问题)
- [工作方式](#工作方式)
- [核心能力](#核心能力)
- [平台](#平台)
- [安装](#安装)
- [怎么调用](#怎么调用)
- [使用示例](#使用示例)
- [文件结构](#文件结构)
- [运行示例](#运行示例)
- [许可证](#许可证)

---

<a id="解决什么问题"></a>

## 解决什么问题

当 AI 面对一个复杂需求时——比如「调研三家公司并汇总成报告」，或者「整理桌面、清理系统垃圾、再备份重要文件」——默认做法是串行：先做 A，再做 B，再做 C。中间还夹着一次又一次的等待。

真正的瓶颈不是单个任务慢，而是它们本来互不依赖，却被排成了一条队。

**Task Orchestrator 改变这一点。** 它分析需求、拆成原子子任务、识别彼此依赖、构建有向无环图（DAG），再把互不依赖的子任务按波次并行派发。结果是更短的执行时间、更清晰的结构，以及每一步都可验证的中间产出。

<a id="工作方式"></a>

## 工作方式

<img src="assets/pipeline.png" alt="四阶段流水线：分析拆解 → 构建依赖图 → 波次规划 → 执行与汇总" width="100%">

整个链路分四步：

一、**分析拆解**。把用户需求切成粒度合理的原子子任务，并区分哪些独立、哪些有依赖。

二、**构建依赖图**。识别数据依赖、时序依赖和逻辑依赖，构造成 DAG，并验证图中没有环。

三、**波次规划**。对 DAG 做拓扑分层，同一层的任务互相独立，构成一个波次；生成执行计划交用户确认。

四、**执行与汇总**。每个波次内的任务同时派发给多个 Sub Agent，全部返回后验收，再进入下一波，最后合并为统一交付物。

```mermaid
graph TD
    A[👤 用户需求] --> B[🔍 阶段一：分析拆解]
    B --> C[🧩 阶段二：构建依赖图]
    C --> D[🌊 阶段三：波次规划]
    D --> E[⚡ 阶段四：执行与汇总]
    E --> F[📦 最终交付]

    subgraph W0["Wave 0（并行）"]
        T1[任务 1]
        T2[任务 2]
        T3[任务 3]
    end

    subgraph W1["Wave 1（汇总）"]
        T4[任务 4]
    end

    T1 --> T4
    T2 --> T4
    T3 --> T4
```

一句话概括机制：**同一波次内可以并行，跨波次必须等待**。

<a id="核心能力"></a>

## 核心能力

- **自动拆解**：解析复杂需求并切分为原子子任务，不需要人工规划。
- **依赖感知 DAG**：识别子任务间的数据、时序与逻辑依赖，构建并验证有向无环图。
- **波次并行派发**：把互相独立的子任务分到同一波，由多个 Sub Agent 同时执行。
- **结果汇总**：收集全部子任务产出，优雅处理失败分支，合并为统一交付物。
- **多 Agent 路由**：按任务类型自动路由到对应的 Sub Agent（file-agent、search-agent、browser、app-agent、computer-agent）。

<a id="平台"></a>

## 平台

**主要平台**：OpenClaw（通过 `sessions_spawn` 派发子 Agent）。

可适配 Claude Code 或其他具备子 Agent 能力的平台。平台无关的 DAG 引擎见 `scripts/orchestrate.py`。

<a id="安装"></a>

## 安装

OpenClaw 环境：

```bash
# macOS / Linux
cp -r task-skill-orchestrator ~/.qclaw/skills/
```

```powershell
# Windows (PowerShell)
Copy-Item -Recurse task-skill-orchestrator $env:USERPROFILE\.qclaw\skills\
```

或通过 SkillHub：

```bash
openclaw skill install task-skill-orchestrator
```

<a id="怎么调用"></a>

## 怎么调用

在对话中使用以下任一表达即可触发：

| 中文 | English |
|------|---------|
| 并行处理 | handle these in parallel |
| 同时做这些 | do all of these at once |
| 拆任务 | split this task |
| 多线并进 | multi-thread this |
| 批量执行 | batch execute |
| 复杂任务拆解 | decompose this complex task |

<a id="使用示例"></a>

## 使用示例

例一，有依赖的场景：

```
用户：帮我调研特斯拉、比亚迪、蔚来三家公司的 2025 年市场份额、核心技术和最新财报，最后汇总成对比报告

Agent：
拆解完成。4 个子任务，2 个波次。

Wave 0（并行，3 个任务）：
  ① 调研特斯拉 2025 市场份额、核心技术、财报 → search-agent
  ② 调研比亚迪 2025 市场份额、核心技术、财报 → search-agent
  ③ 调研蔚来   2025 市场份额、核心技术、财报 → search-agent

Wave 1（汇总，依赖 Wave 0 全部完成）：
  ④ 合并三份调研结果，产出对比报告 → file-agent

是否开始执行？

用户：执行

[Agent 并行派发 ①②③，等待全部返回，再派发 ④]
[产出：car_companies_comparison_report.md]
```

例二，完全独立的场景：

```
用户：同时帮我做三件事：整理桌面文件、清理系统垃圾、备份 D 盘重要文件到 E 盘

Agent：
拆解完成。3 个子任务，1 个波次。
（三者互相独立，无依赖关系。）

Wave 0（并行，3 个任务）：
  ① 整理桌面文件 → file-agent
  ② 清理系统垃圾 → computer-agent
  ③ 备份 D 盘重要文件到 E 盘 → file-agent

是否开始执行？
```

<a id="文件结构"></a>

## 文件结构

```
task-skill-orchestrator/
├── SKILL.md                  # 核心技能指令
├── README.md                 # 中文说明（本文件）
├── README.en.md              # English README
├── CHANGELOG.md              # 版本历史
├── CONTRIBUTING.md           # 贡献指南
├── LICENSE                   # Apache-2.0 许可证
├── meta.json                 # 技能元数据
├── assets/
│   ├── dag-waves.png         # 分波并行机制图
│   └── pipeline.png          # 四阶段流水线图
├── examples/
│   └── parallel_research.py  # 可运行示例，演示 DAG 逻辑
├── scripts/
│   └── orchestrate.py        # 平台无关的 DAG 引擎
├── tests/
│   └── test_orchestrator.py  # DAG 逻辑单元测试
└── tools/
    └── gen_readme_images.py  # 生成 README 配图（Pillow）
```

<a id="运行示例"></a>

## 运行示例

```bash
cd examples
python parallel_research.py
```

输出：

```
============================================================
用户需求：帮我调研特斯拉、比亚迪、蔚来三家公司的 2025 年市场份额...
============================================================

[阶段一] 分析拆解...
4 个子任务：
  [T1] 调研特斯拉 2025 市场份额、核心技术、财报
  [T2] 调研比亚迪 2025 市场份额、核心技术、财报
  [T3] 调研蔚来   2025 市场份额、核心技术、财报
  [T4] 合并三份调研结果，产出对比报告

[阶段二] 构建依赖图...
依赖关系：
  T1 → T4
  T2 → T4
  T3 → T4

[阶段三] 波次规划...
  Wave 0: T1, T2, T3
  Wave 1: T4

============================================================
执行计划：
============================================================
拆解完成。4 个子任务，2 个波次。

Wave 0（并行，3 个任务）：
  • [T1] 调研特斯拉... → search-agent
  • [T2] 调研比亚迪... → search-agent
  • [T3] 调研蔚来...   → search-agent

Wave 1（汇总）：
  • [T4] 合并三份调研结果 → file-agent

是否开始执行？
============================================================
```

---

## 贡献

欢迎提交 Issue 和 PR，请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 版本

完整版本历史见 [CHANGELOG.md](CHANGELOG.md)。

- **v1.0.0**（2026-05-25）：初始版本。核心四阶段流水线：拆解 → 依赖图 → 波次派发 → 汇总。

<a id="许可证"></a>

## 许可证

**Apache-2.0** —— 自由使用、修改、分发，需保留署名与协议声明。完整条款见 [LICENSE](LICENSE)。

Copyright 2026 YardonYan
