# 更新日志

本项目所有重要变更都记录在此。

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [未发布]

### 新增

- 双语 README（`README.md` 中文默认 + `README.en.md` 英文，可互相跳转）。
- 开源标准社区文件：`LICENSE`、`CONTRIBUTING.md`、`CODE_OF_CONDUCT.md`、`SECURITY.md`、`CHANGELOG.md`。
- `.github/` 模板：Issue 模板、PR 模板、GitHub Actions CI（安装依赖 + 跑 pytest）。
- `.gitattributes`（强制 LF）、`.env.example`、`requirements-dev.txt`。
- 规则引擎单元测试 `tests/test_scoring.py`（纯函数、离线）。

### 变更

- 教学文件（`TECH_OVERVIEW.md`、`SLIDES.md`、PPT、`build_ppt.py`）统一移入 `docs/`。
- 保留一份样例报告到 `docs/examples/sample-report.html`。

### 移除

- 生成产物 `reports/`、`cache/` 移出版本控制（改为 `.gitignore` 忽略）。
- 删除与 `main.py` 完全重复的 `streamlit_app.py`。
- 删除未被引用的死代码 `rules/basic_rules.py`。

## [1.0.0] - 2026-07

### 新增

- 三段式 Pipeline：collect（akshare 真实数据 + Mock 降级）→ analyze（DeepSeek + 缓存）→ render（HTML 报告）。
- 规则引擎（`rules/config/rules.yaml` 可配置打分）。
- YAML 角色卡多角色点评、多股对比。
- Streamlit 交互界面。
