import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import yfinance as yf

st.title('S&P 500 App')

st.markdown("""
This app retrieves the list of the **S&P 500** (from Wikipedia) and its corresponding **stock closing price** (year-to-date)!
* **Python libraries:** base64, pandas, streamlit, numpy, matplotlib, seaborn
* **Data source:** [Wikipedia](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies).
""")

st.sidebar.header('User Input Features')

# Web scraping on S&P 500 data
@st.cache
def load_data():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    html = pd.read_html(url, header=0)
    df = html[0]
    return df

df = load_data()
sector = df.groupby('GICS Sector')

# Sidebar - Sector selection
sorted_sector_unique = sorted(df['GICS Sector'].unique())
selected_sector = st.sidebar.multiselect('Sector', sorted_sector_unique, sorted_sector_unique)

# Filtering data
df_selected_sector = df[(df['GICS Sector'].isin(selected_sector))]

st.header('Display Companies in Selecter Sector')
st.write('Data dimension: ' + str(df_selected_sector.shape[0]) + ' rows and ' + str(df_selected_sector.shape[1]) + ' columns.')
st.dataframe(df_selected_sector)

# Download S&P 500 data
# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="SP500.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(df_selected_sector), unsafe_allow_html=True)

data = yf.download(
            tickers = list(df_selected_sector[:10].Symbol),
            period = 'ytd',
            interval = '1d',
            group_by = 'ticker',
            auto_adjust = True,
            prepost = True,
            threads = True,
            proxy = None
        )

# Plot Closing Price of Query Symbol
# def price_plot(symbol):
#     df = pd.DataFrame(data[symbol].Close)
#     df['Date'] = df.index
#     fig, ax = plt.subplots()
#     ax.fill_between(df.Date, df.Close, color='skyblue', alpha=.3)
#     ax.plot(df.Date, df.Close, color='skyblue', alpha=.8)
#     ax.set_xticks(ax.get_xticklabels(), rotation=90)
#     ax.title(symbol, fontweight='bold')
#     ax.xlabel('Date', fontweight='bold')
#     ax.ylabel('Closing Price', fontweight='bold')
#     return st.pyplot(fig)

def price_plot(symbol):
    df = pd.DataFrame(data[symbol].Close)
    df['Date'] = pd.to_datetime(df.index, format='%Y-%m-%d')
    fig, ax = plt.subplots()
    fig.autofmt_xdate(rotation=90)
    ax.fill_between(df.Date, df.Close, color='skyblue', alpha=.3)
    ax.plot(df.Date, df.Close, color='skyblue', alpha=.8)
    ax.set_title(symbol, fontweight='bold')
    ax.set_xlabel('Date', fontweight='bold')
    ax.set_ylabel('Closing Price', fontweight='bold')
    return st.pyplot(fig)

num_company = st.sidebar.slider('Number of Companies', 1, 5)

if st.button('Show Plots'):
    st.header('Stock Closing Price')
    for i in list(df_selected_sector.Symbol)[:num_company]:
        price_plot(i)
