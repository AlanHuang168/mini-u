# skills/analysis_skill/analyze.py
from pipeline.collect import collect_data
from pipeline.analyze import analyze_with_llm
from pipeline.render import generate_report

def run_analysis(ticker: str) -> str:
    data = collect_data(ticker)
    analysis = analyze_with_llm(data)
    return generate_report([data], [analysis])