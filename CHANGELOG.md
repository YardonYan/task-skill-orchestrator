# Changelog / 更新日志

All notable changes to this project will be documented in this file.

本项目的所有重要变更都会记录在此文件中。

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-05-25

### Added / 新增
- Initial release / 初始版本
- Four-phase pipeline: Decompose → Build DAG → Wave Planning → Execute & Merge / 四阶段流水线：拆解→构建依赖图→波次规划→执行与汇总
- Dependency-aware DAG construction with automatic validation / 依赖感知的有向无环图构建与自动验证
- Topological wave planning for parallel dispatch / 基于拓扑排序的波次规划
- Multi-agent routing (file-agent, search-agent, browser, app-agent, computer-agent) / 多 Agent 路由
- Result aggregation with failure handling / 带失败处理的结果汇总
- Bilingual documentation (Chinese & English) / 双语文档
- Runnable example (`examples/parallel_research.py`) / 可运行示例
- Platform-agnostic DAG engine (`scripts/orchestrate.py`) / 平台无关的 DAG 引擎
- Unit tests for core DAG logic (`tests/test_orchestrator.py`) / 核心 DAG 逻辑单元测试

### Credits / 致谢
- Core methodology derived from [parallel-task by am-will](https://github.com/am-will/codex-skills) / 核心方法论源自 am-will 的 parallel-task
