# pipeline/collect.py
import akshare as ak
from datetime import datetime
from rules.scoring import calculate_score
 
def calculate_basic_score(data: dict) -> int:
    """简单规则打分"""
    score = 50
    if data.get("price", 0) and float(data.get("price", 0)) > 1000:
        score += 10
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

def collect_data(ticker: str):
    """真实数据采集 + 优雅 fallback"""
    print(f"[Pipeline] Step 1 - 开始采集 {ticker} 数据...")
    
    data = {
        "ticker": ticker,
        "name": "未知股票",
        "price": "数据暂不可用",
        "change": "N/A",
        "score": 56,
        "basic": "品牌护城河强，ROE 稳定",
        "risk": "当前估值偏高，市场情绪分歧",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "suggestion": "观望"
    }
    
    try:
        # 尝试获取股票名称
        stock_info = ak.stock_info_a_code_name()
        match = stock_info[stock_info['code'] == ticker.zfill(6)]
        if not match.empty:
            data["name"] = match['name'].iloc[0]
        
        # 尝试获取最新行情
        df = ak.stock_zh_a_hist(symbol=ticker.zfill(6), period="daily", adjust="qfq")
        if not df.empty:
            latest = df.iloc[-1]
            data["price"] = round(float(latest['收盘']), 2)
            data["change"] = f"{latest['涨跌幅']:.2f}%"
        
        # 规则打分
        data["score"] = calculate_basic_score(data)
        data["suggestion"] = get_investment_suggestion(data["score"])
        
        print(f"[Pipeline] ✅ 数据采集成功: {data['name']}")
        
    except Exception as e:
        print(f"[Pipeline] ⚠️ akshare 抓取失败: {e}，使用 Mock 数据")
        if ticker == "600519":
            data["name"] = "贵州茅台"
            data["price"] = 1190.96
            data["change"] = "+0.85%"
            data["score"] = 56
            data["suggestion"] = "观望"
    
        # 调用规则引擎
   
    scoring_result = calculate_score(data)
    data.update(scoring_result)
    
    
    return data