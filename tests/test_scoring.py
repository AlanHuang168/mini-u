"""规则引擎单元测试：纯函数、不联网、不调用 LLM。"""

from rules.scoring import (
    safe_float,
    evaluate_condition,
    calculate_score,
    get_suggestion,
    get_level,
)


def test_safe_float_handles_bad_input():
    assert safe_float(3.5) == 3.5
    assert safe_float("12.3") == 12.3
    assert safe_float(None) == 0
    assert safe_float("not-a-number") == 0
    assert safe_float("1.2%", default=-1) == -1  # 带 % 的字符串无法直接转换


def test_evaluate_condition_greater_and_less():
    assert evaluate_condition("price > 1000", {"price": 2000}) is True
    assert evaluate_condition("price > 1000", {"price": 500}) is False
    assert evaluate_condition("roe < 10", {"roe": 5}) is True
    assert evaluate_condition("roe < 10", {"roe": 15}) is False
    # 缺失字段按默认 0 处理，不抛异常
    assert evaluate_condition("price > 1000", {}) is False


def test_get_suggestion_thresholds():
    assert get_suggestion(85) == "强烈推荐"
    assert get_suggestion(70) == "推荐"
    assert get_suggestion(55) == "观望"
    assert get_suggestion(30) == "回避"


def test_get_level_thresholds():
    assert get_level(85) == "优秀"
    assert get_level(70) == "良好"
    assert get_level(55) == "中等"
    assert get_level(30) == "较弱"


def test_calculate_score_base_line():
    """空数据 → 基础分 50 → 观望/中等，命中规则为空。"""
    result = calculate_score({})
    assert result["score"] == 50
    assert result["suggestion"] == "观望"
    assert result["level"] == "中等"
    assert result["applied_rules"] == []


def test_calculate_score_applies_rules():
    """高价 + 高 ROE 命中两条规则：50 + 15 + 20 = 85。"""
    result = calculate_score({"price": 2000, "roe": 25})
    assert result["score"] == 85
    assert result["suggestion"] == "强烈推荐"
    assert result["level"] == "优秀"
    assert "price_high" in result["applied_rules"]
    assert "high_roe" in result["applied_rules"]


def test_calculate_score_is_capped_at_100():
    """即使叠加多条加分，最终分也不超过 100。"""
    result = calculate_score({"price": 2000, "roe": 25, "change": 5})
    assert 0 <= result["score"] <= 100
