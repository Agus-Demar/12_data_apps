import yfinance as yf
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.write("""
# Simple Stock Price App

Shown are the stock **closing price** and ***volume*** of Google!

""")

#define the ticker symbol
tickerSymbol = 'SPY'
#get data on this ticker
tickerData = yf.Ticker(tickerSymbol)
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