import streamlit as st
import pandas as pd
import numpy as np
from tensorflow import keras
from keras import models

import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime

st.title("Stock Prediction App")
stock = st.text_input("Enter The Stock id", "GOOG")

end = datetime.now()
start = end.replace(year=end.year - 20)

stockdata = yf.download(stock,start,end)
# model = load_model('latest_stock_price_model.keras')
st.subheader("stock data")
st.write(stockdata)

splitting_len = int(len(stockdata)*0.7)
x_test = pd.DataFrame(stockdata.Close[splitting_len:])

def plot_graph(figuresize,values,columnname,heading):
    plt.figure()
    values.plot(figsize=figuresize)
    plt.xlabel("years")
    plt.ylabel(columnname)
    plt.title(f'{heading} stock price')

st.plotly_chart()
