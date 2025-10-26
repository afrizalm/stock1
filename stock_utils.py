import requests
from bs4 import BeautifulSoup
import yfinance as yf
import pandas as pd
import time

def get_lq45_kontan():
    url = 'https://www.kontan.co.id/indeks-lq45'
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')

    table = soup.find('table')
    rows = table.find_all('tr')[1:]

    kode_list = []
    nama_list = []

    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 3:
            kode = cols[1].text.strip()
            nama = cols[2].text.strip()
            kode_list.append(kode)
            nama_list.append(nama)
    
    df = pd.DataFrame({'Kode': kode_list, 'Nama': nama_list})
    df['Ticker'] = df['Kode'].apply(lambda x: f"{x}.JK")
    return df

def get_stock_metrics(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        dividends = stock.dividends
        actions = stock.actions

        current_price = info.get("currentPrice", 0)
        eps = info.get("trailingEps", 0)
        book_value = info.get("bookValue", 0)
        total_debt = info.get("totalDebt", 0)
        total_equity = info.get("totalAssets", 0) - total_debt if "totalAssets" in info else None
        revenue = info.get("totalRevenue", 0)
        operating_income = info.get("operatingIncome", 0)
        current_assets = info.get("totalCurrentAssets", 0)
        current_liabilities = info.get("totalCurrentLiabilities", 0)

        pe_ratio = current_price / eps if eps else None
        pb_ratio = current_price / book_value if book_value else None
        de_ratio = total_debt / total_equity if total_equity else None
        roe = info.get("returnOnEquity", None)
        current_ratio = current_assets / current_liabilities if current_liabilities else None
        dividend_yield = info.get("dividendYield", None)
        earnings_yield = eps / current_price if current_price else None
        operating_margin = operating_income / revenue if revenue else None

        enter_date = dividends.index.min() if not dividends.empty else None
        exit_date = dividends.index.max() if not dividends.empty else None

        valuation = "Undervalued" if pe_ratio and pe_ratio < 15 and pb_ratio and pb_ratio < 1 else "Overvalued"

        return {
            "Stock": ticker,
            "Price": current_price,
            "P/E": round(pe_ratio, 2) if pe_ratio else None,
            "P/B": round(pb_ratio, 2) if pb_ratio else None,
            "D/E": round(de_ratio, 2) if de_ratio else None,
            "ROE": round(roe, 2) if roe else None,
            "Current Ratio": round(current_ratio, 2) if current_ratio else None,
            "Dividend Yield": round(dividend_yield, 4) if dividend_yield else None,
            "Earnings Yield": round(earnings_yield, 4) if earnings_yield else None,
            "Operating Margin": round(operating_margin, 4) if operating_margin else None,
            "Valuation": valuation
        }

    except Exception as e:
        return {"Stock": ticker, "Error": str(e)}
