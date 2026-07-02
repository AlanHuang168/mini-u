mini-uzi-teach/
├── main.py                    # 入口（聚合所有子 Skill）
├── SKILL.md                   # Skill 身份证
├── .env
├── requirements.txt
├── cache/                     # 缓存
├── reports/                   # 报告
├── prompts/                   # Prompt 模板
├── rules/                     # 规则引擎
│   ├── __init__.py
│   └── scoring.py
├── skills/                    # 子 Skill 目录
│   ├── analysis_skill/
│   │   ├── __init__.py
│   │   └── analyze.py
│   ├── role_play_skill/
│   │   ├── __init__.py
│   │   └── role_play.py
│   └── compare_skill/
│       ├── __init__.py
│       └── compare.py
└── pipeline/                  # Pipeline 协调层（可选）
    ├── __init__.py
    └── pipeline.py


阶段,目标,要增加的技术点,难度,教学价值
阶段1,理解 Pipeline,把代码拆成 collect → analyze → render,低,最高
阶段2,理解规则 vs LLM,把规则引擎和 LLM 明确分开成模块,中,很高
阶段3,理解报告生成,做出更接近 UZI 的自包含 HTML 报告,中,高
阶段4,理解缓存与鲁棒性,增加简单缓存 + fallback,中,实用
阶段5,理解 Skill 结构,加上 SKILL.md + 多命令支持,中高,架构思维


创建虚拟环境：
python -m venv .venv

# Mac/Linux 激活
source .venv/bin/activate

# Windows 激活
# .venv\Scripts\activate

# 安装依赖（使用国内镜像加速）
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

streamlit run main.py

# 用 venv 里的 pip 明确安装
# 先升级 pip
./.venv/bin/python -m pip install --upgrade pip

# 再安装依赖
./.venv/bin/python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 验证是否安装成功
./.venv/bin/python -c "import openai; print('openai 版本:', openai.__version__)"
./.venv/bin/python -c "import streamlit; print('streamlit 版本:', streamlit.__version__)"

# 用 venv 的 Python 运行 Streamlit
./.venv/bin/python -m streamlit run main.py