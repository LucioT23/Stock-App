import streamlit as st
import pandas as pd
import numpy as np 
from datetime import datetime 
import streamlit as st
import plotly.express as px

pd.set_option('display.max_row',111)
pd.set_option('display.max_column',111)


st.title('Digital Deployment')

with st.sidebar: 
    st.image("https://www.onepointltd.com/wp-content/uploads/2020/03/inno2.png")
    st.title("Mobile Client Fleet Check_ML")
    choice = st.radio("Navigation", ["Download","GLM AC deployment","Customer Migration", "Project Manager"])
    st.info("This project application helps you to have a complete vision of the digital deployments of our clients")

    
if choice == "Download":
    st.title("Download Your Dataset")
    file = st.file_uploader("Download Your File")
    if file: 
        df = pd.read_csv(file, index_col=None)
        df= df.drop(columns=['application déployée'])
        
        # Renome les portails avec des noms uniques (EWOCS/GLM AC/MWM)
        def rename_application(df):
          for i,val in enumerate(df['Application déployée']):
            #print(i,val)
            if val == 'MWM, MWM' or val == 'MWM':
              df.loc[i,'Portail déployée']='MWM'    
            elif val == 'EWOCS, EWOCS' or val =='EWOCS':
              df.loc[i,'Portail déployée']='EWOCS'
            elif val == 'GLM AC, GLM AC' or val == 'GLM AC, MWM' or val == 'GLM AC, EWOCS' or val =='GLM AC' or val =='HUG':
              df.loc[i,'Portail déployée']='GLM AC'
          return df

        df= rename_application(df)

        # tranfo en date toutes les colonnes avec un format date
        date_columns = [col for col in df.columns if 'date' in col]
        for col in date_columns :
          df[col]= pd.to_datetime(df[col],format='%Y %m %d')

        today = datetime.now().date()
        today = pd.to_datetime(today,format='%Y %m %d')

        # MAJ du statut de déploiement
        def statut(row):
            if pd.notnull(row['date Vie de Solution']) and row['date Vie de Solution'].date() < today:
                return 'Déployé'
            elif pd.notnull(row['date Kick-off Interne']) and pd.isnull(row['date Vie de Solution']):
                if row['Statut'] == 'Stand by':
                    return 'Non déployé'
                else:
                    return 'En cours'
            else:
                return 'Non déployé'

        df['statut deploiement'] = df.apply(statut, axis=1)

        # select not renouvellement ou avenant
        df = df[df['Renouvellement'].isna()]
        #df = df[df['Portail déployée']!='GLM AC]]['Renouvellement'].isna()

        # replace NaN by 0
        df["Code groupe DISE"] = df["Code groupe DISE"].fillna("0")

        # Replace ',' '/' and '-' with ';'
        df["Code groupe DISE"] = df["Code groupe DISE"].str.replace(r'[,/-]', ';')
        df["Code groupe DISE"] = df["Code groupe DISE"].astype(str).apply(lambda x: [int(i) for i in x.split(';')])

        df['quarter'] = pd.PeriodIndex(df['date Kick-off Interne'], freq='Q')
        df['quarterc'] = df['quarter'].astype('string')

        #calcul du délais
        df['delivery_time'] = (df['date Vie de Solution']-df['date Kick-off Interne']).dt.days

        # Conversion en semaines
        df['delivery_time_week'] = round(df['delivery_time'] / 7)
        # Calcul de la différence en mois
        df['delivery_time_month'] = (df['date Vie de Solution'].dt.year - df['date Kick-off Interne'].dt.year) * 12 + (df['date Vie de Solution'].dt.month - df['date Kick-off Interne'].dt.month)

        df = df[df['Statut']!='Contrat Perdu']
        # sauvegarde + affichage
        df.to_csv('dataset.csv', index=None)
        st.dataframe(df)

if choice == "GLM AC deployment":

        df = pd.read_csv('dataset.csv', index_col=None)
        df_non_deployed = df[df['statut deploiement'].isin(['Non déployé'])]
        df_deployed = df[df['statut deploiement'].isin(['Déployé'])]
        df_ongoing = df[df['statut deploiement'].isin(['En cours'])]
        df_deploiement = df[(df['statut deploiement']=='Déployé') | (df['statut deploiement']=='En cours')]
        df_deploiement = df_deploiement[df_deploiement['Portail déployée']=='GLM AC']
        df_deploiement = df_deploiement.sort_values(by='quarterc', ascending=True)

        counts = df_ongoing['Portail déployée'].value_counts()

        # plotting the pie chart
        fig = px.pie(df_ongoing, names=counts.index, values =counts,width=800, height=400) # names=counts.index
        fig.update_traces(textinfo="percent+label+value")
        #fig.update_layout(width=int(500))
        # showing the plot
        #fig.show()

        #Ajout Graph Deploiement en cours
        st.subheader("Déploiement en cours")
        st.write(fig)

        df_deploiement_mean = pd.DataFrame(df_deploiement.groupby(['quarterc'])['delivery_time_month'].mean()).reset_index()

        # plotting the histogram
        fig1 = px.histogram(df_deploiement_mean, x="quarterc", y="delivery_time_month",title="Durée de déploiement par Trimestre")
        fig1.update_layout(height=400,width =800, yaxis_title="délai de déploiement",xaxis_title="Trimestre")
        
        #Ajout Graph Durée des deploiements GLM AC
        st.subheader("Durée des deploiements GLM AC")
        st.write(fig1)

        data3 = df_deploiement.dropna(subset=['delivery_time_month'])
        fig2 = px.scatter(data3, x="quarterc", y="delivery_time_month", text="title")
        #fig2.update_traces(textposition='top center')
        fig2.update_layout(
            height=600,width=800,
            title_text='Durée de déploiement par trimestre (GLM AC)', yaxis_title="délai de déploiement",xaxis_title="Trimestre")
        
        def improve_text_position(x):
          positions = ['top center','top right', 'bottom center', 'bottom left']  # you can add more: left center ...
          return [positions[i % len(positions)] for i in range(len(x))]

        fig2.update_traces(textposition=improve_text_position(data3["quarterc"]))

        #Ajout Graph Durée des deploiements GLM AC par client déployés
        st.subheader("Durée des deploiements GLM AC par client déployé")
        st.write(fig2)

        # plotting the histogram
        fig3 = px.histogram(df_deploiement, x="quarterc",color='statut deploiement', title="Statut déploiement par date de Kickoff (GLM AC)")
        fig3.update_layout(height=400,width =900, yaxis_title="Nb déploiement",xaxis_title="Trimestre")
        

        #Ajout Graph Statut déploiement par date de Kickoff (GLM AC)
        st.subheader("Statut déploiement par date de Kickoff (GLM AC)")
        st.write(fig3)

        fig4 = px.scatter(df_deploiement.reset_index(), x="quarterc",color='statut deploiement', text="title")
        fig4.update_traces(textposition='top center')
        fig4.update_layout(height=800,width=800,
            title_text='Statut déploiement par date de Kickoff (GLM AC) par client', yaxis_title="Client",xaxis_title="Trimestre")

        #Ajout Statut déploiement par date de Kickoff (GLM AC) par client
        st.subheader("Statut déploiement par date de Kickoff (GLM AC) par client")
        st.write(fig4)

if choice == "Customer Migration":

        df = pd.read_csv('dataset.csv', index_col=None)
        df_deploiement2 = df[(df['statut deploiement']=='Déployé') | (df['statut deploiement']=='En cours')]
        data_test = df_deploiement2.copy()
        data_test = data_test[['title','Code groupe DISE','quarterc','date Vie de Solution','trimestre_deployé', 'Portail déployée','statut deploiement']]

        trimestres = sorted(data_test['trimestre_deployé'].unique())

        new_data = pd.DataFrame()  # créer un DataFrame vide

        # boucler sur chaque trimestre
        for t in trimestres:
          df_t = data_test[data_test['trimestre_deployé'] <= t]
          df_t['trimestre_digital'] = t #deployé
          new_data = pd.concat([new_data, df_t])
          new_data = new_data.sort_values(by=['trimestre_digital','title']).reset_index(drop=True)
          new_data['trimestre_digital'] = new_data['trimestre_digital'].astype('string')

        new_data['title'] = new_data['title'].str.title()

        st.dataframe(new_data)
        
