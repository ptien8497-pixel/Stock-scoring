if st.sidebar.button("🚀 Tải dữ liệu từ FMP"):
    if not api_key:
        st.sidebar.error("Vui lòng nhập API Key từ FMP!")
    else:
        with st.spinner(f"Đang tải báo cáo tài chính cho {ticker_input.upper()}..."):
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

                def get_first_record(payload, name):
                    if isinstance(payload, dict):
                        if "Error Message" in payload:
                            raise ValueError(f"{name}: {payload['Error Message']}")
                        if "error" in payload:
                            raise ValueError(f"{name}: {payload['error']}")
                        if "errors" in payload:
                            raise ValueError(f"{name}: {payload['errors']}")
                        raise ValueError(f"{name}: Dữ liệu trả về không đúng định dạng list.")
                    if not isinstance(payload, list) or len(payload) == 0:
                        raise ValueError(f"{name}: Không có dữ liệu cho mã {tk}.")
                    return payload[0]

                quote = get_first_record(quote_json, "Quote")
                inc = get_first_record(is_json, "Income Statement")
                bal = get_first_record(bs_json, "Balance Sheet")
                cf = get_first_record(cf_json, "Cash Flow")

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
