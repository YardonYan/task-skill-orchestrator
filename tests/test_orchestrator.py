#!/usr/bin/env python3
"""
Unit tests for the Task Orchestrator DAG engine.
任务编排器 DAG 引擎的单元测试。

Run / 运行:
    cd tests
    python -m pytest test_orchestrator.py -v
"""

import sys
import os

# Add parent scripts/ directory to path so we can import orchestrate
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from orchestrate import TaskDAG, WavePlanner, Task


# ═══════════════════════════════════════════════════════════════
# TaskDAG Tests
# ═══════════════════════════════════════════════════════════════


class TestTaskDAG:
    """Tests for TaskDAG creation and validation."""

    def test_add_single_task(self) -> None:
        dag = TaskDAG()
        dag.add_task("T1", "Research Tesla", agent="search-agent")
        assert dag.task_count == 1
        assert dag.get_task("T1").description == "Research Tesla"

    def test_add_duplicate_task_raises(self) -> None:
        dag = TaskDAG()
        dag.add_task("T1", "Task one")
        try:
            dag.add_task("T1", "Duplicate")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_add_task_with_dependencies(self) -> None:
        dag = TaskDAG()
        dag.add_task("T1", "Research")
        dag.add_task("T2", "Report", depends_on=["T1"])
        assert dag.get_task("T2").depends_on == ["T1"]

    def test_missing_dependency_raises(self) -> None:
        dag = TaskDAG()
        dag.add_task("T1", "Report", depends_on=["T_NONEXISTENT"])
        try:
            dag.validate()
            assert False, "Should have raised ValueError for missing dependency"
        except ValueError as e:
            assert "T_NONEXISTENT" in str(e)

    def test_cycle_detection_simple(self) -> None:
        dag = TaskDAG()
        dag.add_task("T1", "A", depends_on=["T2"])
        dag.add_task("T2", "B", depends_on=["T1"])
        try:
            dag.validate()
            assert False, "Should have raised ValueError for cycle"
        except ValueError:
            pass

    def test_cycle_detection_three_nodes(self) -> None:
        dag = TaskDAG()
        dag.add_task("T1", "A", depends_on=["T3"])
        dag.add_task("T2", "B", depends_on=["T1"])
        dag.add_task("T3", "C", depends_on=["T2"])
        try:
            dag.validate()
            assert False, "Should have raised ValueError for cycle"
        except ValueError:
            pass

    def test_serialization_roundtrip(self) -> None:
        dag = TaskDAG()
        dag.add_task("T1", "Research Tesla", agent="search-agent", output_path="tesla.md")
        dag.add_task("T2", "Research BYD", agent="search-agent", output_path="byd.md")
        dag.add_task("T3", "Merge report", depends_on=["T1", "T2"], agent="file-agent")

        json_str = dag.to_json()
        dag2 = TaskDAG.from_json(json_str)

        assert dag2.task_count == 3
        assert dag2.get_task("T3").depends_on == ["T1", "T2"]

    def test_get_nonexistent_task_raises(self) -> None:
        dag = TaskDAG()
        try:
            dag.get_task("NOPE")
            assert False, "Should have raised KeyError"
        except KeyError:
            pass


# ═══════════════════════════════════════════════════════════════
# WavePlanner Tests
# ═══════════════════════════════════════════════════════════════


class TestWavePlanner:
    """Tests for WavePlanner topology and parallelism."""

    def _build_research_dag(self) -> TaskDAG:
        """Build the standard 3-company research DAG."""
        dag = TaskDAG()
        dag.add_task("T1", "Research Tesla", agent="search-agent",
                     output_path="tesla.md")
        dag.add_task("T2", "Research BYD", agent="search-agent",
                     output_path="byd.md")
        dag.add_task("T3", "Research NIO", agent="search-agent",
                     output_path="nio.md")
        dag.add_task("T4", "Merge report", depends_on=["T1", "T2", "T3"],
                     agent="file-agent",
                     output_path="report.md")
        return dag

    def test_wave_count(self) -> None:
        dag = self._build_research_dag()
        planner = WavePlanner(dag)
        waves = planner.plan()
        assert len(waves) == 2

    def test_wave_0_contains_independent_tasks(self) -> None:
        dag = self._build_research_dag()
        planner = WavePlanner(dag)
        waves = planner.plan()
        wave0_ids = {t.id for t in waves[0]}
        assert wave0_ids == {"T1", "T2", "T3"}

    def test_wave_1_contains_aggregation(self) -> None:
        dag = self._build_research_dag()
        planner = WavePlanner(dag)
        waves = planner.plan()
        wave1_ids = {t.id for t in waves[1]}
        assert wave1_ids == {"T4"}

    def test_all_independent_tasks_single_wave(self) -> None:
        dag = TaskDAG()
        dag.add_task("T1", "Clean desktop", agent="file-agent")
        dag.add_task("T2", "Clear junk", agent="computer-agent")
        dag.add_task("T3", "Backup files", agent="file-agent")
        planner = WavePlanner(dag)
        waves = planner.plan()
        assert len(waves) == 1
        assert len(waves[0]) == 3

    def test_linear_chain(self) -> None:
        """T1 → T2 → T3 → T4 should produce 4 waves of 1 task each."""
        dag = TaskDAG()
        dag.add_task("T1", "Step 1")
        dag.add_task("T2", "Step 2", depends_on=["T1"])
        dag.add_task("T3", "Step 3", depends_on=["T2"])
        dag.add_task("T4", "Step 4", depends_on=["T3"])
        planner = WavePlanner(dag)
        waves = planner.plan()
        assert len(waves) == 4
        for wave in waves:
            assert len(wave) == 1

    def test_diamond_dependency(self) -> None:
        """T1 → T2, T1 → T3, T2 → T4, T3 → T4 (diamond pattern)."""
        dag = TaskDAG()
        dag.add_task("T1", "Root")
        dag.add_task("T2", "Left", depends_on=["T1"])
        dag.add_task("T3", "Right", depends_on=["T1"])
        dag.add_task("T4", "Merge", depends_on=["T2", "T3"])
        planner = WavePlanner(dag)
        waves = planner.plan()
        assert len(waves) == 3
        assert {t.id for t in waves[0]} == {"T1"}
        assert {t.id for t in waves[1]} == {"T2", "T3"}
        assert {t.id for t in waves[2]} == {"T4"}

    def test_parallelism_summary(self) -> None:
        dag = self._build_research_dag()
        planner = WavePlanner(dag)
        summary = planner.get_parallelism_summary()
        assert summary["total_tasks"] == 4
        assert summary["total_waves"] == 2
        assert summary["max_parallelism"] == 3
        assert summary["theoretical_speedup"] == 2.0

    def test_format_plan_does_not_crash(self) -> None:
        dag = self._build_research_dag()
        planner = WavePlanner(dag)
        plan = planner.format_plan()
        assert "Decomposition complete" in plan
        assert "T1" in plan
        assert "T4" in plan
