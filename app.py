import streamlit as st
import pandas as pd
from operator import index
#import plotly.express as px
from pycaret.regression import setup, compare_models, pull, save_model, load_model
import pandas_profiling
from streamlit_pandas_profiling import st_profile_report
import os 

st.title('A Simple Streamlit Tony Web App')

with st.sidebar: 
    st.image("https://www.onepointltd.com/wp-content/uploads/2020/03/inno2.png")
    #st.title("Mobile Client Fleet Check_ML")
    #choice = st.radio("Navigation", ["Upload","Profiling","Modelling", "Download"])
    #st.info("This project application helps you check your customer mobile fleet data.")
