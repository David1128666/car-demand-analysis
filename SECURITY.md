# Security Policy

> This document is bilingual. The English version appears first, followed by
> the Simplified Chinese version.

## English

### Supported Versions

Security fixes are applied to the latest code on the `main` branch.

### Reporting a Vulnerability

Do not open a public issue for passwords, access tokens, database exposure,
authentication bypasses, remote code execution, or other sensitive findings.

Use the private security contact on the repository owner's GitHub profile.
Include:

- The affected component and version.
- Reproduction steps.
- Expected and actual behavior.
- Potential impact.
- A suggested fix when available.

### Secret Handling

- Never commit `.env`, passwords, API keys, private keys, or database dumps.
- Use `.env.example` for public configuration templates.
- Rotate credentials immediately if they are exposed.
- Use environment variables or a secret manager in production.

### Data Handling

- Do not upload real customer or personal data.
- Use synthetic or authorized data in examples and tests.
- Confirm the redistribution and commercial-use terms of every public dataset.

## 中文

### 支持版本

安全修复应用于 `main` 分支上的最新代码。

### 报告安全问题

不要通过公开 Issue 提交密码、访问令牌、数据库暴露、认证绕过、远程代码执行
或其他敏感问题。

请通过仓库所有者的 GitHub 主页私下联系维护者，并包含：

- 受影响的组件和版本。
- 复现步骤。
- 预期行为和实际行为。
- 潜在影响。
- 可提供时附上修复建议。

### 密钥处理

- 不要提交 `.env`、密码、API Key、私钥或数据库备份。
- 公开配置模板使用 `.env.example`。
- 凭据一旦泄露，应立即轮换。
- 生产环境应使用环境变量或密钥管理服务。

### 数据处理

- 不要上传真实客户数据或个人数据。
- 示例和测试应使用模拟数据或已获授权的数据。
- 使用公开数据集前，应确认再分发和商业使用条款。
