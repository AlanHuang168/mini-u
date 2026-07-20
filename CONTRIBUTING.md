# 贡献指南

感谢你为 Mini-U 做贡献！这是一个教学项目，欢迎任何让它更清晰、更好学的改动。

## 开发环境

需要 Python 3.10 或更高版本。

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

## 运行与测试

```bash
streamlit run main.py   # 本地跑起来
pytest                  # 跑单元测试（纯函数，不联网）
```

## 提交流程

1. 从 `master` 新建分支：`git checkout -b feat/你的改动` 或 `fix/...`、`docs/...`、`chore/...`。
2. 保持改动聚焦，一个 PR 只做一件事。
3. 行为有变更时补上对应测试。
4. 提交信息用简洁的祈使句，建议遵循 [Conventional Commits](https://www.conventionalcommits.org/)
   （`feat:` / `fix:` / `docs:` / `chore:` / `refactor:` / `test:`）。
5. 推送分支后发起 Pull Request，在描述里说明**改了什么、为什么、怎么验证的**。

## PR 期望

- 诚实报告：跑过哪些命令、结果如何、有没有失败。
- 不提交生成产物（`reports/`、`cache/` 已在 `.gitignore` 中忽略）。
- 文档随代码同步更新（改了行为就更新 README / 注释）。
- 保持中文默认、英文同步：`README.md` 与 `README.en.md` 两份要一致。

## 代码风格

- 遵循 PEP 8，函数写清楚 docstring。
- 规则改动优先改 [`rules/config/rules.yaml`](rules/config/rules.yaml)，而不是硬编码进 Python。
- 新增角色评论员：在 [`roles/`](roles/) 下加一个 YAML 文件即可，不用改代码。

有任何疑问，欢迎先开 Issue 讨论。
