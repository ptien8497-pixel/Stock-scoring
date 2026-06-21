import streamlit as st
import requests

st.set_page_config(page_title="Hệ Thống 50 Điểm (FMP)", layout="wide")

st.title("📈 Hệ Thống Chấm Điểm Đầu Tư Giá Trị (50-Point System)")
st.markdown("Tự động tải dữ liệu từ Financial Modeling Prep (FMP) và tính các chỉ số cơ bản từ báo cáo tài chính gốc.")

st.sidebar.header("🔍 Tải Dữ Liệu Tự Động")
ticker_input = st.sidebar.text_input("Nhập mã cổ phiếu Mỹ (VD: AAPL, MSFT, NVDA)", value="AAPL")
api_key = st.sidebar.text_input("Nhập FMP API Key của bạn:", type="password")

if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.data = {}

def get_first_record(payload, name, ticker):
    if isinstance(payload, dict):
        if "Error Message" in payload:
            raise ValueError(f"{name}: {payload['Error Message']}")
        if "error" in payload:
            raise ValueError(f"{name}: {payload['error']}")
        if "errors" in payload:
            raise ValueError(f"{name}: {payload['errors']}")
        raise ValueError(f"{name}: Dữ liệu trả về không đúng định dạng list.")
    if not isinstance(payload, list) or len(payload) == 0:
        raise ValueError(f"{name}: Không có dữ liệu cho mã {ticker}.")
    return payload[0]

if st.sidebar.button("🚀 Tải dữ liệu từ FMP"):
    if not api_key:
        st.sidebar.error("Vui lòng nhập FMP API Key.")
    else:
        with st.spinner(f"Đang tải dữ liệu cho {ticker_input.upper()}..."):
            try:
                tk = ticker_input.upper().strip()

                url_quote = f"https://financialmodelingprep.com/api/v3/quote/{tk}?apikey={api_key}"
                url_is = f"https://financialmodelingprep.com/api/v3/income-statement/{tk}?limit=1&apikey={api_key}"
                url_bs = f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{tk}?limit=1&apikey={api_key}"
                url_cf = f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{tk}?limit=1&apikey={api_key}"

                resp_quote = requests.get(url_quote, timeout=20)
                resp_is = requests.get(url_is, timeout=20)
                resp_bs = requests.get(url_bs, timeout=20)
                resp_cf = requests.get(url_cf, timeout=20)

                quote_json = resp_quote.json()
                is_json = resp_is.json()
                bs_json = resp_bs.json()
                cf_json = resp_cf.json()

                st.sidebar.write("Quote status:", resp_quote.status_code)
                st.sidebar.write("IS status:", resp_is.status_code)
                st.sidebar.write("BS status:", resp_bs.status_code)
                st.sidebar.write("CF status:", resp_cf.status_code)

                quote = get_first_record(quote_json, "Quote", tk)
                inc = get_first_record(is_json, "Income Statement", tk)
                bal = get_first_record(bs_json, "Balance Sheet", tk)
                cf = get_first_record(cf_json, "Cash Flow", tk)

                current_assets = bal.get("totalCurrentAssets") or 0
                current_liabilities = bal.get("totalCurrentLiabilities") or 0
                total_debt = bal.get("totalDebt") or 0
                equity = bal.get("totalStockholdersEquity") or 0
                total_assets = bal.get("totalAssets") or 0
                cash_and_short_term = bal.get("cashAndShortTermInvestments") or bal.get("cashAndCashEquivalents") or 0
                short_term_debt = bal.get("shortTermDebt") or 0
                goodwill = bal.get("goodwill") or 0
                intangible_assets = bal.get("intangibleAssets") or 0

                revenue = inc.get("revenue") or 0
                gross_profit = inc.get("grossProfit") or 0
                net_income = inc.get("netIncome") or 0
                ebitda = inc.get("ebitda") or 0

                free_cash_flow = cf.get("freeCashFlow") or 0

                market_cap = quote.get("marketCap") or 0
                pe_ratio = quote.get("pe") or quote.get("priceEarningsRatio") or 0

                calc_current_ratio = current_assets / current_liabilities if current_liabilities else 0
                calc_debt_equity = total_debt / equity if equity else 0
                calc_gross_margin = (gross_profit / revenue) * 100 if revenue else 0
                calc_net_margin = (net_income / revenue) * 100 if revenue else 0
                calc_roe = (net_income / equity) * 100 if equity else 0
                calc_fcf_yield = (free_cash_flow / market_cap) * 100 if market_cap else 0
                calc_cash_vs_debt = "Cash > ST Debt" if cash_and_short_term > short_term_debt else "Cash <= ST Debt"
                calc_intangibles_ratio = ((goodwill + intangible_assets) / total_assets) if total_assets else 0
                calc_net_debt_ebitda = ((total_debt - cash_and_short_term) / ebitda) if ebitda else 0

                st.session_state.data = {
                    "current_ratio": calc_current_ratio,
                    "debt_equity": calc_debt_equity,
                    "gross_margin": calc_gross_margin,
                    "net_margin": calc_net_margin,
                    "roe": calc_roe,
                    "ttm_pe": pe_ratio,
                    "fcf_yield": calc_fcf_yield,
                    "cash_vs_debt": calc_cash_vs_debt,
                    "intangibles": calc_intangibles_ratio,
                    "net_debt_ebitda": calc_net_debt_ebitda,
                    "div_yield": 0.0
                }

                st.session_state.data_loaded = True
                st.sidebar.success("Tải & tính toán thành công!")

            except Exception as e:
                st.sidebar.error(f"Lỗi hệ thống: {str(e)}")

d = st.session_state.data if st.session_state.data_loaded else {}

tab1, tab2, tab3 = st.tabs(["🟢 Tier 1: Cơ Bản", "🔵 Tier 2: Tăng Trưởng", "🟣 Tier 3: Định Giá"])

with tab1:
    st.header("Hạng Mục 1: Các Yếu Tố Cơ Bản (Max 15 Pts)")
    st.caption("Một phần dữ liệu được tự động tính từ báo cáo tài chính FMP; bạn có thể chỉnh tay nếu cần.")
    col1, col2 = st.columns(2)

    with col1:
        current_ratio = st.number_input("Current Ratio", value=float(d.get("current_ratio", 1.0)))
        debt_equity = st.number_input("Debt to Equity", value=float(d.get("debt_equity", 0.5)))
        gross_margin = st.number_input("Gross Profit Margin (%)", value=float(d.get("gross_margin", 45.0)))
        net_margin = st.number_input("Net Profit Margin (%)", value=float(d.get("net_margin", 16.0)))
        roe = st.number_input("Return on Equity (ROE) (%)", value=float(d.get("roe", 20.0)))
        roc = st.number_input("Return on Capital (ROC) (%)", value=16.0)
        shareholder_yield = st.number_input("Shareholder Yield (%) (Cổ tức + Mua lại)", value=float(d.get("div_yield", 0.0)))

    with col2:
        fcf_yield = st.number_input("FCF Yield (%)", value=float(d.get("fcf_yield", 4.0)))
        cash_vs_debt = st.selectbox(
            "Tiền mặt so với Nợ ngắn hạn",
            ["Cash > ST Debt", "Cash <= ST Debt"],
            index=0 if d.get("cash_vs_debt", "Cash > ST Debt") == "Cash > ST Debt" else 1
        )
        pref_stock = st.selectbox("Cổ phiếu ưu đãi", ["Không có", "Có"])
        re_trend = st.selectbox("Xu hướng Lợi nhuận giữ lại (10 năm)", ["Tăng vững chắc", "Không rõ/Giảm"])
        intangibles = st.number_input("(Goodwill + Intangibles) / Total Assets", value=float(d.get("intangibles", 0.2)))
        net_debt_ebitda = st.number_input("Net Debt / EBITDA", value=float(d.get("net_debt_ebitda", 0.5)))
        div_cagr_5y = st.number_input("5-Year Dividend CAGR (%)", value=5.0)

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
    st.info("Các chỉ số CAGR 5 năm và forecast nên nhập tay hoặc tính riêng để đảm bảo đúng logic hệ thống của bạn.")
    rev_cagr = st.number_input("5-Year Revenue CAGR (%)", value=15.0)
    next_rev = st.number_input("Next-Year Forecast Revenue Growth (%)", value=18.0)
    fcf_cagr = st.number_input("5-Year FCF CAGR (%)", value=12.0)

    def score_growth(val, mode):
        if val >= 30: return 2.5 if mode == "rev5" else 5.0
        if val >= 25: return 2.25 if mode == "rev5" else 4.5
        if val >= 20: return 2.0 if mode == "rev5" else 4.0
        if val >= 14: return 1.75 if mode == "rev5" else 3.5
        if val >= 12: return 1.5 if mode == "rev5" else 3.0
        if val >= 10: return 1.25 if mode == "rev5" else 2.5
        if val >= 8: return 1.0 if mode == "rev5" else 2.0
        if val >= 6: return 0.75 if mode == "rev5" else 1.5
        if val >= 4: return 0.5 if mode == "rev5" else 1.0
        if val >= 2: return 0.25 if mode == "rev5" else 0.5
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

    t2_score = score_growth(rev_cagr, "rev5") + score_growth(next_rev, "next") + score_fcf(fcf_cagr)

with tab3:
    st.header("Hạng Mục 3: Định Giá (Max 17.5 Pts)")
    col_a, col_b = st.columns(2)

    with col_a:
        ni_cagr = st.number_input("5-Yr Net Income CAGR (%)", value=16.0)
        ttm_pe = st.number_input("TTM P/E Ratio", value=float(d.get("ttm_pe", 22.0)))

    with col_b:
        eps_growth = st.number_input("Next-Yr EPS Growth (%)", value=22.0)
        fwd_pe = st.number_input("Forward P/E Ratio", value=19.0)

    hist_pe_diff = st.selectbox(
        "Current P/E vs 5-Yr Hist P/E",
        [">30% Discount", "20-30% Discount", "10-20% Discount", "Fair Value (+/-10%)", "10-20% Premium", "20-30% Premium", ">30% Premium"]
    )

    def get_ni_pe_score(cagr, pe):
        if pe > 100:
            return 0
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

    def get_eps_pe_score(eps, pe):
        if eps < 0:
            return 0
        if pe <= 20: col = 0
        elif pe <= 25: col = 1
        elif pe <= 30: col = 2
        elif pe <= 35: col = 3
        elif pe <= 50: col = 4
        else: col = 5

        if eps >= 30: return [5.0, 4.5, 4.0, 3.5, 2.0, 0][col]
        if eps >= 20: return [4.5, 4.0, 3.5, 3.0, 1.5, 0][col]
        if eps >= 15: return [4.0, 3.5, 3.0, 2.5, 1.0, 0][col]
        if eps >= 10: return [3.5, 3.0, 2.5, 2.0, 1.0, 0][col]
        return [2.0, 1.5, 1.0, 1.0, 0.5, 0][col]

    def get_hist_pe_score(diff):
        mapping = {
            ">30% Discount": 2.5,
            "20-30% Discount": 2.0,
            "10-20% Discount": 1.5,
            "Fair Value (+/-10%)": 1.0,
            "10-20% Premium": 0.5,
            "20-30% Premium": 0.25,
            ">30% Premium": 0.0
        }
        return mapping.get(diff, 0)

    t3_score = get_ni_pe_score(ni_cagr, ttm_pe) + get_eps_pe_score(eps_growth, fwd_pe) + get_hist_pe_score(hist_pe_diff)

st.divider()
st.header("🎯 KẾT QUẢ XẾP HẠNG")

total_score = t1_score + t2_score + t3_score

c1, c2, c3, c4 = st.columns(4)
c1.metric("Cơ Bản (Tier 1)", f"{t1_score} / 15")
c2.metric("Tăng Trưởng (Tier 2)", f"{t2_score} / 17.5")
c3.metric("Định Giá (Tier 3)", f"{t3_score} / 17.5")
c4.metric("TỔNG ĐIỂM", f"{total_score} / 50.0")

if total_score >= 40:
    st.success("Tín hiệu: CỰC KỲ XUẤT SẮC.")
elif total_score >= 30:
    st.info("Tín hiệu: RẤT TỐT.")
elif total_score >= 20:
    st.warning("Tín hiệu: TRUNG BÌNH.")
else:
    st.error("Tín hiệu: YẾU KÉM.")
