import yfinance as yf
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.write("""
# Simple Stock Price App

Shown are the stock **closing price** and ***volume*** of major indexes!

""")

#dict that maps tickers
ticker_dict = {'S&P 500':'SPY','Nasdaq':'QQQ','Industrial Dow Jones':'DIA','Russell 2000':'IWM'}
#define the ticker symbol
selected_ticker = st.selectbox('Choose one of the following tickers from major indexes', ['S&P 500','Nasdaq','Industrial Dow Jones','Russell 2000'])
#get data on this ticker
tickerData = yf.Ticker(ticker_dict[selected_ticker])
#get the historical prices for this ticker
tickerDF = tickerData.history(period='1d', start=datetime.today() - timedelta(days=365), end=datetime.today())
# Open   High     Low Close    Volume    Dividends   Stock Splits

st.write("""
## Closing price
""")
st.line_chart(tickerDF.Close)
st.write("""
## Volume
""")
st.line_chart(tickerDF.Volume)