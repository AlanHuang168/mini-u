# Mini-U 量化分析员 — 技术细节（教学案例）

> 一个展示 **"规则引擎 + LLM"混合架构** 的 Streamlit 教学应用，用于 A 股个股分析。

---

## 整体架构

```
用户输入股票代码
     ↓
[Pipeline 三步流程]
Step 1: collect.py   → akshare 采集行情 + 规则引擎打分
Step 2: analyze.py   → DeepSeek LLM 生成 AI 分析
Step 3: render.py    → 生成 HTML 报告

[Skills 插件层]
compare_skill   → 多股票对比（复用 Pipeline）
role_play_skill → 多角色投资评论（巴菲特、赵老哥等）

[缓存层]
cache.py        → JSON 文件缓存，6小时过期
```

---

## 技术栈

| 模块 | 技术 |
|------|------|
| Web UI | Streamlit |
| 行情数据 | akshare（A股数据） |
| LLM | DeepSeek（兼容 OpenAI SDK） |
| 模板 | Jinja2 |
| 角色配置 | YAML |
| 缓存 | JSON 文件（本地） |

---

## 核心设计模式（教学重点）

### 1. Pipeline 模式

三个独立步骤（collect → analyze → render）通过字典 `data` 串联，每步只做一件事，便于单独替换和测试。

### 2. 规则引擎 + LLM 混合

- `rules/scoring.py`：基于 YAML 配置的规则引擎，条件语句（`price > 1000`）自动打分（50 基础分 + 规则加减分）
- `pipeline/analyze.py`：把规则结果作为上下文传给 DeepSeek，LLM 做解读而不是做数据计算

**关键思路**：规则引擎处理结构化逻辑（可解释、可审计），LLM 处理自然语言叙述（灵活、可读）。

### 3. Skill 插件层

`skills/` 目录下每个子目录是一个独立功能包，通过组合调用 Pipeline 模块实现复杂功能，主应用只需 `from skills.xxx import xxx`。

### 4. 优雅降级（Graceful Degradation）

- akshare 抓取失败 → fallback 到 Mock 数据（不崩溃）
- 未配置 API Key → 返回演示模式文案（不报错）
- 缓存命中 → 跳过 LLM 调用（节省费用）

---

## Bug 修复说明（教学点：API Key 安全）

**错误做法**（修复前）：

```python
# 把用户输入写入 os.environ（进程级别，所有用户共享）
os.environ["DEEPSEEK_API_KEY"] = deepseek_key
# 下次 rerun 从环境变量回填 → Key 泄露给其他用户
value=os.getenv("DEEPSEEK_API_KEY", "")
```

**正确做法**（修复后）：

```python
# 用 session_state（每个浏览器会话独立）
if "deepseek_key" not in st.session_state:
    st.session_state.deepseek_key = ""
# Key 通过参数显式传递，不污染全局环境
analyze_with_llm(data, api_key=effective_key)
```

**核心原则**：在多用户 Web 应用中，敏感信息（API Key）只能存在会话级别（`session_state`），不能存在进程级别（`os.environ`）。

---

## 目录结构

```
mini-u/
├── streamlit_app.py        # 主入口（UI 层）
├── pipeline/
│   ├── collect.py          # Step 1：数据采集 + 规则打分
│   ├── analyze.py          # Step 2：DeepSeek LLM 分析
│   ├── render.py           # Step 3：HTML 报告生成
│   └── cache.py            # JSON 文件缓存（6小时 TTL）
├── rules/
│   ├── scoring.py          # 规则引擎主函数
│   └── config/rules.yaml   # 规则配置（可热更新）
├── skills/
│   ├── compare_skill/      # 多股票对比插件
│   └── role_play_skill/    # 多角色 LLM 评论插件
├── roles/                  # 投资角色 YAML 卡片
├── prompts/                # LLM Prompt 模板（Jinja2）
└── cache/                  # JSON 缓存文件
```
