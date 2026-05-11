# 贡献指南 Contributing Guide

感谢您对 SmartClip 的兴趣！我们欢迎各种形式的贡献。

Thank you for your interest in SmartClip! We welcome all forms of contributions.

## 🚀 如何贡献 How to Contribute

### 1. 报告问题 Reporting Issues

- 使用 GitHub Issues 报告 bug 或提出功能建议
- 请提供详细的复现步骤和环境信息
- 如果是功能建议，请描述使用场景和预期行为

### 2. 提交代码 Submitting Code

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 3. 代码规范 Code Standards

- 遵循 PEP 8 Python 代码规范
- 添加适当的注释和文档字符串
- 确保代码通过所有测试
- 保持与现有代码风格一致

## 📝 提交信息规范 Commit Message Convention

我们使用 Angular 提交规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

类型 (Type):
- `feat`: 新功能
- `fix`: 修复
- `docs`: 文档
- `style`: 格式调整
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建/工具

## 🧪 测试 Testing

```bash
# 运行测试
python -m pytest tests/

# 检查代码风格
flake8 smartclip.py

# 类型检查
mypy smartclip.py
```

## 📋 开发环境设置 Development Setup

```bash
# 克隆仓库
git clone https://github.com/gitstq/SmartClip.git
cd SmartClip

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 运行应用
python smartclip.py
```

## 🌟 贡献者 Contributors

感谢所有为 SmartClip 做出贡献的人！

<a href="https://github.com/gitstq/SmartClip/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=gitstq/SmartClip" />
</a>

## 📄 许可证 License

通过提交代码，您同意您的贡献将在 MIT 许可证下发布。

By submitting code, you agree that your contributions will be licensed under the MIT License.
