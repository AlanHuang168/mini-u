# pipeline/render.py
from datetime import datetime

def generate_report(data_list: list, analyses: list) -> str:
    """高级美化报告"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>量化分析员报告</title>
        <style>
            body {{ font-family: system-ui, sans-serif; background: #f8fafc; padding: 20px; margin: 0; }}
            .container {{ max-width: 1100px; margin: 0 auto; background: white; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); overflow: hidden; }}
            .header {{ background: linear-gradient(135deg, #0891b2, #1e3a8a); color: white; padding: 30px; text-align: center; }}
            .card {{ background: #f8fafc; padding: 24px; margin: 16px 0; border-radius: 12px; border-left: 5px solid #10b981; }}
            .risk {{ border-left-color: #ef4444; background: #fef2f2; }}
            .analysis {{ line-height: 1.8; font-size: 16px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>量化分析员报告</h1>
                <p>Pipeline 教学版 · {timestamp}</p>
            </div>
            <div style="padding:40px">
    """

    for i, (data, analysis) in enumerate(zip(data_list, analyses)):
        html += f"""
        <div class="card">
            <h2>{data.get('name', '未知')} ({data['ticker']})</h2>
            <p><strong>价格</strong> ≈ {data.get('price', 'N/A')} 元 | 
               <strong>涨跌</strong> {data.get('change', 'N/A')} | 
               <strong>评分</strong> {data.get('score', 'N/A')} 分</p>
            <div class="analysis">{analysis}</div>
        </div>
        """

    html += """
            </div>
            <div style="text-align:center;padding:30px;color:#64748b;font-size:13px;border-top:1px solid #e2e8f0">
                本报告用于教学演示 · 数据来源于 akshare + DeepSeek
            </div>
        </div>
    </body>
    </html>
    """
    return html