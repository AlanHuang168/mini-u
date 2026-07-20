# pipeline/collect.py
import akshare as ak
from datetime import datetime
from rules.scoring import calculate_score

MOCK_DATA = {
    "600519": {"name": "贵州茅台", "price": 1190.96, "change": "+0.85%"},
    "000333": {"name": "美的集团", "price": 58.32,   "change": "+1.20%"},
    "000001": {"name": "平安银行", "price": 11.45,   "change": "-0.35%"},
}

def collect_data(ticker: str, use_mock: bool = False):
    """真实数据采集 + 优雅 fallback"""
    print(f"[Pipeline] Step 1 - 开始采集 {ticker} 数据...")

    mock = MOCK_DATA.get(ticker, {"name": f"股票{ticker}", "price": 100.0, "change": "0.00%"})
    data = {
        "ticker": ticker,
        "name": mock["name"],
        "price": mock["price"],
        "change": mock["change"],
        "score": 56,
        "basic": "品牌护城河强，ROE 稳定",
        "risk": "当前估值偏高，市场情绪分歧",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "suggestion": "观望"
    }

    if not use_mock:
        try:
            stock_info = ak.stock_info_a_code_name()
            match = stock_info[stock_info['code'] == ticker.zfill(6)]
            if not match.empty:
                data["name"] = match['name'].iloc[0]

            df = ak.stock_zh_a_hist(symbol=ticker.zfill(6), period="daily", adjust="qfq")
            if not df.empty:
                latest = df.iloc[-1]
                data["price"] = round(float(latest['收盘']), 2)
                data["change"] = f"{latest['涨跌幅']:.2f}%"

            print(f"[Pipeline] ✅ 数据采集成功: {data['name']}")

        except Exception as e:
            print(f"[Pipeline] ⚠️ akshare 抓取失败: {e}，使用 Mock 数据")
    else:
        print(f"[Pipeline] 演示模式: 使用 Mock 数据 {data['name']}")

    scoring_result = calculate_score(data)
    data.update(scoring_result)

    return data