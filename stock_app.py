import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import plotly.express as px
import base64
import warnings
warnings.filterwarnings('ignore')

pd.set_option('display.max_row',111)
pd.set_option('display.max_column',111)

# pour nommer la page
st.set_page_config(page_title="Stock Prediction!!!", page_icon=":euro:",layout="wide")

st.title(' :house: Stock Prediction')
# Pour remonter le titre dans la page
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

# pip install streamlit fbprophet yfinance plotly
import streamlit as st
from datetime import date

import yfinance as yf
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go

START = "2015-01-01"
TODAY = date.today().strftime("%Y-%m-%d")

st.title('Stock Forecast App')

stocks = ('GOOG', 'AAPL', 'MSFT', 'GME')
selected_stock = st.selectbox('Select dataset for prediction', stocks)

n_years = st.slider('Years of prediction:', 1, 4)
period = n_years * 365


@st.cache
def load_data(ticker):
    data = yf.download(ticker, START, TODAY)
    data.reset_index(inplace=True)
    return data

	
data_load_state = st.text('Loading data...')
data = load_data(selected_stock)
data_load_state.text('Loading data... done!')

st.subheader('Raw data')
with st.expander("Data"):
    st.dataframe(data.style.background_gradient(cmap="Oranges"))

# Plot raw data
def plot_raw_data():
	fig = go.Figure()
	fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name="stock_open"))
	fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name="stock_close"))
	fig.layout.update(title_text='Time Series data with Rangeslider', xaxis_rangeslider_visible=True)
	st.plotly_chart(fig)
	
plot_raw_data()

# Predict forecast with Prophet.
df_train = data[['Date','Close']]
df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})

m = Prophet()
m.fit(df_train)
future = m.make_future_dataframe(periods=period)
forecast = m.predict(future)

# Show and plot forecast
st.subheader('Forecast data')
with st.expander("Data"):
    st.dataframe(forecast.style.background_gradient(cmap="Blues"))
    
st.write(f'Forecast plot for {n_years} years')
fig1 = plot_plotly(m, forecast)
fig1.update_layout(yaxis_title="Cours de l'action €", xaxis_title = "Date")
st.plotly_chart(fig1,use_container_width=True)
#st.plotly_chart(fig1)

st.write("Forecast components")
fig2 = m.plot_components(forecast)
#fig2.update_layout(yaxis_title="Cours de l'action €", xaxis_title = "Date")
st.plotly_chart(fig2,use_container_width=True) 
#st.write(fig2)

#fl = st.file_uploader(" :file_folder: Upload a file",type=(["csv","txt","xlsx","xls"]))
#if fl is not None:
#    filename = fl.name
#    st.write(filename)
#    df = pd.read_csv(filename) #, encoding = "ISO-8859-1")

#df['Date']=pd.to_datetime(df['Date'])



#chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])
#st.line_chart(data=df, x=df['Close'], y=df['Date']) 
