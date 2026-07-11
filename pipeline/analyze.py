# pipeline/analyze.py
from openai import OpenAI
from jinja2 import Template
import json
import os
from dotenv import load_dotenv

from pipeline.cache import load_cache, save_cache

load_dotenv()


def analyze_with_llm(data: dict, api_key: str = None) -> str:
    ticker = data["ticker"]

    cached = load_cache(ticker, mode="llm")
    if cached:
        return cached

    api_key = api_key or os.getenv("DEEPSEEK_API_KEY")

    if not api_key:
        return f"""
### 演示模式分析：{data.get('name', data['ticker'])} ({data['ticker']})

当前 Hugging Face Space 未配置 `DEEPSEEK_API_KEY`，所以已跳过真实 DeepSeek 调用。

这是一个 Mini-UZI Pipeline 教学版演示结果：

- 数据采集：已完成
- 规则引擎：已完成
- LLM 分析：演示模式
- 报告生成：可继续执行

如需启用真实 AI 分析，请在 Space Settings → Secrets 中配置 `DEEPSEEK_API_KEY`。
"""

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )

    with open("prompts/analyst_prompt.txt", "r", encoding="utf-8") as f:
        template = Template(f.read())

    prompt = template.render(
        ticker=f"{data.get('name', data['ticker'])} ({data['ticker']})",
        data=json.dumps(data, ensure_ascii=False, indent=2)
    )

    print("[Pipeline] Step 2 - 调用 DeepSeek 分析规则引擎输出...")

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        max_tokens=800
    )

    analysis = response.choices[0].message.content
    save_cache(ticker, analysis, mode="llm")
    return analysis