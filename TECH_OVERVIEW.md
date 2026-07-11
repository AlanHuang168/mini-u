# Mini-U 量化分析员 · 技术教学讲义

> 一个用 **150 行核心代码** 讲清楚「**规则引擎 + LLM 混合架构**」的完整教学项目。
> 本文档按「一节 ≈ 一组幻灯片」组织，可直接拆分成 PPT。
>
> 在线体验：HuggingFace Space `dayahs/mini-u` ｜ 技术栈：Python + Streamlit + DeepSeek + akshare

---

## 目录

1. [项目定位：它到底解决什么问题](#1-项目定位)
2. [系统架构总览](#2-系统架构总览)
3. [技术栈一览](#3-技术栈一览)
4. [核心技术点（逐个拆解）](#4-核心技术点)
   - 4.1 Pipeline 三段式架构
   - 4.2 规则引擎：配置驱动打分
   - 4.3 规则引擎 + LLM 混合（本项目灵魂）
   - 4.4 Prompt 工程：模板 + 角色卡
   - 4.5 多角色 Role-Play
   - 4.6 Skill 模块化架构
   - 4.7 缓存机制：省钱又提速
   - 4.8 优雅降级与容错
5. [端到端数据流转](#5-端到端数据流转)
6. [工程实战踩坑复盘（高价值教学素材）](#6-工程实战踩坑复盘)
7. [可扩展方向与课后练习](#7-可扩展方向与课后练习)
8. [附录：目录结构](#8-附录目录结构)

---

## 1. 项目定位

### 一句话
输入股票代码 → 系统自动「采集数据 + 规则打分 + AI 深度分析 + 多角色点评」→ 输出一份美观的 HTML 分析报告。

### 为什么值得学
这是一个 **麻雀虽小五脏俱全** 的 AI 应用范本，涵盖了一个真实 LLM 产品的所有关键环节：

| 环节 | 真实产品里对应什么 |
|------|-------------------|
| 数据采集 | 接入外部数据源 / API |
| 规则引擎 | 可解释、可审计的确定性逻辑 |
| LLM 分析 | 大模型能力的接入与封装 |
| Prompt 模板 | Prompt 工程与版本管理 |
| 缓存 | 降本增效、限流保护 |
| 多角色 | 多 Agent / 多视角设计 |
| 报告生成 | 结果的结构化呈现 |

> **教学核心观点**：LLM 应用不是「把问题丢给大模型」，而是**用工程手段把 LLM 编排进一条可控的流水线**。

---

## 2. 系统架构总览

### 分层架构图

```
┌─────────────────────────────────────────────────┐
│                UI 层  (Streamlit)                │
│   streamlit_app.py  ← HuggingFace 入口           │
│   · 输入股票代码 / API Key                       │
│   · 展示报告 + 多角色评论                        │
└───────────────────────┬─────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────┐
│              Skill 层  (可插拔功能包)             │
│   analysis_skill   单股票完整分析                 │
│   compare_skill    多股票对比                     │
│   role_play_skill  多角色评论                     │
└───────────────────────┬─────────────────────────┘
                        │  组合调用
┌───────────────────────▼─────────────────────────┐
│           Pipeline 层  (三段式核心流水线)         │
│   collect.py  →  analyze.py  →  render.py        │
│   采集+打分       LLM 分析        生成报告        │
└──────┬──────────────┬───────────────┬────────────┘
       │              │               │
┌──────▼──────┐ ┌─────▼──────┐ ┌──────▼───────┐
│  规则引擎    │ │  缓存层     │ │ Prompt 模板  │
│ rules/       │ │ cache.py    │ │ prompts/     │
│ scoring.py   │ │ (JSON+TTL)  │ │ roles/*.yaml │
└─────────────┘ └────────────┘ └──────────────┘
       │
┌──────▼──────┐
│ 外部数据源   │
│ akshare (A股)│
└─────────────┘
```

### 三层职责

- **UI 层**：只负责交互与展示，不含业务逻辑。
- **Skill 层**：把 Pipeline 组合成「用户能理解的功能」，可自由增删。
- **Pipeline 层**：真正干活的三段式流水线，是整个系统的骨架。

> **教学点**：分层的本质是「变化隔离」——换 UI 不影响 Pipeline，换数据源不影响报告生成。

---

## 3. 技术栈一览

| 分类 | 技术 | 作用 |
|------|------|------|
| Web UI | **Streamlit** | 纯 Python 写交互式 Web 应用，零前端代码 |
| 大模型 | **DeepSeek** | 生成分析文本（用 OpenAI SDK 调用，兼容协议） |
| 数据源 | **akshare** | 免费 A 股行情数据 |
| 模板引擎 | **Jinja2** | Prompt 动态渲染 |
| 配置格式 | **YAML** | 规则配置、角色人设卡 |
| 缓存 | **JSON 文件** | 本地持久化缓存 |
| 部署 | **HuggingFace Spaces** | 免费托管 Streamlit 应用 |

> **教学点**：DeepSeek 兼容 OpenAI 协议，所以直接用 `openai` 库、改一个 `base_url` 就能调用——这是当前国产大模型的普遍做法，学会一套 SDK 走天下。

```python
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"   # ← 只改这一行
)
```

---

## 4. 核心技术点

### 4.1 Pipeline 三段式架构

整个系统的骨架就是三个函数，用一个 `data` 字典串起来：

```python
# streamlit_app.py 核心 3 行
data     = collect_data(ticker)                 # Step 1 采集 + 规则打分
analysis = analyze_with_llm(data, api_key=key)  # Step 2 LLM 分析
report   = generate_report([data], [analysis])  # Step 3 生成报告
```

| 步骤 | 文件 | 输入 → 输出 | 干什么 |
|------|------|------------|--------|
| Step 1 | `collect.py` | 股票代码 → data 字典 | 抓行情 + 规则打分 |
| Step 2 | `analyze.py` | data → 分析文本 | 调 DeepSeek 生成分析 |
| Step 3 | `render.py` | data + 分析 → HTML | 拼装美化报告 |

> **教学点：为什么用 Pipeline？**
> - **单一职责**：每步只做一件事，好测试、好替换。
> - **可组合**：Skill 层就是把这三步重新排列组合。
> - **易调试**：出错时一眼定位在哪一步（日志里 `Step 1/2/3` 清晰可见）。

---

### 4.2 规则引擎：配置驱动打分

规则**不写死在代码里**，而是放在 `rules/config/rules.yaml`：

```yaml
rules:
  - id: price_high         # 高价股加分
    condition: price > 1000
    score_delta: 15
  - id: positive_change    # 上涨加分
    condition: change > 0
    score_delta: 10
  - id: high_roe           # 高 ROE 加分
    condition: roe > 20
    score_delta: 20
```

引擎读取配置，逐条判断，累加分数：

```python
def calculate_score(data: dict) -> dict:
    rules = load_rules()          # 从 YAML 加载
    score = 50                    # 基础分
    applied = []
    for rule in rules:
        if evaluate_condition(rule["condition"], data):
            score += rule["score_delta"]
            applied.append(rule["id"])
    final = min(100, max(0, score))   # 夹在 0~100
    return {"score": final, "suggestion": get_suggestion(final),
            "level": get_level(final), "applied_rules": applied}
```

`evaluate_condition` 是一个极简条件解析器（把 `"price > 1000"` 变成真假判断）：

```python
def evaluate_condition(condition: str, data: dict) -> bool:
    if ">" in condition:
        key, value = condition.split(">")
        return safe_float(data.get(key.strip(), 0)) > safe_float(value.strip())
    # < 同理...
```

> **教学点：为什么要配置驱动？**
> - 改规则不用改代码、不用重新部署，运营/产品也能维护。
> - `applied_rules` 记录了「命中了哪些规则」→ **可解释性**，这正是 LLM 缺乏而规则引擎擅长的。

---

### 4.3 规则引擎 + LLM 混合（本项目灵魂）

这是整个项目**最值得讲的设计思想**：

```
       结构化、确定性              自然语言、灵活性
     ┌──────────────┐          ┌──────────────┐
     │   规则引擎    │  ──数据──▶│  DeepSeek    │
     │  算分/评级    │          │  解读/叙述   │
     └──────────────┘          └──────────────┘
       可解释、可审计            会说人话、有洞察
       但呆板                    但不可控、会幻觉
```

- **规则引擎**负责「算」：算分数、给评级 → **可解释、可复现、零成本**。
- **LLM** 负责「说」：把冰冷的数字翻译成有逻辑的投资分析 → **可读、有洞察**。

关键代码：规则结果作为**上下文**喂给 LLM，LLM 只做解读不做计算：

```python
prompt = template.render(
    ticker=f"{data['name']} ({data['ticker']})",
    data=json.dumps(data, ensure_ascii=False, indent=2)  # ← 规则引擎的输出
)
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.6,      # 分析类任务，温度偏低求稳
    max_tokens=800
)
```

> **教学点（金句）**：
> **「让规则引擎做数学题，让大模型做作文题。」**
> 把确定性逻辑交给代码，把语言表达交给 LLM——这是设计可靠 AI 应用的核心原则，能有效降低幻觉、提升可控性。

---

### 4.4 Prompt 工程：模板 + 角色卡

Prompt **不硬编码在 Python 里**，而是独立成文件 `prompts/analyst_prompt.txt`，用 Jinja2 渲染变量：

```jinja2
你是一位经验丰富、风格严谨的首席股票分析师。
当前股票：{{ticker}}

请基于以下规则引擎输出数据，进行深度分析：
{{data}}

要求：
- 结构清晰：基本面分析 → 风险评估 → 投资逻辑 → 最终建议
- 突出数据支撑（引用具体数字）
- 长度控制在 250-400 字
- 最后给出明确的投资评级（强烈推荐 / 推荐 / 观望 / 谨慎 / 回避）
```

> **教学点：Prompt 为什么要独立成文件？**
> - **可维护**：改 Prompt 不动代码，非技术人员也能调。
> - **可版本管理**：Prompt 是 AI 应用的「源代码」，值得进 git 独立追踪。
> - **模板变量**：`{{ticker}}`、`{{data}}` 让同一个 Prompt 适配所有股票。
> - **框定输出**：明确要求「结构、字数、评级选项」是控制 LLM 输出质量的关键技巧。

---

### 4.5 多角色 Role-Play

同一只股票，让 LLM **扮演不同投资风格的人**分别点评。每个角色是一张 YAML「人设卡」：

```yaml
# roles/buffett.yaml
name: 巴菲特
style: 价值投资
focus: 护城河、ROE、安全边际
prompt: "你是以长期价值投资闻名的巴菲特。请从护城河、ROE、安全边际角度分析这只股票。"
```

目前内置 4 个角色，风格迥异：

| 角色 | 风格 | 关注点 |
|------|------|--------|
| 巴菲特 | 价值投资 | 护城河、ROE、安全边际 |
| 赵老哥 | 游资短线 | 龙虎榜、板块热度、情绪 |
| 木头姐 | 成长创新 | 创新、增长潜力、颠覆性 |
| 陈小群 | 宏观策略 | 宏观经济、政策、行业周期 |

加载角色卡 + 拼 Prompt + 调用 LLM：

```python
def get_role_comment(ticker, data, role_name, api_key=None):
    role = yaml.safe_load(open(f"roles/{role_name}.yaml"))
    prompt = f"""{role['prompt']}
股票：{ticker}
当前数据：{data}
请用第一人称、以你的投资风格给出简短评论（100-150字）。"""
    # 调用 DeepSeek，temperature=0.7（点评类任务，温度偏高求多样）
```

> **教学点：**
> - **数据与逻辑分离**：加一个新角色只需加一个 YAML 文件，**零代码改动**。
> - **温度调参**：分析报告 `temperature=0.6`（求稳），角色点评 `0.7`（求个性）——**同一个模型，不同任务用不同温度**。
> - 这就是「多 Agent / 多视角」思想的最小实现。

---

### 4.6 Skill 模块化架构

`skills/` 下每个子目录是一个**独立功能包**，通过组合 Pipeline 实现不同能力：

```
skills/
├── analysis_skill/    单股票完整分析
├── compare_skill/     多股票对比
└── role_play_skill/   多角色评论
```

比如「多股票对比」就是循环调用 Pipeline：

```python
def compare_stocks(tickers, api_key=None, use_mock=False):
    data_list, analysis_list = [], []
    for ticker in tickers:
        data = collect_data(ticker, use_mock=use_mock)      # 复用 Step 1
        analysis = analyze_with_llm(data, api_key=api_key)  # 复用 Step 2
        data_list.append(data); analysis_list.append(analysis)
    return generate_report(data_list, analysis_list)        # 复用 Step 3
```

> **教学点**：Skill = 「乐高积木」。Pipeline 是基础积木块，Skill 是用积木拼出的成品。新功能 = 新拼法，底层零改动。

---

### 4.7 缓存机制：省钱又提速

LLM 调用**要花钱、要等待**。同一只股票短时间内重复分析没必要再调一次，用文件缓存挡住：

```python
def analyze_with_llm(data, api_key=None):
    cached = load_cache(ticker, mode="llm")   # ① 先查缓存
    if cached:
        return cached                          # ② 命中直接返回，不调 LLM
    # ③ 未命中才真正调用 DeepSeek...
    save_cache(ticker, analysis, mode="llm")   # ④ 存缓存
```

缓存文件带**时间戳 + TTL 过期**逻辑（默认 6 小时）：

```python
def load_cache(ticker, mode="full", expire_hours=6):
    cache = json.load(open(cache_file))
    cached_time = datetime.fromisoformat(cache["timestamp"])
    if datetime.now() - cached_time < timedelta(hours=expire_hours):
        return cache["data"]   # 未过期才用
    return None
```

缓存文件长这样（`cache/600519_llm.json`）：

```json
{
  "timestamp": "2026-07-02T16:26:35.760894",
  "data": "### 贵州茅台（600519）深度分析报告 ..."
}
```

> **教学点：缓存三要素**
> 1. **Key 设计**：`{股票代码}_{模式}` 唯一标识一份缓存。
> 2. **TTL 过期**：行情会变，缓存不能永久有效 → 用时间戳判断新鲜度。
> 3. **降本增效**：缓存命中 = 省一次 API 费用 + 秒级响应。这是所有 LLM 应用的标配优化。

---

### 4.8 优雅降级与容错

真实系统一定会遇到「外部依赖挂掉」，本项目处处做了 **fallback（兜底）**：

| 故障场景 | 兜底策略 | 效果 |
|----------|----------|------|
| akshare 抓取失败 | 用内置 Mock 数据 | 不崩溃，照样出报告 |
| 没配 API Key | 返回「演示模式」文案 | 不报错，提示怎么配置 |
| 角色卡文件不存在 | 返回「角色不存在」提示 | 优雅提示而非抛异常 |
| 规则条件解析失败 | `try/except` 跳过该规则 | 单条规则错误不影响整体 |

```python
try:
    df = ak.stock_zh_a_hist(symbol=ticker)   # 尝试真实数据
    ...
except Exception as e:
    print(f"⚠️ akshare 抓取失败: {e}，使用 Mock 数据")   # 兜底
```

> **教学点**：**「Fail Gracefully（优雅失败）」**——好的系统不是「不出错」，而是「出错时也能给用户一个合理的结果」。演示 / 教学场景尤其需要，不能因为一个网络波动就白屏。

---

## 5. 端到端数据流转

以「分析贵州茅台 600519」为例，追踪一次完整请求：

```
用户输入 "600519" + API Key
   │
   ▼ Step 1  collect_data("600519")
   ├─ akshare 抓行情  →  {name:"贵州茅台", price:1190.96, change:"+0.85%"}
   ├─ 规则引擎 calculate_score()
   │    · price>1000 命中 → +15
   │    · change>0   命中 → +10
   │    → score:65, level:"良好", suggestion:"推荐"
   ▼
   data 字典（结构化数据）
   │
   ▼ Step 2  analyze_with_llm(data)
   ├─ 查缓存 → 未命中
   ├─ Jinja2 渲染 Prompt（塞入 data）
   ├─ 调 DeepSeek(temperature=0.6) → 生成 250-400 字分析
   ├─ 存缓存
   ▼
   analysis 文本（自然语言）
   │
   ▼ Step 3  generate_report([data],[analysis])
   └─ 拼装成带 CSS 样式的 HTML
   │
   ▼ 多角色循环 get_role_comment() × 4
   └─ 巴菲特 / 赵老哥 / 木头姐 / 陈小群 各自点评
   │
   ▼ st.html(report) 展示 + 保存到 reports/*.html
```

> **教学点**：注意数据形态的转变——**「结构化数据(dict) → 自然语言(text) → 呈现(HTML)」**，这是几乎所有 LLM 应用的通用数据流。

---

## 6. 工程实战踩坑复盘

> 本节是**最真实、最有教学价值**的部分——这些都是本项目开发部署中真实踩过的坑。

### 坑 1：API Key 安全 —— `os.environ` vs `session_state`

**❌ 错误写法**（会导致 Key 跨用户泄露）：
```python
os.environ["DEEPSEEK_API_KEY"] = user_input   # 写进程环境变量 → 所有用户共享！
value = os.getenv("DEEPSEEK_API_KEY", "")      # 下次 rerun 回填 → 别人看得到
```

**✅ 正确写法**（会话级隔离）：
```python
if "deepseek_key" not in st.session_state:
    st.session_state.deepseek_key = ""
# 每个浏览器会话独立，互不干扰
effective_key = st.session_state.deepseek_key
# Key 通过函数参数显式传递，不污染全局
analyze_with_llm(data, api_key=effective_key)
```

> **教学点（安全红线）**：
> 多用户 Web 应用里，敏感信息只能存**会话级**（`session_state`），**绝不能**存进程级（`os.environ`）。
> `os.environ` 是**整个进程共享**的——用户 A 写进去，用户 B 就读得到。

### 坑 2：mini-racer / V8 在 macOS 子线程 segfault

**现象**：同一份代码，HuggingFace(Linux) 正常，命令行直跑正常，但本地 `streamlit run` 一采集数据就 `segmentation fault`。

**根因**：
- akshare 底层用 `mini-racer`（Google V8 JS 引擎）解析数据。
- Streamlit 把脚本跑在**子线程**（ScriptRunner thread）里。
- **V8 引擎在 macOS 上被子线程初始化时会崩溃**（C 层 segfault，Python 的 `try/except` 拦不住）。

**排查方法**（教学价值）：用「二分法 + 独立复现」定位——把可疑调用单独拎出来跑，看退出码：
```bash
python -c "import akshare as ak; ak.stock_zh_a_hist(symbol='600519')"  # 命令行：正常
# 但同样代码在 streamlit 子线程里 → segfault
# → 结论：不是代码 bug，是 V8 + 子线程 + macOS 的底层缺陷
```

**解法**：加「演示模式」开关，跳过 akshare 直接用 Mock 数据。

> **教学点**：
> - **`segmentation fault` ≠ Python 异常**，是 C 扩展层崩溃，`try/except` 捕获不了。
> - 「环境 A 好、环境 B 崩」时，要对比**三个变量**：操作系统、Python 版本、运行方式（主线程 vs 子线程）。

### 坑 3：依赖没写全 —— `ModuleNotFoundError: yaml`

代码 `import yaml`，但 `requirements.txt` 里漏了 `PyYAML`。HuggingFace 的镜像恰好预装了，本地干净 venv 就报错。

> **教学点**：**依赖必须显式声明**，不能依赖「运行环境碰巧装了」。判断标准：在一个全新的空环境里 `pip install -r requirements.txt` 能否跑起来。

### 坑 4：虚拟环境误提交 git

`git add .` 会把 `.venv/` 也加进去。虚拟环境**体积大、含平台相关二进制、可重建**，绝不该进 git。

**解法**：`.gitignore` 加 `.venv*/`（用通配符覆盖 `.venv`、`.venv311` 等所有变体）。

> **教学点**：虚拟环境靠 `requirements.txt` 一键重建，永远不进版本库。同理还有 `__pycache__/`、`.env`（含密钥）、`node_modules/`。

---

## 7. 可扩展方向与课后练习

留给学员的动手题（由易到难）：

| 难度 | 练习 | 涉及知识点 |
|------|------|-----------|
| ⭐ | 新增一个投资角色（如「量化派」） | 加一个 `roles/*.yaml`，体会数据驱动 |
| ⭐ | 在 `rules.yaml` 加一条新规则 | 配置驱动的规则引擎 |
| ⭐⭐ | 把缓存过期时间做成 UI 可调 | Streamlit 交互 + 参数传递 |
| ⭐⭐ | 给报告加一个「评分雷达图」 | 数据可视化（st.plotly_chart） |
| ⭐⭐⭐ | 把 JSON 文件缓存换成 Redis | 缓存后端抽象、接口设计 |
| ⭐⭐⭐ | 把 DeepSeek 换成其他大模型 | LLM 供应商抽象、OpenAI 兼容协议 |
| ⭐⭐⭐ | 用子进程跑 akshare 修复 macOS segfault | 进程隔离、并发模型 |

---

## 8. 附录：目录结构

```
mini-u/
├── streamlit_app.py        # HuggingFace 入口（UI 层，与 main.py 内容一致）
├── main.py                 # 本地入口
├── SKILL.md                # 项目「身份证」（Skill 元信息）
├── requirements.txt        # 依赖声明
│
├── pipeline/               # ★ 核心三段式流水线
│   ├── collect.py          #   Step 1 数据采集 + 规则打分
│   ├── analyze.py          #   Step 2 DeepSeek LLM 分析
│   ├── render.py           #   Step 3 HTML 报告生成
│   └── cache.py            #   缓存（JSON + 6h TTL）
│
├── rules/                  # ★ 规则引擎
│   ├── scoring.py          #   引擎主逻辑 + 条件解析
│   ├── basic_rules.py      #   简单打分示例
│   └── config/rules.yaml   #   规则配置（可热改）
│
├── skills/                 # ★ 可插拔功能包
│   ├── analysis_skill/     #   单股票完整分析
│   ├── compare_skill/      #   多股票对比
│   └── role_play_skill/    #   多角色评论
│
├── roles/                  # 角色人设卡（YAML）
│   ├── buffett.yaml        #   巴菲特（价值投资）
│   ├── zhaolaoge.yaml      #   赵老哥（游资短线）
│   ├── mutoujie.yaml       #   木头姐（成长创新）
│   └── chenxiaoqun.yaml    #   陈小群（宏观策略）
│
├── prompts/                # Prompt 模板（Jinja2）
│   ├── analyst_prompt.txt  #   分析师 Prompt
│   └── summary_prompt.txt  #   总结 Prompt
│
├── cache/                  # 缓存文件（JSON）
└── reports/                # 生成的 HTML 报告
```

---

### 一页总结（可做收尾 PPT）

> **Mini-U 教会我们的 5 件事：**
> 1. **分层与流水线** —— 用 Pipeline 把复杂流程拆成单一职责的步骤。
> 2. **规则 + LLM 混合** —— 让代码算数、让大模型说话，各司其职。
> 3. **配置驱动** —— 规则、角色、Prompt 都外置成文件，改配置不改代码。
> 4. **工程化标配** —— 缓存降本、优雅降级、依赖声明、密钥隔离。
> 5. **真实的坑** —— 密钥安全、C 扩展崩溃、环境差异，都是宝贵的实战经验。
