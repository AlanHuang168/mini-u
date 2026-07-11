import streamlit as st
from dotenv import load_dotenv
import os
from datetime import datetime

# Pipeline 核心模块
from pipeline.collect import collect_data
from pipeline.analyze import analyze_with_llm
from pipeline.render import generate_report

# 子 Skill 模块
from skills.role_play_skill.role_play import get_role_comment
from skills.compare_skill.compare import compare_stocks

load_dotenv()

st.title("量化分析员 - Pipeline 教学版")
st.caption("规则引擎 + DeepSeek 混合模式")

# 用 session_state 保存 Key（每个浏览器会话独立，不污染进程环境变量）
if "deepseek_key" not in st.session_state:
    st.session_state.deepseek_key = ""

deepseek_key = st.text_input("DeepSeek API Key (可选)", type="password", value=st.session_state.deepseek_key)

if deepseek_key:
    st.session_state.deepseek_key = deepseek_key

# 优先用用户本次输入的 key，其次用服务器配置的环境变量（HuggingFace Secrets）
effective_key = st.session_state.deepseek_key or os.getenv("DEEPSEEK_API_KEY", "")

ticker_input = st.text_input("股票代码（支持多个，用逗号分隔）", "600519, 000333")

if st.button("🚀 开始分析"):
    if not effective_key:
        st.error("请先输入 DeepSeek API Key")
    else:
        tickers = [t.strip() for t in ticker_input.split(",") if t.strip()]

        status_text = st.empty()

        if len(tickers) > 1:
            status_text.info("使用多股票对比模式...")
            report_html = compare_stocks(tickers, api_key=effective_key)
            st.success("✅ 多股票对比完成！")
        else:
            status_text.info(f"Step 1: 采集 {tickers[0]} 数据...")
            data = collect_data(tickers[0])
            data_list = [data]

            status_text.info("Step 2: DeepSeek 分析...")
            analysis = analyze_with_llm(data, api_key=effective_key)
            analysis_list = [analysis]

            status_text.info("Step 3: 生成报告...")
            report_html = generate_report(data_list, analysis_list)
            st.success("✅ 单股票分析完成！")

        st.html(report_html)

        # 多角色评论
        st.subheader("👥 多角色评论员观点")
        roles = ["buffett", "zhaolaoge", "mutoujie", "chenxiaoqun"]

        for i, ticker in enumerate(tickers):
            current_data = data_list[i] if 'data_list' in locals() and i < len(data_list) else {"name": ticker, "ticker": ticker}
            name = current_data.get('name', ticker)
            st.write(f"### {name} ({ticker})")
            for role in roles:
                comment = get_role_comment(ticker, current_data, role, api_key=effective_key)
                st.write(f"**{role.title()} 观点**：{comment}")
                st.divider()
        
        # 保存
        os.makedirs("reports", exist_ok=True)
        filename = f"reports/{'-'.join(tickers)}_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report_html)
        st.success(f"报告已保存: {filename}")