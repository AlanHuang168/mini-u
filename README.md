# Mini-U · 量化分析教学版 🚀

[![CI](https://github.com/AlanHuang168/mini-u/actions/workflows/ci.yml/badge.svg)](https://github.com/AlanHuang168/mini-u/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)

简体中文 | [English](./README.en.md)

一个**麻雀虽小、五脏俱全**的 A 股量化分析教学项目。用最少的代码把一条完整的
AI 应用链路讲清楚：**采集真实行情 → 规则引擎打分 → DeepSeek 深度分析 → 生成 HTML 报告**，
再加上「多位投资大佬」角色扮演点评和多股对比，全部由一个 Streamlit 界面驱动。

> ⚠️ **免责声明**：本项目仅用于技术教学与演示，所有分析结果**不构成任何投资建议**。

## 你能从中学到什么

这个项目刻意把下面几个知识点做成可以单独拆开看的模块：

| 知识点 | 对应实现 |
|---|---|
| **collect → analyze → render 三段式 Pipeline** | [`pipeline/`](pipeline/) |
| **规则引擎与 LLM 混合决策**（规则出分，LLM 出解读） | [`rules/scoring.py`](rules/scoring.py) + [`pipeline/analyze.py`](pipeline/analyze.py) |
| **YAML 角色卡**（用配置定义「投资风格」，不写死在代码里） | [`roles/*.yaml`](roles/) |
| **缓存降低 Token 成本**（命中缓存就不再调用 LLM） | [`pipeline/cache.py`](pipeline/cache.py) |
| **DeepSeek 模型调用**（OpenAI 兼容 SDK） | [`pipeline/analyze.py`](pipeline/analyze.py) |
| **Streamlit 展示层** | [`main.py`](main.py) |
| **真实数据 + 优雅降级**（akshare 抓不到就回退 Mock，不崩） | [`pipeline/collect.py`](pipeline/collect.py) |

## 架构一览

```text
                        用户输入股票代码（Streamlit）
                                   │
          ┌────────────────────────┼────────────────────────┐
          ▼                        ▼                         ▼
   ┌─────────────┐         ┌───────────────┐         ┌───────────────┐
   │  collect     │         │   rules 引擎   │         │   analyze      │
   │ akshare 真实 │  ──►    │  YAML 规则打分 │  ──►    │ DeepSeek + 缓存 │
   │ 失败→Mock降级│         │ 确定性、可解释 │         │ 自然语言解读   │
   └─────────────┘         └───────────────┘         └───────┬───────┘
                                                             │
                                    ┌────────────────────────┤
                                    ▼                        ▼
                            ┌───────────────┐        ┌───────────────┐
                            │  render        │        │ role_play      │
                            │ 自包含 HTML 报告│        │ YAML 角色卡点评 │
                            └───────────────┘        └───────────────┘
```

**设计要点**：规则引擎负责「确定性、可解释」的打分（价格、涨跌、ROE 等硬指标），
LLM 只负责「把分数和数据翻译成人话」的深度解读——两者职责分明，这正是
**规则 + LLM 混合决策**的核心思想。

## 快速开始

需要 Python 3.10 或更高版本。

```bash
# 1. 克隆
git clone https://github.com/AlanHuang168/mini-u.git
cd mini-u

# 2. 创建并激活虚拟环境
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows (PowerShell)
# .venv\Scripts\Activate.ps1

# 3. 安装依赖（可选用国内镜像加速）
pip install -r requirements.txt
# pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 4. 运行
streamlit run main.py
```

浏览器打开后：填入股票代码（如 `600519, 000333`，支持逗号分隔多个）→ 点「🚀 开始分析」。

## 配置 DeepSeek API Key

LLM 分析与角色点评需要 DeepSeek 的 Key（[申请地址](https://platform.deepseek.com/)）。三种方式任选其一：

1. **界面输入**（推荐）：在 Streamlit 页面顶部的输入框直接粘贴，仅存于当前浏览器会话，不落盘。
2. **环境变量**：复制 `.env.example` 为 `.env`，填入 `DEEPSEEK_API_KEY=...`。
3. **不配置**：勾选「演示模式」或留空 Key，走 Mock 数据 + 演示文案，**零成本跑通全链路**。

## 目录结构

```text
mini-u/
├── main.py               # Streamlit 入口（聚合整条 Pipeline）
├── SKILL.md              # Skill 身份卡（子命令声明）
├── requirements.txt      # 运行时依赖
├── requirements-dev.txt  # 测试依赖
├── pipeline/             # ★ 核心三段式 Pipeline
│   ├── collect.py        #   采集：akshare 真实数据 + Mock 降级
│   ├── analyze.py        #   分析：DeepSeek 调用 + 缓存
│   ├── render.py         #   渲染：自包含 HTML 报告
│   └── cache.py          #   缓存：按 ticker + 有效期存取
├── rules/                # ★ 规则引擎（确定性打分）
│   ├── scoring.py        #   规则求值主逻辑
│   └── config/rules.yaml #   规则配置（可编辑，无需改代码）
├── roles/                # ★ YAML 角色卡（巴菲特/木头姐/赵老哥/陈小群）
├── prompts/              # Prompt 模板
├── skills/               # 子 Skill（多角色点评、多股对比）
├── tests/                # 单元测试（规则引擎，无需联网）
└── docs/                 # 教学讲义、PPT、样例报告
```

## 特性详解

### 真实数据 + 优雅降级
[`collect.py`](pipeline/collect.py) 优先用 [akshare](https://github.com/akfamily/akshare) 抓实时行情；
一旦网络失败或代码不存在，**自动回退到内置 Mock 数据**并打印告警，保证整条链路永远跑得通、演示不翻车。

### 规则引擎（可配置）
打分规则写在 [`rules/config/rules.yaml`](rules/config/rules.yaml)，形如「价格 > 1000 加 15 分」。
改规则**不用动 Python 代码**，改 YAML 即可。评分结果同时给出建议（强烈推荐/推荐/观望/回避）和命中的规则列表，完全可解释。

### YAML 角色卡
每位「投资大佬」是一个 [`roles/*.yaml`](roles/)，定义 `name / style / focus / prompt`。
新增一位评论员只需加一个 YAML 文件，无需改代码——这就是**用配置驱动人设**。

### 缓存降低成本
[`cache.py`](pipeline/cache.py) 按 `ticker + mode` 落 JSON，默认 6 小时有效。
命中缓存直接返回，**不再发起 DeepSeek 调用**，省 Token、省钱、也更快。

## 教学阶段

项目按难度拆成 5 个渐进阶段，适合照着一步步学（详见 [`docs/TECH_OVERVIEW.md`](docs/TECH_OVERVIEW.md)）：

| 阶段 | 目标 | 难度 | 教学价值 |
|---|---|---|---|
| 1 | 理解 Pipeline：把代码拆成 collect → analyze → render | 低 | 最高 |
| 2 | 理解规则 vs LLM：把规则引擎和 LLM 明确分模块 | 中 | 很高 |
| 3 | 理解报告生成：做出自包含 HTML 报告 | 中 | 高 |
| 4 | 理解缓存与鲁棒性：加缓存 + fallback | 中 | 实用 |
| 5 | 理解 Skill 结构：加 SKILL.md + 多命令 | 中高 | 架构思维 |

## 测试

```bash
pip install -r requirements-dev.txt
pytest
```

测试只覆盖**规则引擎**等纯函数（不联网、不调用 LLM），CI 会在每次 PR 上自动运行。

## 参与贡献

欢迎 Issue 和 PR。提交前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 与 [行为准则](CODE_OF_CONDUCT.md)。
安全问题请按 [SECURITY.md](SECURITY.md) 私下反馈。

## 许可证

[MIT](./LICENSE) © 2026 AlanHuang168
