import streamlit as st
import pandas as pd
#from operator import index
#import plotly.express as px
#import pycaret
#from pycaret.regression import setup, compare_models, pull, save_model, load_model
#import pandas_profiling
#from streamlit_pandas_profiling import st_profile_report
#import os 

st.title('A Simple Streamlit Tony Web App')

with st.sidebar: 
    st.image("https://www.onepointltd.com/wp-content/uploads/2020/03/inno2.png")
    st.title("Mobile Client Fleet Check_ML")
    choice = st.radio("Navigation", ["Upload","Profiling","Modelling", "Download"])
    st.info("This project application helps you check your customer mobile fleet data.")

    
if choice == "Upload":
    st.title("Upload Your Dataset")
    file = st.file_uploader("Upload Your Dataset")
    if file: 
        df = pd.read_csv(file, index_col=None)
        df.to_csv('dataset.csv', index=None)
        st.dataframe(df)
