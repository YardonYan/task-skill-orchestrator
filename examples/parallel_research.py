#!/usr/bin/env python3
"""
Task Orchestrator Example: Parallel Research & Report Generation
Demonstrates the four-phase pipeline: decompose → DAG → wave plan → dispatch.

任务编排大师示例：并行调研与报告生成
演示四阶段流水线：拆解 → 依赖图 → 波次规划 → 派发。

Inspired by parallel-task by am-will (https://github.com/am-will/codex-skills).
"""

import json
from typing import List, Dict, Set, Tuple

class TaskOrchestrator:
    """Core orchestrator class / 核心编排器类"""

    def __init__(self, user_request: str):
        self.user_request = user_request
        self.tasks: List[Dict] = []
        self.dependencies: List[Tuple[str, str]] = []
        self.agent_mapping = {
            "file": "file-agent",
            "search": "search-agent",
            "browser": "browser",
            "app": "app-agent",
            "computer": "computer-agent"
        }

    # ─── Phase 1: Analyze & Decompose ──────────────────────────

    def analyze_and_decompose(self) -> List[Dict]:
        """Phase 1: Analyze the user request and split into atomic subtasks.
        阶段一：分析用户需求，拆分为原子子任务。

        ⚠️ DEMO-ONLY: This implementation uses hardcoded pattern matching for
        demonstration. In production, replace with LLM-based decomposition
        following the specification in SKILL.md Phase 1.

        ⚠️ 仅演示：此实现使用硬编码模式匹配进行演示。生产环境中应替换为
        基于 LLM 的拆解，遵循 SKILL.md 阶段一的规范。
        """
        if ("Tesla" in self.user_request or "特斯拉" in self.user_request) and \
           ("BYD" in self.user_request or "比亚迪" in self.user_request) and \
           ("NIO" in self.user_request or "蔚来" in self.user_request):

            self.tasks = [
                {
                    "id": "T1",
                    "description": "Research Tesla 2025 market share, core technology, and latest financial report",
                    "agent": "search",
                    "dependencies": [],
                    "output": "tesla_research.md"
                },
                {
                    "id": "T2",
                    "description": "Research BYD 2025 market share, core technology, and latest financial report",
                    "agent": "search",
                    "dependencies": [],
                    "output": "byd_research.md"
                },
                {
                    "id": "T3",
                    "description": "Research NIO 2025 market share, core technology, and latest financial report",
                    "agent": "search",
                    "dependencies": [],
                    "output": "nio_research.md"
                },
                {
                    "id": "T4",
                    "description": "Aggregate three research results into a comparison report with market share comparison, technology roadmap analysis, and financial data comparison",
                    "agent": "file",
                    "dependencies": ["T1", "T2", "T3"],
                    "output": "car_companies_comparison_report.md"
                }
            ]

        elif "桌面" in self.user_request and "垃圾" in self.user_request and "备份" in self.user_request:

            self.tasks = [
                {
                    "id": "T1",
                    "description": "Organize desktop files into categorized folders (documents/images/archives)",
                    "agent": "file",
                    "dependencies": [],
                    "output": None
                },
                {
                    "id": "T2",
                    "description": "Clean system junk files (temp files, cache, recycle bin)",
                    "agent": "computer",
                    "dependencies": [],
                    "output": None
                },
                {
                    "id": "T3",
                    "description": "Back up important files from D: drive to E: drive",
                    "agent": "file",
                    "dependencies": [],
                    "output": None
                }
            ]

        else:
            # Generic fallback: create a simple two-wave plan
            # 通用回退：创建简单两波计划
            self.tasks = [
                {
                    "id": "T1",
                    "description": f"Process part 1 of: {self.user_request[:60]}...",
                    "agent": "search",
                    "dependencies": [],
                    "output": "result_part1.md"
                },
                {
                    "id": "T2",
                    "description": f"Process part 2 of: {self.user_request[:60]}...",
                    "agent": "search",
                    "dependencies": [],
                    "output": "result_part2.md"
                },
                {
                    "id": "T3",
                    "description": f"Aggregate T1 and T2 results for: {self.user_request[:60]}...",
                    "agent": "file",
                    "dependencies": ["T1", "T2"],
                    "output": "final_result.md"
                }
            ]

        return self.tasks

    # ─── Phase 2: Build DAG ────────────────────────────────────

    def build_dag(self) -> Dict[str, Set[str]]:
        """Phase 2: Build the dependency graph (DAG).
        阶段二：构建依赖图（有向无环图）。
        """
        dag = {t["id"]: set() for t in self.tasks}
        for t in self.tasks:
            for dep_id in t["dependencies"]:
                dag[dep_id].add(t["id"])
        return dag

    # ─── Phase 3: Wave Planning ─────────────────────────────────

    def plan_waves(self) -> List[List[Dict]]:
        """Phase 3: Topological sort into execution waves.
        阶段三：拓扑排序生成执行波次。
        """
        dag = self.build_dag()
        tasks_by_id = {t["id"]: t for t in self.tasks}

        # Calculate in-degrees
        in_degree = {tid: 0 for tid in dag}
        for from_id, to_set in dag.items():
            for to_id in to_set:
                in_degree[to_id] += 1

        waves = []
        remaining = set(tasks_by_id.keys())

        while remaining:
            wave = []
            for tid in list(remaining):
                if in_degree[tid] == 0:
                    wave.append(tasks_by_id[tid])
                    remaining.remove(tid)

            if not wave:
                raise ValueError(
                    f"Cycle detected in DAG! "
                    f"Remaining nodes with unresolved dependencies: {remaining}. "
                    f"In-degrees: { {tid: in_degree[tid] for tid in remaining} }"
                )

            waves.append(wave)

            # Update in-degrees after removing this wave
            for task in wave:
                for dep_id in dag[task["id"]]:
                    in_degree[dep_id] -= 1

        return waves

    # ─── Phase 4: Generate Execution Plan ───────────────────────

    def generate_execution_plan(self) -> str:
        """Generate human-readable execution plan.
        生成可读的执行计划。
        """
        waves = self.plan_waves()

        plan = f"\n{'='*60}\n"
        plan += f"Decomposition complete. {len(self.tasks)} subtasks, {len(waves)} waves.\n"
        plan += f"任务拆解完成。{len(self.tasks)} 个子任务，{len(waves)} 波执行。\n"
        plan += f"{'='*60}\n"

        for i, wave in enumerate(waves):
            label = "Parallel / 并行" if len(wave) > 1 else "Solo / 单独"
            if i == len(waves) - 1 and any(t["dependencies"] for t in wave):
                label = "Aggregation (depends on all previous) / 汇总（依赖前序所有）"

            plan += f"\nWave {i} ({label}, {len(wave)} task(s)):\n"
            for task in wave:
                plan += f"  [{task['id']}] {task['description']}\n"
                plan += f"       → {self.agent_mapping[task['agent']]}\n"

        # Show dependencies
        deps_shown = False
        for t in self.tasks:
            if t["dependencies"]:
                if not deps_shown:
                    plan += f"\nDependencies / 依赖关系:\n"
                    deps_shown = True
                plan += f"  [{t['id']}] depends on / 依赖: {', '.join(t['dependencies'])}\n"

        plan += f"\n{'='*60}\n"
        plan += f"Proceed with execution? / 是否开始执行？\n"
        plan += f"{'='*60}\n"

        return plan

    # ─── Dispatch Task Generation ───────────────────────────────

    def generate_dispatch_tasks(self, wave_index: int) -> List[Dict]:
        """Generate dispatch_task parameters for a given wave.
        生成指定波次的 dispatch_task 调用参数。
        """
        waves = self.plan_waves()
        if wave_index >= len(waves):
            return []

        dispatch_list = []
        for task in waves[wave_index]:
            task_desc = (
                f"<overall_goal>\n{self.user_request}\n</overall_goal>\n"
                f"<current_task>\n{task['description']}\n</current_task>"
            )

            dispatch_list.append({
                "agent_name": self.agent_mapping[task["agent"]],
                "task": task_desc,
                "memory_ids": []
            })

        return dispatch_list


# ═══════════════════════════════════════════════════════════════
# Demo / 演示
# ═══════════════════════════════════════════════════════════════

def main():
    user_request = (
        "帮我调研特斯拉、比亚迪、蔚来三家公司的 2025 年市场份额、核心技术和最新财报，"
        "最后汇总成对比报告"
    )

    print("User request / 用户需求：")
    print(user_request)

    orchestrator = TaskOrchestrator(user_request)

    # Phase 1
    print("\n[Phase 1 / 阶段一] Decomposing... / 正在拆解...")
    tasks = orchestrator.analyze_and_decompose()
    print(f"Decomposed into {len(tasks)} atomic subtasks / 拆解为 {len(tasks)} 个子任务。")

    # Phase 2
    print("\n[Phase 2 / 阶段二] Building DAG... / 正在构建依赖图...")
    dag = orchestrator.build_dag()
    for from_id, to_set in dag.items():
        if to_set:
            print(f"  {from_id} → {', '.join(to_set)}")

    # Phase 3
    print("\n[Phase 3 / 阶段三] Planning waves... / 正在规划波次...")
    waves = orchestrator.plan_waves()
    for i, wave in enumerate(waves):
        ids = [t["id"] for t in wave]
        print(f"  Wave {i}: {', '.join(ids)}")

    # Phase 4: Show plan
    print("\n" + orchestrator.generate_execution_plan())

    # Show dispatch details
    print("How Wave 0 would be dispatched / Wave 0 派发方式：")
    wave0 = orchestrator.generate_dispatch_tasks(0)
    for i, d in enumerate(wave0):
        print(f"\n  Call {i+1}: dispatch_task(")
        print(f"    agent_name=\"{d['agent_name']}\"")
        print(f"    task=\"{d['task'][:80]}...\"")
        print(f"  )")

    print(f"\n{'─'*60}")
    print("In production, all {0} Wave 0 calls are issued in ONE assistant message for true parallelism.".format(len(wave0)))
    print("生产环境中，Wave 0 的所有 {0} 个调用在同一条 assistant 消息中发出，实现真并行。".format(len(wave0)))
    print(f"{'─'*60}\n")


if __name__ == "__main__":
    main()