# Contributing to Task Skill Orchestrator / 贡献指南

Thanks for your interest in contributing! / 感谢你有兴趣贡献！

## How to Contribute / 如何贡献

### Reporting Bugs / 报告 Bug

1. Check [existing issues](https://github.com/YardonYan/task-skill-orchestrator/issues) to avoid duplicates / 先查看已有 Issue 避免重复
2. Open a new issue with:
   - Clear title describing the problem / 清晰描述问题的标题
   - Steps to reproduce / 复现步骤
   - Expected vs actual behavior / 预期行为 vs 实际行为
   - Platform info (OpenClaw version, OS) / 平台信息

### Suggesting Features / 建议新功能

1. Open an issue with the `enhancement` label / 开一个 `enhancement` 标签的 Issue
2. Describe the use case and why it's valuable / 描述使用场景及其价值

### Pull Requests / 提交 PR

1. Fork the repository / Fork 仓库
2. Create a feature branch: `git checkout -b feature/your-feature` / 创建特性分支
3. Follow the existing code style / 遵循现有代码风格
4. Add tests for new functionality / 为新功能添加测试
5. Update documentation if needed / 必要时更新文档
6. Submit a PR with a clear description / 提交清晰描述的 PR

## Development / 开发

### Project Structure / 项目结构

```
task-skill-orchestrator/
├── SKILL.md              # Core skill instructions (LLM prompt) / 核心技能指令
├── README.md             # Project overview / 项目概览
├── meta.json             # Skill metadata / 技能元数据
├── scripts/              # Reusable scripts / 可复用脚本
│   └── orchestrate.py    # Platform-agnostic DAG engine
├── examples/             # Runnable examples / 可运行示例
│   └── parallel_research.py
└── tests/                # Unit tests / 单元测试
    └── test_orchestrator.py
```

### Running Tests / 运行测试

```bash
cd tests
python -m pytest test_orchestrator.py -v
```

### Code Style / 代码风格

- Python: Follow PEP 8 / 遵循 PEP 8
- Documentation: Bilingual (Chinese + English) for user-facing content / 面向用户的内容使用中英双语
- Commit messages: Conventional Commits preferred / 推荐使用 Conventional Commits 格式
