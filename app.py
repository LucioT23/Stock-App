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
    # Ajouter un bouton de téléchargement de fichier
    uploaded_file = st.file_uploader("Choisissez un fichier Excel :", type=["xlsx"])

    if uploaded_file is not None:
    # Charger le fichier sélectionné en tant que dataframe
      df = pd.read_excel(uploaded_file, index_col=None)

      # Afficher le dataframe
      st.write("Voici le contenu du fichier Excel sélectionné :")
      st.write(df)

    # Ajouter un bouton "Télécharger"
    #st.write("Cliquez sur le bouton pour télécharger le fichier Excel :")
    #if st.button("Télécharger"):
    #    st.write("Téléchargement en cours...")
    #    st.excel_download(df, "data.xlsx")
    #    st.write("Téléchargement terminé.")

    # file = st.file_uploader("Upload Your Dataset")
    # if file: 
    #    df = pd.read_csv(file, index_col=None)
    #    df.to_csv('dataset.csv', index=None)
    #    st.dataframe(df)
