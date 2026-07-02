# pipeline/analyze.py
from openai import OpenAI
from jinja2 import Template
import json
import os
from dotenv import load_dotenv

from pipeline.cache import load_cache, save_cache



load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

def analyze_with_llm(data: dict) -> str:
    ticker = data['ticker']
    
    # 检查 LLM 缓存
    cached = load_cache(ticker, mode="llm")
    if cached:
        return cached
    
    """LLM 只负责解读规则引擎的结果"""
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
    #return response.choices[0].message.content
    # 保存 LLM 结果
    analysis = response.choices[0].message.content
    save_cache(ticker, analysis, mode="llm")
    return analysis