import streamlit as st
import pandas as pd
import numpy as np 
from datetime import datetime 
import streamlit as st
!pip install plotly_express
import plotly.express as px

pd.set_option('display.max_row',111)
pd.set_option('display.max_column',111)
#import openpyxl
#from operator import index
#import plotly.express as px
#import pycaret
#from pycaret.regression import setup, compare_models, pull, save_model, load_model
#import pandas_profiling
#from streamlit_pandas_profiling import st_profile_report
#import os 

st.title('A Simple Tony Web App')

with st.sidebar: 
    st.image("https://www.onepointltd.com/wp-content/uploads/2020/03/inno2.png")
    st.title("Mobile Client Fleet Check_ML")
    choice = st.radio("Navigation", ["Download","Profiling","Modelling", "Upload"])
    st.info("This project application helps you check your customer mobile fleet data.")

    
if choice == "Download":
    st.title("Download Your Dataset")
    file = st.file_uploader("Download Your File")
    if file: 
        df = pd.read_csv(file, index_col=None)
        df.to_csv('dataset.csv', index=None)
        st.dataframe(df)


