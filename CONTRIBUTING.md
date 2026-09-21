# Contributing

> This document is bilingual. The English version appears first, followed by
> the Simplified Chinese version.

## English

### Development Principles

1. Never commit real credentials, personal data, database dumps, or large
   generated artifacts.
2. Keep the frontend fully translated in both English and Simplified Chinese.
3. Update documentation and tests when behavior or APIs change.
4. Keep changes focused and avoid unrelated formatting churn.

### Environment

- JDK 11
- Maven 3.8+
- Python 3.11+
- Node.js 18+ (20 LTS recommended)
- MySQL 8.0+
- Kafka 3.x and Spark 3.3.1 for the data pipeline

### Local Verification

Frontend:

```bash
cd frontend
npm install
npm run check:locales
npm run build
```

Backend:

```bash
python -m compileall -q backend
```

Scala:

```bash
mvn -f car-demand-analysis/pom.xml -DskipTests package
```

### Documentation Language

- `README.md` is the GitHub homepage and must remain in English.
- Other user-facing Markdown documents should be bilingual unless there is a
  specific reason to keep them in one language.
- New frontend text must be added to both
  `frontend/src/locales/en.js` and `frontend/src/locales/zh-CN.js`.

### Branches and Commits

- Default branch: `main`
- Feature branches: `feat/<short-description>`
- Fix branches: `fix/<short-description>`
- Documentation branches: `docs/<short-description>`

Recommended commit prefixes:

```text
feat: add a user-facing capability
fix: correct a bug
docs: update documentation
test: add or update tests
chore: update tooling or maintenance files
```

### Pull Requests

Describe the problem, the solution, verification commands, and any migration or
security impact. Keep pull requests scoped to one logical change.

## 中文

### 开发原则

1. 不要提交真实凭据、个人数据、数据库备份或大型生成文件。
2. 前端新增文案必须同时提供英文和简体中文。
3. 行为或 API 变化时，同步更新文档和测试。
4. 保持改动聚焦，避免无关格式化。

### 开发环境

- JDK 11
- Maven 3.8+
- Python 3.11+
- Node.js 18+，推荐 20 LTS
- MySQL 8.0+
- 数据链路需要 Kafka 3.x 和 Spark 3.3.1

### 本地验证

前端：

```bash
cd frontend
npm install
npm run check:locales
npm run build
```

后端：

```bash
python -m compileall -q backend
```

Scala：

```bash
mvn -f car-demand-analysis/pom.xml -DskipTests package
```

### 文档语言

- `README.md` 是 GitHub 项目主页，必须保持英文。
- 其他面向用户的 Markdown 文档应为中英双语，除非有特定原因只保留一种语言。
- 前端新增文案必须同时添加到
  `frontend/src/locales/en.js` 和 `frontend/src/locales/zh-CN.js`。

### 分支与提交

- 默认分支：`main`
- 功能分支：`feat/<short-description>`
- 修复分支：`fix/<short-description>`
- 文档分支：`docs/<short-description>`

推荐提交前缀：

```text
feat: 新增用户功能
fix: 修复问题
docs: 更新文档
test: 新增或更新测试
chore: 更新工具或维护文件
```

### Pull Request

请说明问题、解决方案、验证命令，以及迁移或安全影响。每个 Pull Request
应聚焦于一个逻辑改动。
