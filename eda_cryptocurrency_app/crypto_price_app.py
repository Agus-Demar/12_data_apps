# This app is for educational purpose only. Insights gained is not financial advice. Use at your own risk!
import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
import base64
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests
import json
import time
import ast
#---------------------------------#
# New feature (make sure to upgrade your streamlit library)
# pip install --upgrade streamlit

#---------------------------------#
# Page layout
## Page expands to full width
st.set_page_config(layout="wide")
#---------------------------------#
# Title

image = Image.open('crypto_logo.jpg')

st.image(image, width=500)

st.title('Crypto Price App')
st.markdown("""
This app retrieves cryptocurrency prices for the top 100 cryptocurrency from the **CoinMarketCap**!

""")
#---------------------------------#
# About
expander_bar = st.expander("About")
expander_bar.markdown("""
* **Python libraries:** base64, pandas, streamlit, numpy, matplotlib, seaborn, BeautifulSoup, requests, json, time
* **Data source:** [CoinMarketCap](http://coinmarketcap.com).
* **Credit:** Web scraper adapted from the Medium article *[Web Scraping Crypto Prices With Python](https://towardsdatascience.com/web-scraping-crypto-prices-with-python-41072ea5b5bf)* written by [Bryan Feng](https://medium.com/@bryanf).
""")

#---------------------------------#
# Page layout (continued)
## Divide page to 3 columns (col1 = sidebar, col2 and col3 = page contents)
col1 = st.sidebar
col2, col3 = st.columns((2,1))

#---------------------------------#
# Sidebar + Main panel
col1.header('Input Options')

## Sidebar - Currency price unit
# currency_price_unit = col1.selectbox('Select currency for price', ('USD', 'BTC', 'ETH'))

# Web scraping of CoinMarketCap data
@st.cache(hash_funcs={'_json.Scanner': hash})
def load_data():

    selected_cols = ['coin_name',
         'coin_symbol', 
         'market_cap', 
         'price',
         'percent_change_1h',
         'percent_change_24h',
         'percent_change_7d',
         'volume_24h']

    cmc = requests.get('https://coinmarketcap.com')
    soup = BeautifulSoup(cmc.content, 'html.parser')

    data = soup.find('script', id='__NEXT_DATA__', type = 'application/json')
    coins = {}
    coin_data = json.loads(data.contents[0])
    listings = coin_data['props']['initialState']
    listings = json.loads(listings)['cryptocurrency']['listingLatest']['data']
    cols = listings[0]['keysArr']
    content = pd.DataFrame(listings[1:])
    content = content.drop(content.columns[-1], axis=1)
    content.columns = cols
    content = content.drop(['id'], axis=1).rename(columns={'slug':'coin_name', 'symbol':'coin_symbol',
                                                           'quote.USD.price':'price',
                                                           'quote.USD.percentChange1h':'percent_change_1h',
                                                           'quote.USD.percentChange24h':'percent_change_24h',
                                                           'quote.USD.percentChange7d':'percent_change_7d',
                                                           'quote.USD.marketCap':'market_cap',
                                                           'quote.USD.volume24h':'volume_24h'})
    content = content[selected_cols] 
    content['market_cap'] = content['market_cap'].astype(int).apply(lambda x: ("{:,d}".format(x)))
    content['volume_24h'] = content['volume_24h'].astype(int).apply(lambda x: ("{:,d}".format(x)))
    content['price'] = content['price'].apply(lambda x: ("{:.2f}".format(x)))
    return content
   
df = load_data()

## Sidebar - Cryptocurrency selections
sorted_coin = sorted( df['coin_symbol'] )
selected_coin = col1.multiselect('Cryptocurrency', sorted_coin, sorted_coin)

df_selected_coin = df[ (df['coin_symbol'].isin(selected_coin)) ] # Filtering data

## Sidebar - Number of coins to display
num_coin = col1.slider('Display Top N Coins', 1, 100, 100)
df_coins = df_selected_coin[:num_coin]

## Sidebar - Percent change timeframe
percent_timeframe = col1.selectbox('Percent change time frame',
                                    ['7d','24h', '1h'])
percent_dict = {"7d":'percent_change_7d',"24h":'percent_change_24h',"1h":'percent_change_1h'}
selected_percent_timeframe = percent_dict[percent_timeframe]

## Sidebar - Sorting values
sort_values = col1.selectbox('Sort values?', ['Yes', 'No'])

col2.subheader('Price Data of Selected Cryptocurrency')
col2.write('Data Dimension: ' + str(df_selected_coin.shape[0]) + ' rows and ' + str(df_selected_coin.shape[1]) + ' columns.')

col2.dataframe(df_coins)

# Download CSV data
# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="crypto.csv">Download CSV File</a>'
    return href

col2.markdown(filedownload(df_selected_coin), unsafe_allow_html=True)

#---------------------------------#
# Preparing data for Bar plot of % Price change
col2.subheader('Table of % Price Change')
df_change = pd.concat([df_coins.coin_symbol, df_coins.percent_change_1h, df_coins.percent_change_24h, df_coins.percent_change_7d], axis=1)
df_change = df_change.set_index('coin_symbol')
col2.dataframe(df_change)
df_change['positive_percent_change_1h'] = df_change['percent_change_1h'] > 0
df_change['positive_percent_change_24h'] = df_change['percent_change_24h'] > 0
df_change['positive_percent_change_7d'] = df_change['percent_change_7d'] > 0


# Conditional creation of Bar plot (time frame)
col3.subheader('Bar plot of % Price Change')

def plot_change(df, percent_timeframe, sort_values):
    timeframe_dict = {'7d': ['percent_change_7d', '*7 days period*', 'positive_percent_change_7d'],
                      '24h': ['percent_change_24h', '*24 hour period*', 'positive_percent_change_24h'],
                      '1h': ['percent_change_1h', '*1 hour period*', 'positive_percent_change_1h']} 

    values = timeframe_dict[percent_timeframe]

    if sort_values == 'Yes':
        df = df.sort_values(by=[values[0]])
    col3.write(values[1])
    plt.figure(figsize=(5,25))
    plt.subplots_adjust(top = 1, bottom = 0)
    ax = df[values[0]].plot(kind='barh', color=df[values[2]].map({True: 'g', False: 'r'}))
    ax.xaxis.grid(True)
    col3.pyplot(plt)

plot_change(df_change, percent_timeframe, sort_values)