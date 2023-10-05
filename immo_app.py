import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st
import plotly.express as px
import base64
import warnings
warnings.filterwarnings('ignore')

pd.set_option('display.max_row',111)
pd.set_option('display.max_column',111)


st.title(' :house: Immo Data Analyze')

with st.sidebar:
    st.image("https://www.onepointltd.com/wp-content/uploads/2020/03/inno2.png")
    st.title("Digital Mobile Deployment_ML")
    choice = st.radio("Navigation", ["Download","GLM AC deployment","Customer Migration", "Project Manager", "Test"])
    st.info("This project application helps you to have a complete vision of the digital deployments of our clients")


if choice == "Download":
    st.header("Download Your Kantree Dataset") # ou st.subheader()
    file = st.file_uploader("Download Your File", key="1")
    if file:
        df = pd.read_csv(file, index_col=None)
        df= df.drop(columns=['application déployée'])

        st.write(df)
