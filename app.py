import streamlit as st
import requests

st.set_page_config(page_title="Hệ Thống 50 Điểm Tự Động", layout="wide")

st.title("📈 Hệ Thống Chấm Điểm Đầu Tư Giá Trị (50-Point System)")
st.markdown("Nhập mã cổ phiếu để tải dữ liệu tự động từ Fiscal.ai API.")

# --- TẠO THANH CÔNG CỤ BÊN TRÁI (SIDEBAR) ---
st.sidebar.header("🔍 Tải Dữ Liệu Tự Động")
ticker_input = st.sidebar.text_input("Nhập mã cổ phiếu (VD: NASDAQ_MSFT)", value="NASDAQ_MSFT")
api_key = st.sidebar.text_input("Nhập Fiscal.ai API Key của bạn:", type="password")

if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.data = {}

if st.sidebar.button("🚀 Tải dữ liệu từ Fiscal.ai"):
    if not api_key:
        st.sidebar.error("Vui lòng nhập API Key!")
    else:
        with st.spinner(f"Đang tải dữ liệu cho {ticker_input}..."):
            try:
                url = f"https://api.fiscal.ai/v1/company/profile?companyKey={ticker_input.upper()}&apiKey={api_key}"
                response = requests.get(url)
                
                if response.status_code == 200:
                    info = response.json()
                    
                    st.sidebar.success("Tải dữ liệu Fiscal.ai thành công!")
                    st.sidebar.json(info)
                    
                    st.session_state.data = {
                        'current_ratio': info.get('currentRatio', 1.0),
                        'debt_equity': info.get('debtToEquity', 0.5),
                        'gross_margin': info.get('grossMargin', 45.0),
                        'net_margin': info.get('netMargin', 16.0),
                        'roe': info.get('roe', 20.0),
                        'ttm_pe': info.get('peRatioTTM', 22.0),
                        'fwd_pe': info.get('forwardPE', 19.0),
                        'div_yield': info.get('dividendYield', 0.0)
                    }
                    st.session_state.data_loaded = True
                else:
                    st.sidebar.error(f"Lỗi API: {response.status_code}. Vui lòng kiểm tra mã cổ phiếu.")
            except Exception as e:
                st.sidebar.error("Lỗi kết nối mạng.")
                st.sidebar.error("Lỗi kết nối mạng.")

# (Phần Code giao diện các Tab Tier 1, 2, 3 và Tính điểm giữ nguyên như phiên bản Yahoo Finance)
