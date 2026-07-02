# skills/compare_skill/compare.py
from pipeline.collect import collect_data
from pipeline.analyze import analyze_with_llm
from pipeline.render import generate_report

def compare_stocks(tickers: list, progress_bar=None, status_text=None) -> str:
    """多股票对比（支持进度条）"""
    data_list = []
    analysis_list = []
    
    total = len(tickers)
    for i, ticker in enumerate(tickers):
        progress = (i / total) * 0.8   # 0.0 ~ 0.8
        
        if status_text:
            status_text.info(f"Step 1: 采集 {ticker} 数据...")
        if progress_bar:
            progress_bar.progress(progress)
        
        data = collect_data(ticker)
        data_list.append(data)
        
        if status_text:
            status_text.info(f"Step 2: DeepSeek 分析 {ticker}...")
        if progress_bar:
            progress_bar.progress(progress + 0.1)
        
        analysis = analyze_with_llm(data)
        analysis_list.append(analysis)
    
    if progress_bar:
        progress_bar.progress(0.9)
    
    return generate_report(data_list, analysis_list)