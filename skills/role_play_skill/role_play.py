# pipeline/role_play.py
import yaml
from pathlib import Path
from openai import OpenAI
import os


def get_role_comment(ticker: str, data: dict, role_name: str) -> str:
    """让 LLM 模拟特定角色评论"""

    role_file = Path(f"roles/{role_name.lower()}.yaml")
    if not role_file.exists():
        return f"角色 {role_name} 的卡片不存在"

    with open(role_file, "r", encoding="utf-8") as f:
        role = yaml.safe_load(f)

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return f"演示模式：未配置 DEEPSEEK_API_KEY，已跳过 {role_name} 角色 LLM 点评。"

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )

    prompt = f"""{role['prompt']}
股票：{ticker}
当前数据：{data}

请用第一人称、以你的投资风格给出简短评论（100-150字）。"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content