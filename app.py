import streamlit as st
import requests

st.set_page_config(page_title="Hệ Thống 50 Điểm (FMP Data)", layout="wide")

st.title("📈 Hệ Thống Chấm Điểm Đầu Tư Giá Trị (50-Point System)")
st.markdown("Hệ thống tự động tải báo cáo tài chính gốc từ FMP và tự động tính toán các chỉ số.")

# --- TẠO THANH CÔNG CỤ BÊN TRÁI ---
st.sidebar.header("🔍 Tải Dữ Liệu Tự Động")
ticker_input = st.sidebar.text_input("Nhập mã cổ phiếu Mỹ (VD: AAPL, MSFT)", value="AAPL")
api_key = st.sidebar.text_input("Nhập FMP API Key của bạn:", type="password")

if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.data = {}

if st.sidebar.button("🚀 Tải dữ liệu từ FMP"):
    if not api_key:
        st.sidebar.error("Vui lòng nhập API Key từ FMP!")
    else:
        with st.spinner(f"Đang tải báo cáo tài chính cho {ticker_input.upper()}..."):
            try:
                tk = ticker_input.upper()
                # Gọi 4 Endpoint cơ bản (Luôn miễn phí)
                url_profile = f"https://financialmodelingprep.com/api/v3/profile/{tk}?apikey={api_key}"
                url_is = f"https://financialmodelingprep.com/api/v3/income-statement/{tk}?limit=1&apikey={api_key}"
                url_bs = f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{tk}?limit=1&apikey={api_key}"
                url_cf = f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{tk}?limit=1&apikey={api_key}"
                
                res_prof = requests.get(url_profile).json()
                res_is = requests.get(url_is).json()
                res_bs = requests.get(url_bs).json()
                res_cf = requests.get(url_cf).json()
                
                if len(res_prof) > 0 and len(res_is) > 0 and len(res_bs) > 0 and len(res_cf) > 0:
                    prof = res_prof[0]
                    inc = res_is[0]
                    bal = res_bs[0]
                    cf = res_cf[0]
                    
                    # --- TỰ ĐỘNG TÍNH TOÁN BẰNG TOÁN HỌC ---
                    # Ngăn lỗi chia cho 0
                    liabilities = bal.get('totalCurrentLiabilities', 1) or 1
                    equity = bal.get('totalStockholdersEquity', 1) or 1
                    revenue = inc.get('revenue', 1) or 1
                    mcap = prof.get('mktCap', 1) or 1
                    
                    calc_current_ratio = bal.get('totalCurrentAssets', 0) / liabilities
                    calc_debt_equity = bal.get('totalDebt', 0) / equity
                    calc_gross_margin = (inc.get('grossProfit', 0) / revenue) * 100
                    calc_net_margin = (inc.get('netIncome', 0) / revenue) * 100
                    calc_roe = (inc.get('netIncome', 0) / equity) * 100
                    calc_fcf_yield = (cf.get('freeCashFlow', 0) / mcap) * 100
                    
                    # Lấy PE và Cổ tức
                    calc_pe = prof.get('pe', 20.0) # Có thể null
                    if not calc_pe: calc_pe = 20.0
                    
                    st.session_state.data = {
                        'current_ratio': calc_current_ratio,
                        'debt_equity': calc_debt_equity,
                        'gross_margin': calc_gross_margin,
                        'net_margin': calc_net_margin,
                        'roe': calc_roe,
                        'ttm_pe': calc_pe,
                        'fcf_yield': calc_fcf_yield,
                        'div_yield': 0.0 # Để an toàn, người dùng tự cộng cổ tức và mua lại cổ phiếu
                    }
                    st.session_state.data_loaded = True
                    st.sidebar.success("Tải & Tính toán thành công!")
                else:
                    st.sidebar.error("Không tìm thấy dữ liệu báo cáo cho mã này.")
            except Exception as e:
                st.sidebar.error(f"Lỗi hệ thống: {e}")

# Lấy dữ liệu từ session
d = st.session_state.data if st.session_state.data_loaded else {}

# --- GIAO DIỆN CHIA 3 TAB ---
tab1, tab2, tab3 = st.tabs(["🟢 Tier 1: Cơ Bản", "🔵 Tier 2: Tăng Trưởng", "🟣 Tier 3: Định Giá"])

with tab1:
    st.header("Hạng Mục 1: Các Yếu Tố Cơ Bản (Max 15 Pts)")
    st.caption("Dữ liệu tự động tính toán từ Báo cáo tài chính gốc (FMP).")
    col1, col2 = st.columns(2)
    
    with col1:
        current_ratio = st.number_input("Current Ratio", value=float(d.get('current_ratio', 1.0)))
        debt_equity = st.number_input("Debt to Equity", value=float(d.get('debt_equity', 0.5)))
        gross_margin = st.number_input("Gross Profit Margin (%)", value=float(d.get('gross_margin', 45.0)))
        net_margin = st.number_input("Net Profit Margin (%)", value=float(d.get('net_margin', 16.0)))
        roe = st.number_input("Return on Equity (ROE) (%)", value=float(d.get('roe', 20.0)))
        roc = st.number_input("Return on Capital (ROC) (%)", value=16.0) 
        shareholder_yield = st.number_input("Shareholder Yield (%) (Cổ tức + Mua lại)", value=float(d.get('div_yield', 3.5)))
        
    with col2:
        fcf_yield = st.number_input("FCF Yield (%)", value=float(d.get('fcf_yield', 4.0)))
        cash_vs_debt = st.selectbox("Tiền mặt so với Nợ ngắn hạn", ["Cash > ST Debt", "Cash <= ST Debt"])
        pref_stock = st.selectbox("Cổ phiếu ưu đãi", ["Không có", "Có"])
        re_trend = st.selectbox("Xu hướng Lợi nhuận (10 năm)", ["Tăng vững chắc", "Không rõ/Giảm"])
        intangibles = st.number_input("(Goodwill + Intangibles) / Total Assets", value=0.2)
        net_debt_ebitda = st.number_input("Net Debt / EBITDA", value=0.5)
        div_cagr_5y = st.number_input("5-Year Dividend CAGR (%)", value=5.0)

    # Tính điểm Tier 1
    t1_score = 0.0
    t1_score += 1.0 if current_ratio >= 1.5 else (0.5 if 1.0 <= current_ratio < 1.5 else 0)
    t1_score += 1.0 if debt_equity <= 0.8 else (0.5 if 0.8 < debt_equity <= 1.0 else 0)
    t1_score += 1.0 if gross_margin > 40 else (0.5 if 20 <= gross_margin <= 40 else 0)
    t1_score += 1.0 if net_margin > 15 else (0.5 if 10 <= net_margin <= 15 else 0)
    t1_score += 1.0 if roe >= 15 else (0.5 if 10 <= roe < 15 else 0)
    t1_score += 1.0 if roc >= 15 else (0.5 if 10 <= roc < 15 else 0)
    t1_score += 1.0 if shareholder_yield >= 3 else (0.5 if 1.5 <= shareholder_yield < 3 else 0)
    t1_score += 1.0 if fcf_yield >= 3 else 0
    t1_score += 1.0 if cash_vs_debt == "Cash > ST Debt" else 0
    t1_score += 1.0 if pref_stock == "Không có" else 0
    t1_score += 1.0 if re_trend == "Tăng vững chắc" else 0
    t1_score += 1.0 if intangibles <= 0.3 else 0
    t1_score += 1.0 if net_debt_ebitda <= 1 else (0.5 if 1 < net_debt_ebitda <= 3 else 0)
    t1_score += 2.0 if div_cagr_5y > 10 else (1.0 if 3 <= div_cagr_5y <= 10 else (0.5 if 0 < div_cagr_5y < 3 else 0))

with tab2:
    st.header("Hạng Mục 2: Chỉ Số Tăng Trưởng (Max 17.5 Pts)")
    rev_cagr = st.number_input("5-Year Revenue CAGR (%)", value=15.0)
    next_rev = st.number_input("Next-Year Forecast Revenue Growth (%)", value=18.0)
    fcf_cagr = st.number_input("5-Year FCF CAGR (%)", value=12.0)

    def score_growth(val, type_):
        if val >= 30: return 2.5 if type_=="rev5" else 5.0
        if val >= 25: return 2.25 if type_=="rev5" else 4.5
        if val >= 20: return 2.0 if type_=="rev5" else 4.0
        if val >= 14: return 1.75 if type_=="rev5" else 3.5
        if val >= 12: return 1.5 if type_=="rev5" else 3.0
        if val >= 10: return 1.25 if type_=="rev5" else 2.5
        if val >= 8: return 1.0 if type_=="rev5" else 2.0
        if val >= 6: return 0.75 if type_=="rev5" else 1.5
        if val >= 4: return 0.5 if type_=="rev5" else 1.0
        if val >= 2: return 0.25 if type_=="rev5" else 0.5
        return 0.0

    def score_fcf(val):
        if val >= 20: return 10.0
        if val >= 17: return 9.0
        if val >= 14: return 8.0
        if val >= 10: return 7.0
        if val >= 8: return 6.0
        if val >= 6: return 5.0
        if val >= 4: return 4.0
        if val >= 3: return 3.0
        if val >= 2: return 2.0
        if val >= 1: return 1.0
        return 0.0

    t2_score = score_growth(rev_cagr, "rev5") + score_growth(next_rev, "rev_next") + score_fcf(fcf_cagr)

with tab3:
    st.header("Hạng Mục 3: Định Giá (Max 17.5 Pts)")
    col_a, col_b = st.columns(2)
    
    with col_a:
        ni_cagr = st.number_input("5-Yr Net Income CAGR (%)", value=16.0)
        ttm_pe = st.number_input("P/E Ratio", value=float(d.get('ttm_pe', 22.0)))
        
    with col_b:
        eps_growth = st.number_input("Next-Yr EPS Growth (%)", value=22.0)
        fwd_pe = st.number_input("Forward P/E Ratio", value=19.0) 
        
    hist_pe_diff = st.selectbox("Current P/E vs 5-Yr Hist P/E", 
                                [">30% Discount", "20-30% Discount", "10-20% Discount", 
                                 "Fair Value (+/-10%)", "10-20% Premium", "20-30% Premium", ">30% Premium"])

    def get_ni_pe_score(cagr, pe):
        if pe > 100: return 0 
        if pe <= 25: col = 0
        elif pe <= 35: col = 1
        elif pe <= 45: col = 2
        elif pe <= 55: col = 3
        elif pe <= 70: col = 4
        elif pe <= 85: col = 5
        else: col = 6
        
        if cagr > 40: return [10, 9, 8.5, 8, 7, 6.5, 6][col]
        if cagr >= 30: return [9, 8.5, 8, 7, 6.5, 6, 5.5][col]
        if cagr >= 20: return [8.5, 8, 7, 6, 6, 5.5, 4][col]
        if cagr >= 15: return [7.5, 6.5, 6, 6, 5, 4, 3][col]
        if cagr >= 10: return [6, 5.5, 5.5, 5, 3.5, 2.5, 1.5][col]
        if cagr >= 6: return [5.5, 5.5, 4.5, 3.5, 2.5, 1.5, 1][col]
        if cagr >= 3: return [4.5, 4, 3, 2, 1.5, 1, 0][col]
        return [3.5, 3, 2, 1.5, 1, 0, 0][col]

    def get_eps_pe_score(eps, fwd_pe):
        if eps < 0: return 0
        if fwd_pe <= 20: col = 0
        elif fwd_pe <= 25: col = 1
        elif fwd_pe <= 30: col = 2
        elif fwd_pe <= 35: col = 3
        elif fwd_pe <= 50: col = 4
        else: col = 5
            
        if eps >= 30: return [5.0, 4.5, 4.0, 3.5, 2.0, 0][col]
        if eps >= 20: return [4.5, 4.0, 3.5, 3.0, 1.5, 0][col]
        if eps >= 15: return [4.0, 3.5, 3.0, 2.5, 1.0, 0][col]
        if eps >= 10: return [3.5, 3.0, 2.5, 2.0, 1.0, 0][col]
        return [2.0, 1.5, 1.0, 1.0, 0.5, 0][col]

    def get_hist_pe_score(diff):
        mapping = {">30% Discount": 2.5, "20-30% Discount": 2.0, "10-20% Discount": 1.5, 
                   "Fair Value (+/-10%)": 1.0, "10-20% Premium": 0.5, "20-30% Premium": 0.25, ">30% Premium": 0.0}
        return mapping.get(diff, 0)

    t3_score = get_ni_pe_score(ni_cagr, ttm_pe) + get_eps_pe_score(eps_growth, fwd_pe) + get_hist_pe_score(hist_pe_diff)

# ==========================================
# HIỂN THỊ KẾT QUẢ XẾP HẠNG
# ==========================================
st.divider()
st.header("🎯 KẾT QUẢ XẾP HẠNG TỰ ĐỘNG")

total_score = t1_score + t2_score + t3_score

col1, col2, col3, col4 = st.columns(4)
col1.metric("Cơ Bản (Tier 1)", f"{t1_score} / 15")
col2.metric("Tăng Trưởng (Tier 2)", f"{t2_score} / 17.5")
col3.metric("Định Giá (Tier 3)", f"{t3_score} / 17.5")
col4.metric("TỔNG ĐIỂM", f"{total_score} / 50.0")

if total_score >= 40:
    st.success("Tín hiệu: CỰC KỲ XUẤT SẮC (Thỏa mãn tiêu chí khắt khe của Hệ thống 50 Điểm).")
elif total_score >= 30:
    st.info("Tín hiệu: RẤT TỐT (Doanh nghiệp chất lượng, định giá ở mức hợp lý).")
elif total_score >= 20:
    st.warning("Tín hiệu: TRUNG BÌNH (Cần kiểm tra kỹ dòng tiền hoặc có thể định giá đang quá đắt).")
else:
    st.error("Tín hiệu: YẾU KÉM (Bị loại bỏ bởi các chốt chặn rủi ro cơ bản).")
