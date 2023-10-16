import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
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

# Create for Number of room
nb_rooms = st.sidebar.multiselect("Nombre de chambre", df['Number Room'].unique())
if not nb_rooms:
    df2 = df.copy()
else:
    df2 = df[df['Number Room'].isin(nb_rooms)]

# Create for City
city = st.sidebar.multiselect("Ville", df2["City"].unique())
if not city:
    df3 = df2.copy()
else:
    df3 = df2[df2["City"].isin(city)]

st.write(df3)

# Create for Type of house
typologie = st.sidebar.multiselect("Type de logement",df3["type_logement"].unique())

# Filter the data based on Number of room, City and Typologie

if not nb_rooms and not city and not typologie:
    filtered_df = df
elif not nb_rooms and not city:
    filtered_df = df[df["type_logement"].isin(typologie)]
elif not nb_rooms and not typologie:
    filtered_df = df[df["City"].isin(city)]
elif not typologie and not city:
    filtered_df = df[df["Number Room"].isin(nb_rooms)]
elif nb_rooms and city:
    filtered_df = df3[df["Number Room"].isin(nb_rooms) & df3["City"].isin(city)]
elif nb_rooms and typologie:
    filtered_df = df3[df["Number Room"].isin(nb_rooms) & df3["type_logement"].isin(typologie)]
elif city and typologie:
    filtered_df = df3[df["City"].isin(city) & df3["type_logement"].isin(typologie)]
elif city:
    filtered_df = df3[df3["City"].isin(city)]
elif typologie:
    filtered_df = df3[df3["type_logement"].isin(typologie)]
elif nb_rooms:
    filtered_df = df3[df3["Number Room"].isin(nb_rooms)]
else:
    filtered_df = df3[df3["Number Room"].isin(nb_rooms) & df3["City"].isin(city) & df3["type_logement"].isin(typologie)]

col1, col2, col3 = st.columns((3))
with col1:
    st.subheader("Prix par nuit en fonction du nb de chambre")
    #fig = px.bar(category_df, x = "Category", y = "Sales", text = ['${:,.2f}'.format(x) for x in category_df["Sales"]],
    #             template = "seaborn")

    # Scatter plot des annonces par prix et par nombre de chambres
    fig = px.scatter(filtered_df, x="Number Room", y='euros', template = "seaborn") #,color="piscine")
    #fig.update_layout(height=500,width =900, yaxis_title="Prix € par nuit", xaxis_title = "Nombre de chambres", title = "Prix par nuit en fonction du nombre de chambre")
    fig.update_layout(yaxis_title="Prix € par nuit", xaxis_title = "Nombre de chambres")
    st.plotly_chart(fig,use_container_width=True) #, height = 200)

with col2:
    st.subheader("Prix médian par nuit")
    fig = px.box(filtered_df, x="Number Room", y='euros', template = "seaborn") #template="gridon"
    fig.update_layout(yaxis_title="Prix € par nuit", xaxis_title = "Nombre de chambres")
    st.plotly_chart(fig,use_container_width=True)

with col3:
    st.subheader("Prix moyen par nuit")
    rooms = filtered_df.groupby(by = "Number Room", as_index = False)['euros'].mean()
    fig = px.box(rooms, x="Number Room", y='euros', template = "seaborn") #template = "plotly_dark"
    fig.update_layout(yaxis_title="Prix € par nuit", xaxis_title = "Nombre de chambres")
    st.plotly_chart(fig,use_container_width=True)


st.subheader("Localisation des biens")
fig = px.scatter_mapbox(filtered_df, lat="latitude", lon="longitude", color="euros", color_continuous_scale=px.colors.cyclical.IceFire,
                       size_max=15, zoom=11,mapbox_style="carto-positron")
st.plotly_chart(fig,use_container_width=True, height = 500, width = 1000)

st.subheader("Repartition des biens")
rooms = filtered_df.groupby(by = "Number Room", as_index = False)['Title'].count()
fig = px.pie(rooms, values='Title', names='Number Room')
st.plotly_chart(fig,use_container_width=True)

with st.expander("View_Data"):
    rooms = filtered_df.groupby(by = "Number Room", as_index = False)['Title'].count()
    #st.write(rooms.style.background_gradient(cmap="Blues"))
    st.write(rooms) #.style.background_gradient(cmap="Oranges"))
    #csv = region.to_csv(index = False)   #.encode('utf-8')
    # Sauvegardez le DataFrame au format CSV en spécifiant l'encodage
    csv = rooms.to_csv(index=False) #region.to_csv('nom_du_fichier.csv', index=False)
    st.download_button("Download Data", data = csv, mime = "text/csv",
                    help = 'Click here to download the data as a CSV file') #, file_name = "Bien par chambre.csv"
