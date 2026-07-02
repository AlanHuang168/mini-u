# rules/basic_rules.py
def calculate_basic_score(data: dict) -> int:
    """简单规则打分示例"""
    score = 50  # 基础分
    # 示例规则
    if data.get("price", 0) > 1000:
        score += 10
    # 可以继续加更多规则...
    return min(100, max(0, score))

def get_investment_suggestion(score: int) -> str:
    """根据评分给出建议"""
    if score >= 80:
        return "强烈推荐"
    elif score >= 65:
        return "推荐"
    elif score >= 50:
        return "观望"
    else:
        return "回避"