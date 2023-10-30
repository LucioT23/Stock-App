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

fl = st.file_uploader(" :file_folder: Upload a file",type=(["csv","txt","xlsx","xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename) #, encoding = "ISO-8859-1")

with st.expander("Data"):
    st.dataframe(df.style.background_gradient(cmap="Oranges"))

st.line_chart(data=df, x=df['Close'], y=df['Date'], use_container_width=True) #color='r'
