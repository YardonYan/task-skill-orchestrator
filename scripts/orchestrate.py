#!/usr/bin/env python3
"""
Task Orchestrator — Platform-Agnostic DAG Engine
任务编排器 — 平台无关的 DAG 引擎

A reusable, framework-agnostic engine for decomposing tasks into
dependency-aware DAGs and planning parallel execution waves.

可复用的、框架无关的任务拆解引擎，将任务拆解为依赖感知的 DAG 并规划并行执行波次。

Usage / 用法:
    from orchestrate import TaskDAG, WavePlanner

    dag = TaskDAG()
    dag.add_task("T1", description="Research Tesla")
    dag.add_task("T2", description="Research BYD")
    dag.add_task("T3", description="Merge results", depends_on=["T1", "T2"])

    dag.validate()  # Raises ValueError if cycles detected

    planner = WavePlanner(dag)
    waves = planner.plan()
    for i, wave in enumerate(waves):
        print(f"Wave {i}: {[t.id for t in wave]}")
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


# ═══════════════════════════════════════════════════════════════
# Data Models / 数据模型
# ═══════════════════════════════════════════════════════════════


@dataclass
class Task:
    """A single atomic subtask / 单个原子子任务."""

    id: str
    description: str
    depends_on: List[str] = field(default_factory=list)
    agent: str = "search-agent"  # Default agent / 默认 Agent
    output_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════
# DAG Engine / DAG 引擎
# ═══════════════════════════════════════════════════════════════


class TaskDAG:
    """Directed Acyclic Graph of tasks with dependency management.
    带依赖管理的任务有向无环图。"""

    def __init__(self) -> None:
        self._tasks: Dict[str, Task] = {}
        self._edges: Dict[str, Set[str]] = {}  # from_id → {to_id, ...}

    # ── CRUD ──────────────────────────────────────────────────

    def add_task(
        self,
        task_id: str,
        description: str,
        depends_on: Optional[List[str]] = None,
        agent: str = "search-agent",
        output_path: Optional[str] = None,
        **metadata: Any,
    ) -> Task:
        """Add a task to the DAG. / 向 DAG 添加任务。

        Args:
            task_id: Unique task identifier / 唯一任务标识
            description: Human-readable task description / 可读的任务描述
            depends_on: List of task IDs this task depends on / 此任务依赖的任务 ID 列表
            agent: Target agent for dispatching / 派发目标 Agent
            output_path: Expected output file path / 预期输出文件路径
            **metadata: Additional metadata / 额外元数据

        Returns:
            The created Task object / 创建的 Task 对象

        Raises:
            ValueError: If task_id already exists / 如果 task_id 已存在
        """
        if task_id in self._tasks:
            raise ValueError(f"Task '{task_id}' already exists / 任务 '{task_id}' 已存在")

        deps = depends_on or []
        task = Task(
            id=task_id,
            description=description,
            depends_on=deps,
            agent=agent,
            output_path=output_path,
            metadata=metadata,
        )
        self._tasks[task_id] = task
        self._edges[task_id] = set()

        # Register reverse edges for dependency tracking
        for dep_id in deps:
            if dep_id not in self._edges:
                self._edges[dep_id] = set()
            self._edges[dep_id].add(task_id)

        return task

    def get_task(self, task_id: str) -> Task:
        """Get a task by ID. / 按 ID 获取任务。"""
        if task_id not in self._tasks:
            raise KeyError(f"Task '{task_id}' not found / 任务 '{task_id}' 未找到")
        return self._tasks[task_id]

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks. / 返回所有任务。"""
        return list(self._tasks.values())

    @property
    def task_count(self) -> int:
        """Number of tasks in the DAG. / DAG 中的任务数。"""
        return len(self._tasks)

    # ── Validation ────────────────────────────────────────────

    def validate(self) -> None:
        """Validate the DAG: no cycles, no missing dependencies.
        验证 DAG：无环、无缺失依赖。

        Raises:
            ValueError: If cycles or missing dependencies are detected
        """
        # Check for missing dependency references
        for task in self._tasks.values():
            for dep_id in task.depends_on:
                if dep_id not in self._tasks:
                    raise ValueError(
                        f"Task '{task.id}' depends on '{dep_id}' "
                        f"which does not exist / 任务 '{task.id}' 依赖的 "
                        f"'{dep_id}' 不存在"
                    )

        # Cycle detection via topological ordering attempt
        self._topological_order()  # Will raise if cycles exist

    def _topological_order(self) -> List[str]:
        """Compute topological order. Raises ValueError on cycles.
        计算拓扑序，有环时报错。"""
        in_degree = {tid: len(t.depends_on) for tid, t in self._tasks.items()}
        order: List[str] = []
        queue = [tid for tid, deg in in_degree.items() if deg == 0]

        while queue:
            node = queue.pop(0)
            order.append(node)
            for neighbor in self._edges.get(node, set()):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(self._tasks):
            remaining = set(self._tasks.keys()) - set(order)
            raise ValueError(
                f"Cycle detected in DAG! / DAG 中检测到环路！ "
                f"Remaining nodes: {remaining}"
            )

        return order

    # ── Serialization ─────────────────────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        """Serialize DAG to dictionary. / 将 DAG 序列化为字典。"""
        return {
            "tasks": [
                {
                    "id": t.id,
                    "description": t.description,
                    "depends_on": t.depends_on,
                    "agent": t.agent,
                    "output_path": t.output_path,
                    "metadata": t.metadata,
                }
                for t in self._tasks.values()
            ]
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize DAG to JSON string. / 将 DAG 序列化为 JSON 字符串。"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskDAG":
        """Deserialize DAG from dictionary. / 从字典反序列化 DAG。"""
        dag = cls()
        for t_data in data.get("tasks", []):
            dag.add_task(
                task_id=t_data["id"],
                description=t_data["description"],
                depends_on=t_data.get("depends_on", []),
                agent=t_data.get("agent", "search-agent"),
                output_path=t_data.get("output_path"),
                **t_data.get("metadata", {}),
            )
        return dag

    @classmethod
    def from_json(cls, json_str: str) -> "TaskDAG":
        """Deserialize DAG from JSON string. / 从 JSON 字符串反序列化 DAG。"""
        return cls.from_dict(json.loads(json_str))


# ═══════════════════════════════════════════════════════════════
# Wave Planner / 波次规划器
# ═══════════════════════════════════════════════════════════════


class WavePlanner:
    """Topological wave planner for parallel execution.
    用于并行执行的拓扑波次规划器。"""

    def __init__(self, dag: TaskDAG) -> None:
        self._dag = dag

    def plan(self) -> List[List[Task]]:
        """Generate wave plan using topological layering.
        使用拓扑分层生成波次计划。

        Returns:
            List of waves, each wave is a list of Tasks that can run in parallel
            波次列表，每波包含可并行执行的任务列表
        """
        # Validate first
        self._dag.validate()

        in_degree = {tid: len(t.depends_on) for tid, t in self._dag._tasks.items()}
        edges = self._dag._edges
        tasks_by_id = self._dag._tasks
        remaining = set(tasks_by_id.keys())

        waves: List[List[Task]] = []

        while remaining:
            wave = [
                tasks_by_id[tid]
                for tid in list(remaining)
                if in_degree[tid] == 0
            ]

            if not wave:
                raise ValueError(
                    f"Cycle detected: remaining nodes with unresolved "
                    f"dependencies: {remaining}"
                )

            waves.append(wave)

            for task in wave:
                remaining.remove(task.id)
                for dep_id in edges.get(task.id, set()):
                    in_degree[dep_id] -= 1

        return waves

    def get_wave_count(self) -> int:
        """Return number of waves. / 返回波次数。"""
        return len(self.plan())

    def get_parallelism_summary(self) -> Dict[str, Any]:
        """Return parallelism metrics. / 返回并行度指标。"""
        waves = self.plan()
        return {
            "total_tasks": self._dag.task_count,
            "total_waves": len(waves),
            "max_parallelism": max(len(w) for w in waves) if waves else 0,
            "wave_sizes": [len(w) for w in waves],
            "theoretical_speedup": round(
                self._dag.task_count / len(waves), 2
            ) if waves else 1.0,
        }

    def format_plan(self) -> str:
        """Generate human-readable execution plan.
        生成可读的执行计划。"""
        waves = self.plan()
        lines = [
            f"{'='*60}",
            f"Decomposition complete. {self._dag.task_count} subtasks, "
            f"{len(waves)} waves. / 任务拆解完成。",
            f"{'='*60}",
        ]

        for i, wave in enumerate(waves):
            label = "Parallel / 并行" if len(wave) > 1 else "Solo / 单独"
            if i == len(waves) - 1 and any(t.depends_on for t in wave):
                label = "Aggregation / 汇总"

            lines.append(f"\nWave {i} ({label}, {len(wave)} task(s)):")
            for task in wave:
                deps = f" (depends on: {', '.join(task.depends_on)})" if task.depends_on else ""
                lines.append(f"  [{task.id}] {task.description}{deps}")
                lines.append(f"       → {task.agent}")

        lines.append(f"\n{'='*60}")
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# CLI Entry Point / CLI 入口
# ═══════════════════════════════════════════════════════════════


def main() -> None:
    """CLI entry point: read DAG JSON from stdin, output wave plan.
    CLI 入口：从 stdin 读取 DAG JSON，输出波次计划。"""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] in ("--help", "-h"):
        print(__doc__)
        print("\nUsage / 用法:")
        print("  echo '<dag-json>' | python orchestrate.py")
        print("  python orchestrate.py --help")
        return

    try:
        data = json.load(sys.stdin)
        dag = TaskDAG.from_dict(data)
        dag.validate()
        planner = WavePlanner(dag)
        print(planner.format_plan())
        print(f"\nMetrics / 指标: {json.dumps(planner.get_parallelism_summary(), ensure_ascii=False)}")
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error / 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
