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

# pour nommer la page
st.set_page_config(page_title="SuperImmo!!!", page_icon=":house:",layout="wide")

st.title(' :house: Immo Data Analyze')
# Pour remonter le titre dans la page
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

fl = st.file_uploader(" :file_folder: Upload a file",type=(["csv","txt","xlsx","xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename, encoding = "ISO-8859-1")
        

st.sidebar.header("Choose your filter: ")
# Create for Region
nb_rooms = st.sidebar.multiselect("Nombre de chambre", df["Number Room"].unique())
if not nb_rooms:
    df2 = df.copy()
else:
    df2 = df[df["Number Room"].isin(Number Room)]
