import yaml
from pathlib import Path

def safe_float(value, default=0):
    """安全转 float"""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

def load_rules():
    """加载规则配置"""
    config_path = Path("rules/config/rules.yaml")
    if not config_path.exists():
        # 默认规则
        return [
            {"id": "price_high", "condition": "price > 1000", "score_delta": 15},
            {"id": "positive_change", "condition": "change > 0", "score_delta": 10}
        ]
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["rules"]

def evaluate_condition(condition: str, data: dict) -> bool:
    """简单条件评估"""
    try:
        if ">" in condition:
            key, value = condition.split(">")
            return safe_float(data.get(key.strip(), 0)) > safe_float(value.strip())
        elif "<" in condition:
            key, value = condition.split("<")
            return safe_float(data.get(key.strip(), 0)) < safe_float(value.strip())
    except:
        pass
    return False

def calculate_score(data: dict) -> dict:
    """规则引擎主函数"""
    rules = load_rules()
    score = 50  # 基础分
    
    applied = []
    
    for rule in rules:
        try:
            if evaluate_condition(rule["condition"], data):
                delta = rule.get("score_delta", 0)
                score += delta
                applied.append(rule["id"])
        except:
            pass  # 规则失败不影响整体
    
    final_score = min(100, max(0, score))
    
    return {
        "score": final_score,
        "suggestion": get_suggestion(final_score),
        "level": get_level(final_score),
        "applied_rules": applied
    }

def get_suggestion(score: int) -> str:
    if score >= 80:
        return "强烈推荐"
    elif score >= 65:
        return "推荐"
    elif score >= 50:
        return "观望"
    else:
        return "回避"

def get_level(score: int) -> str:
    if score >= 80:
        return "优秀"
    elif score >= 65:
        return "良好"
    elif score >= 50:
        return "中等"
    else:
        return "较弱"