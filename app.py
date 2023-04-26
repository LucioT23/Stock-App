import streamlit as st
import pandas as pd
import numpy as np 
from datetime import datetime 
import streamlit as st
import plotly.express as px
import base64

pd.set_option('display.max_row',111)
pd.set_option('display.max_column',111)


############################################ Fonctions ###################################
def nb_actif(df,df_Tosca):
  df_test = df.copy()
  df_Tosca = df_Tosca.rename(columns={'fk_code_grp':'Code groupe DISE'})
  df_Tosca_test = df_Tosca[['Code groupe DISE','nb_actif']]

  # Création d'un dictionnaire avec les codes et le nombre d'actif correspondant
  actif_par_code = dict(zip(df_Tosca_test['Code groupe DISE'], df_Tosca_test['nb_actif']))

  def calculer_actif(codes):
      codes = [int(c) for c in codes.split(',')]
      return sum(actif_par_code.get(c, 0) for c in codes)

  df_test["Nb_actifs"] = df_test['Code groupe DISE'].apply(calculer_actif)
  return (df_test)

def nb_actif_2(df,df_Tosca):
  df_test = df.copy()
  df_test = df_test.loc[df_test['Code groupe DISE'] != '0']
  df_Tosca = df_Tosca.rename(columns={'fk_code_grp':'Code groupe DISE'})
  df_Tosca_test = df_Tosca[['Code groupe DISE','nb_actif']]

  #### Suppression des codes groupes de df_test non présent dans le dataframe df_Tosca_test car généère des erreurs
  # Convertir les chaînes de caractères de codes en listes de codes dans df_test
  df_test['Code groupe DISE'] = df_test['Code groupe DISE'].str.split(',')

  # Convertir les chaînes de caractères de codes en str dans df_Tosca_test
  df_Tosca_test['Code groupe DISE'] = df_Tosca_test['Code groupe DISE'].astype(str)

  # Convertir les chaînes de caractères de codes en listes de codes dans df_Tosca_test
  df_Tosca_test['Code groupe DISE'] = df_Tosca_test['Code groupe DISE'].str.split(',')

  # Trouver les codes présents dans df_Tosca_test
  codes_tosca = set([code.strip() for codes_list in df_Tosca_test['Code groupe DISE'] for code in codes_list])

  # Sélectionner les lignes de df_test avec des codes présents dans df_Tosca_test
  df_test = df_test[df_test['Code groupe DISE'].apply(lambda x: any(code.strip() in codes_tosca for code in x))]

  # Convertir la liste en chaine de caractère dans la colonne 'Code groupe DISE'
  df_test['Code groupe DISE'] = df_test['Code groupe DISE'].apply(lambda x : ','.join(map(str,x)))

  # Renommer la colonne 'fk_code_grp' en 'Code groupe DISE' dans df_Tosca
  df_Tosca = df_Tosca.rename(columns={'fk_code_grp': 'Code groupe DISE'})
  df_Tosca_test = df_Tosca[['Code groupe DISE', 'nb_actif']]
 
  # Créer un dictionnaire avec les codes et le nombre d'actifs correspondant
  actif_par_code = dict(zip(df_Tosca_test['Code groupe DISE'], df_Tosca_test['nb_actif']))

  def calculer_actif(codes):
      codes = [int(c) for c in codes.split(',')]
      return sum(actif_par_code.get(c, 0) for c in codes)

  df_test["Nb_actifs"] = df_test['Code groupe DISE'].apply(calculer_actif)
  return (df_test)

#####################
def cleaning_data(df):
  
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
  
  # replace NaN by 0
  df["Code groupe DISE"] = df["Code groupe DISE"].fillna("0")

  # Replace ',' '/' and '-' with ';'
  df["Code groupe DISE"] = df["Code groupe DISE"].str.replace(r'[,/-]', ';')
  #df["Code groupe DISE"] = df["Code groupe DISE"].astype(str).apply(lambda x: [int(i) for i in x.split(';')])
  
  # conversion de la colonne en liste d'entiers
  def convert_list(x):
        try:
            return [int(i) for i in x.split(';') if i.isdigit()]
        except ValueError:
            return []

  df["Code groupe DISE"] = df["Code groupe DISE"].astype(str).apply(convert_list)
  df["Code groupe DISE"]  = df["Code groupe DISE"] .astype(str)
  df["Code groupe DISE"]  = df["Code groupe DISE"] .str.replace('[', '').str.replace(']', '')

  df['quarter'] = pd.PeriodIndex(df['date Kick-off Interne'], freq='Q').strftime(' %YQ%q')
  df['quarterc'] = df['quarter'].astype('string')

  #calcul du délais
  # Calcul du délai en mois avec fraction de mois
  df['delivery_time_month'] = ((df['date Vie de Solution'].dt.year - df['date Kick-off Interne'].dt.year) * 12 + (df['date Vie de Solution'].dt.month - df['date Kick-off Interne'].dt.month) + (df['date Vie de Solution'].dt.day - df['date Kick-off Interne'].dt.day) / 30)

  # Arrondir le résultat à un dixième près
  df['delivery_time_month'] = df['delivery_time_month'].apply(lambda x: round(x, 1))

  df = df[df['Statut']!='Contrat Perdu']
  #df['trimestre_deployé'] = pd.PeriodIndex(df['date Vie de Solution'], freq='Q')
  df['trimestre_deployé'] = pd.PeriodIndex(df['date Vie de Solution'], freq='Q').strftime(' %YQ%q')

  return (df)

#####################
def data_by_trimestre(df):

  df_deploiement2 = df[(df['statut deploiement']=='Déployé') | (df['statut deploiement']=='En cours')]
  data_test = df_deploiement2.copy()
  data_test = data_test[['title','Code groupe DISE','quarterc','date Vie de Solution','trimestre_deployé', 'Portail déployée','statut deploiement','Nb_actifs']]
  
  # Trier le DataFrame selon la colonne trimestre_deployé
  trimestres = sorted(data_test['trimestre_deployé'].dropna().unique())

  new_data = pd.DataFrame()  # créer un DataFrame vide

  # boucler sur chaque trimestre
  for t in trimestres:
    #print(t)
    df_t = data_test[data_test['trimestre_deployé'] <= t]
    df_t['trimestre_digital'] = t #deployé
    new_data = pd.concat([new_data, df_t])
    new_data = new_data.sort_values(by=['trimestre_digital','title']).reset_index(drop=True)
    new_data['trimestre_digital'] = new_data['trimestre_digital'].astype('string')

  new_data['title'] = new_data['title'].str.title()
  
  # Créer une nouvelle colonne 'migré' initialement à False
  new_data['migré'] = False

  # Créer une colonne 'new_portail' pour stocker le nouveau portail migré
  new_data['old_portail'] = ''
  old_portail_history = ""

  # Grouper les données par client
  grouped = new_data.groupby('Code groupe DISE') # instead of 'title'


  #old_portail_history= None
  for name, group in grouped:
      
      # Obtenir les portails déployés par le client dans l'ordre chronologique
      portails_deployes = group.sort_values('trimestre_digital')['Portail déployée'] #deployé

      # Vérifier si le client a été migré pour chaque trimestre
      for i in range(len(portails_deployes)):
          if i!=0:
            if portails_deployes.iloc[i] != portails_deployes.iloc[i-1]:
                old_portail = portails_deployes.iloc[i-1]
                if old_portail_history == "":
                    old_portail_history = old_portail

                new_data.loc[(new_data['Code groupe DISE'] == name) & (new_data['trimestre_digital'] == group.iloc[i]['trimestre_digital'])
                 & (new_data['Portail déployée'] == group.iloc[i]['Portail déployée']), 'migré'] = True
                new_data.loc[(new_data['Code groupe DISE'] == name) & (new_data['trimestre_digital'] == group.iloc[i]['trimestre_digital'])
                 & (new_data['Portail déployée'] == group.iloc[i]['Portail déployée']), 'old_portail'] = old_portail_history #portails_deployes.iloc[i-1]  

      old_portail_history = ""

  to_remove=[]

  # Créer une nouvelle colonne 'migré' initialement à False
  new_data['to_remove'] = False

  # Grouper les données par client
  grouped = new_data.groupby('Code groupe DISE')

  for name, group in grouped:
    old_portail_deployes = group.loc[(new_data['Code groupe DISE'] == name) & (new_data['old_portail'] !='')]

    for i in range(len(old_portail_deployes)): #-1
      if old_portail_deployes.iloc[i]['Portail déployée'] == old_portail_deployes.iloc[i]['old_portail']:
        old_portail = old_portail_deployes.iloc[i]['Portail déployée'] 
        new_data.loc[(new_data['Code groupe DISE'] == name)
         & (new_data['Portail déployée'] == old_portail)
         & (new_data['old_portail'] == group.iloc[i]['Portail déployée']),'to_remove']=True

  new_data = new_data.drop(new_data[new_data['to_remove'] == True].index)

  # Grouper les données par client
  grouped = new_data.groupby('Code groupe DISE')

  for name, group in grouped:
      portail_deployes = group.loc[(new_data['Code groupe DISE'] == name)]
      for i in range(len(portail_deployes)-1): #-1
          if (portail_deployes.iloc[i]['trimestre_digital'] == portail_deployes.iloc[i+1]['trimestre_digital']) and (portail_deployes.iloc[i+1]['migré'] == True):
              new_data.loc[(new_data['Code groupe DISE'] == name) & (new_data['migré'] == False) 
              & (new_data['trimestre_digital'] == group.iloc[i]['trimestre_digital']),'to_remove']=True
  
  new_data = new_data.drop(new_data[new_data['to_remove'] == True].index)

  return (new_data)

#####################
def Client_MWM_EWOCS (df, data):
  # déploiement en cours GLM AC extrait du fichier Kantree
  df_ongoing_deploiement_GLMAC = df[(df['statut deploiement']=='En cours') & (df['Portail déployée']=='GLM AC')]
  df_ongoing_deploiement_GLMAC['title'] = df_ongoing_deploiement_GLMAC['title'].str.title()

  # Obtenir la plus récente valeur de la colonne 'trimestre_digital'
  plus_recente = data['trimestre_digital'].max()

  # Clients déployés GLM AC
  data_deploiement = data[(data['trimestre_digital']==plus_recente)] #&(data['Portail déployée']=='GLM AC')]

  # Créer un nouveau dataframe avec les lignes à ajouter
  new_rows = pd.DataFrame({
      'title': df_ongoing_deploiement_GLMAC['title'],
      'Code groupe DISE': df_ongoing_deploiement_GLMAC['Code groupe DISE'],
      'quarterc': df_ongoing_deploiement_GLMAC['quarterc'],
      'date Vie de Solution': df_ongoing_deploiement_GLMAC['date Vie de Solution'],
      'trimestre_deployé': df_ongoing_deploiement_GLMAC['trimestre_deployé'],
      'Portail déployée': df_ongoing_deploiement_GLMAC['Portail déployée'],
      'statut deploiement': df_ongoing_deploiement_GLMAC['statut deploiement'],
      'Nb_actifs': df_ongoing_deploiement_GLMAC['Nb_actifs'],
      'trimestre_digital': plus_recente, # Ajouter une colonne avec une valeur fixe pour tous les nouveaux enregistrements
      'migré': False,
      'old_portail': df_ongoing_deploiement_GLMAC['Portail existant'],
      'to_remove': False
  })

  # Ajouter les nouvelles lignes au dataframe existant
  data_deploiement_GLMAC = pd.concat([data_deploiement, new_rows], ignore_index=True)

  data_deploiement_GLMAC['old_portail'] = data_deploiement_GLMAC['old_portail'].str.upper()
  data_deploiement_GLMAC = data_deploiement_GLMAC[~data_deploiement_GLMAC['title'].isin(['Veolia Sade', 'Grdf', 'Cofely'])]

  resultats = {}
  for portail in ['MWM', 'EWOCS']:
      filtre = ((data_deploiement_GLMAC['Portail déployée']==portail)
      | (data_deploiement_GLMAC['old_portail']==portail)) #(data_deploiement_GLMAC['trimestre_digital']==plus_recente) & 
      resultats[portail] = data_deploiement_GLMAC[filtre]

      # créer une nouvelle colonne 'état' basée sur la colonne 'statut deploiement'
      resultats[portail]['état'] = resultats[portail].apply(lambda row: row['Portail déployée'] if row['statut deploiement'] == 'Déployé' 
                                                            else 'En cours de déploiement' if row['Portail déployée'] == 'GLM AC' else None, axis=1)
  return (resultats)

######################
# Clients MWM sous GLM AC

def client_MWM(df_mwm, df_Planning_data, plus_recente):

  # Clients MWM non déployés sous GLM AC
  # Filtrer les lignes avec 'état' == 'MWM'
  df_mwm_filtered = df_mwm[df_mwm['état'] == 'MWM'].copy()

  # Convertir les trimestres de la colonne 'quarterc' en trimestres de la forme 'YYYYQN'
  df_Planning_data['quarterc'] = pd.PeriodIndex(pd.to_datetime(df_Planning_data['Kickoff GLM AC']), freq='Q').astype(str)

  # Regrouper les trimestres de la colonne 'quarterc' par 'Code DISE'
  quarterc_dict = df_Planning_data.groupby('Code DISE')['quarterc'].agg(lambda x: sorted(set(x))).to_dict()

  # Ajouter la colonne 'trimestre_deployable' en utilisant les valeurs de la colonne 'quarterc' du dataframe 'df_Planning_data'
  df_mwm_filtered['trimestre_deployable_GLM'] = df_mwm_filtered['Code groupe DISE'].map(quarterc_dict)
  df_mwm_filtered['trimestre_deployable_GLM'] = df_mwm_filtered['Code groupe DISE'].map(quarterc_dict)

  # Remplacer les valeurs nulles par des chaînes vides
  df_mwm_filtered['trimestre_deployable_GLM'] = df_mwm_filtered['trimestre_deployable_GLM'].fillna('')
  df_mwm_filtered['trimestre_deployable_GLM'] = df_mwm_filtered['trimestre_deployable_GLM'].apply(lambda x: pd.Period(x[0], freq='Q') if len(x)>0 else pd.NaT)
  df_mwm_filtered = df_mwm_filtered.dropna(subset=['trimestre_deployable_GLM'])
  
  # Convertir les valeurs de la colonne en chaînes de caractères
  df['trimestre_deployable_GLM'] = df['trimestre_deployable_GLM'].astype(str)

  # Convertir les chaînes de caractères en objets périodiques
  periods = pd.PeriodIndex(df['trimestre_deployable_GLM'], freq='Q')

  # Formater la date de sortie au format "YYYYQx"
  df['trimestre_deployable_GLM'] = periods.strftime('%YQ%q')

  st.write(df_mwm_filtered)

  # Obtenir la plus récente valeur de la colonne 'trimestre_digital'
  # plus_recente = data['trimestre_digital'].max()

  # clients MWM en déploiement GLM AC
  test = df_mwm[df_mwm['état'] != 'MWM'].copy()
  test['trimestre_deployable_GLM'] = test['trimestre_deployable_GLM'].fillna(plus_recente)
  #test['trimestre_deployable_GLM'] = pd.to_datetime(test['trimestre_deployable_GLM'], format='%YQ%q', errors='coerce').dt.to_period('Q').astype(str)
  #test['trimestre_deployable_GLM'] = pd.to_datetime(test['trimestre_deployable_GLM']).dt.to_period('Q').astype(str)


  # Ajout des lignes de df2 à df1 en utilisant append()
  df_concat = test.append(df_mwm_filtered)
  
  return(df_concat)
###############################################################################

st.title('Digital Deployment')

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
        #df['delivery_time'] = (df['date Vie de Solution']-df['date Kick-off Interne']).dt.days
        #df['delivery_time_month'] = df['date Vie de Solution'].dt.to_period('M').astype(float) - df['date Kick-off Interne'].dt.to_period('M').astype(float)
        
        # Calcul du délai en mois avec fraction de mois
        df['delivery_time_month'] = ((df['date Vie de Solution'].dt.year - df['date Kick-off Interne'].dt.year) * 12 + (df['date Vie de Solution'].dt.month - df['date Kick-off Interne'].dt.month) + (df['date Vie de Solution'].dt.day - df['date Kick-off Interne'].dt.day) / 30)
        
        # Arrondir le résultat à un dixième près
        df['delivery_time_month'] = df['delivery_time_month'].apply(lambda x: round(x, 1))
  
        df = df[df['Statut']!='Contrat Perdu']
        df['trimestre_deployé'] = pd.PeriodIndex(df['date Vie de Solution'], freq='Q')
        # sauvegarde + affichage
        df.to_csv('dataset.csv', index=None)
        st.dataframe(df)

    ### Fichier Parc TOSCA ###
    st.header("Download Your Tosca Dataset") # ou st.subheader()
    file_Tosca = st.file_uploader("Download Your File", key="2")
    if file_Tosca: 
        df_Tosca = pd.read_csv(file_Tosca, sep=';', warn_bad_lines=True,error_bad_lines=False)
        df_Tosca.to_csv('dataset_Tosca.csv', index=None)
        st.dataframe(df_Tosca)

    ### Fichier Planning ###
    st.header("Download Your Planning Dataset")
    file_plan = st.file_uploader("Download Your File", key="3")
    if file_plan: 
        df_Planning = pd.read_csv(file_plan, sep=';', warn_bad_lines=True,error_bad_lines=False)
        #df_Planning = pd.read_csv(file_plan, sep=';', skiprows=1, warn_bad_lines=True, error_bad_lines=False)
        df_Planning['nom_client'] = df_Planning['nom_client'].str.title()
        df_Planning_data = df_Planning[['nom_client','Code DISE','Kickoff GLM AC','Déployé ou non','Cause : Pas déployé','Causes de regression / API/ autres']]
        df_Planning_data.to_csv('dataset_Planning.csv', index=None)
        st.dataframe(df_Planning_data)


if choice == "GLM AC deployment":
        st.header('GLM AC deployment')
        df = pd.read_csv('dataset.csv', index_col=None)
        df_non_deployed = df[df['statut deploiement'].isin(['Non déployé'])]
        df_deployed = df[df['statut deploiement'].isin(['Déployé'])]
        df_ongoing = df[df['statut deploiement'].isin(['En cours'])]
        df_deploiement = df[(df['statut deploiement']=='Déployé') | (df['statut deploiement']=='En cours')]
        df_deploiement = df_deploiement[df_deploiement['Portail déployée']=='GLM AC']
        df_deploiement = df_deploiement.sort_values(by='quarterc', ascending=True)
        df_deploiement['delivery_time_month'] = df_deploiement['delivery_time_month'].round(1)

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

        df_digit_GLMAC= df[(df['statut deploiement'].isin(['En cours']))&(df['Portail déployée']=='GLM AC')]
        counts_GLMAC = df_digit_GLMAC['Portail existant'].value_counts()

        # plotting the pie chart
        fig10 = px.pie(df_digit_GLMAC, names=counts_GLMAC.index, values =counts_GLMAC,width=800, height=400) # names=counts.index
        fig10.update_traces(textinfo="percent+label+value")
        #Ajout Statut déploiement par date de Kickoff (GLM AC) par client
        st.subheader("Répartition des déploiements GLM AC en cours par portail initial")
        st.write(fig10)

        df_deploiement_mean = pd.DataFrame(df_deploiement.groupby(['quarterc'])['delivery_time_month'].mean()).reset_index()
        df_deploiement_mean['delivery_time_month'] = df_deploiement_mean['delivery_time_month'].round(1)

        # plotting the histogram
        fig1 = px.histogram(df_deploiement_mean, x="quarterc", y="delivery_time_month",title="Durée de déploiement par Trimestre")
        fig1.update_layout(height=400,width =800, yaxis_title="délai de déploiement",xaxis_title="Trimestre")
        
        #Ajout Graph Durée des deploiements GLM AC
        st.subheader("Durée des deploiements GLM AC")
        st.write(fig1)

        data3 = df_deploiement.dropna(subset=['delivery_time_month'])
        data3['delivery_time_month'] = data3['delivery_time_month'].round(1)
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
        st.header('GLM AC Customer Migration')

        df = pd.read_csv('dataset.csv', index_col=None)
        df_Tosca = pd.read_csv('dataset_Tosca.csv', index_col=None)

        df_Tosca = df_Tosca.rename(columns={'fk_code_grp':'Code groupe DISE'})
        df_Tosca = df_Tosca[['Code groupe DISE','nb_actif']]

        # Création d'un dictionnaire avec les codes et le nombre d'actif correspondant
        actif_par_code = dict(zip(df_Tosca['Code groupe DISE'], df_Tosca['nb_actif']))

        def calculer_actif(codes):
            if isinstance(codes, list):
                codes = [int(c.strip("[]")) for c in codes]
            elif isinstance(codes, str):
                codes = [int(c) for c in codes.strip("[]").split(',')]
            else:
                return 0
            return sum(actif_par_code.get(c, 0) for c in codes)

        df["Nb_actifs"] = df['Code groupe DISE'].apply(calculer_actif)

        df_deploiement2 = df[(df['statut deploiement']=='Déployé') | (df['statut deploiement']=='En cours')]             
        data_test = df_deploiement2.copy()
        data_test = data_test[['title','Code groupe DISE','quarterc','date Vie de Solution','trimestre_deployé', 'Portail déployée','statut deploiement','Nb_actifs']]
        
        trimestres = sorted(data_test.dropna(subset=['trimestre_deployé'])['trimestre_deployé'].unique())

        new_data = pd.DataFrame()  # créer un DataFrame vide

        # boucler sur chaque trimestre
        for t in trimestres:
          df_t = data_test[data_test['trimestre_deployé'] <= t]
          df_t['trimestre_digital'] = t #deployé
          new_data = pd.concat([new_data, df_t])
          new_data = new_data.sort_values(by=['trimestre_digital','title']).reset_index(drop=True)
          new_data['trimestre_digital'] = new_data['trimestre_digital'].astype('string')

        new_data['title'] = new_data['title'].str.title()

        # Créer un dictionnaire qui stocke les valeurs complètes pour chaque client
        complete_codes = {}
        for index, row in new_data.iterrows():
            client = row['title']
            code = row['Code groupe DISE']
            if ',' not in code:
                if client in complete_codes:
                    code = complete_codes[client]
                else:
                    continue
            else:
                complete_codes[client] = code

        # Compléter les codes manquants pour chaque client
        for index, row in new_data.iterrows():
            client = row['title']
            code = row['Code groupe DISE']
            if ',' not in code:
                if client in complete_codes:
                    new_data.at[index, 'Code groupe DISE'] = complete_codes[client]

        # Créer une nouvelle colonne 'migré' initialement à False
        new_data['migré'] = False

        # Créer une colonne 'new_portail' pour stocker le nouveau portail migré
        new_data['old_portail'] = ''

        # Grouper les données par client
        grouped = new_data.groupby('Code groupe DISE') # instead of 'title'

        #old_portail_history= None
        for name, group in grouped:
            
            # Obtenir les portails déployés par le client dans l'ordre chronologique
            portails_deployes = group.sort_values('trimestre_digital')['Portail déployée'] #deployé

            # Vérifier si le client a été migré pour chaque trimestre
            for i in range(len(portails_deployes)):
                if i!=0:
                  if portails_deployes.iloc[i] != portails_deployes.iloc[i-1]:
                      old_portail = portails_deployes.iloc[i-1]
                      if old_portail_history == "":
                        old_portail_history = old_portail 

                      new_data.loc[(new_data['Code groupe DISE'] == name) & (new_data['trimestre_digital'] == group.iloc[i]['trimestre_digital']) & (new_data['Portail déployée'] == group.iloc[i]['Portail déployée']), 'migré'] = True
                      new_data.loc[(new_data['Code groupe DISE'] == name) & (new_data['trimestre_digital'] == group.iloc[i]['trimestre_digital']) & (new_data['Portail déployée'] == group.iloc[i]['Portail déployée']), 'old_portail'] = old_portail_history #portails_deployes.iloc[i-1]  

            old_portail_history = ""

        to_remove=[]

        # Créer une nouvelle colonne 'migré' initialement à False
        new_data['to_remove'] = False

        # Grouper les données par client
        grouped = new_data.groupby('Code groupe DISE')

        for name, group in grouped:

          old_portail_deployes = group.loc[(new_data['Code groupe DISE'] == name) & (new_data['old_portail'] !='')]

          for i in range(len(old_portail_deployes)): 
            if old_portail_deployes.iloc[i]['Portail déployée'] == old_portail_deployes.iloc[i]['old_portail']:
              old_portail = old_portail_deployes.iloc[i]['Portail déployée'] 
              new_data.loc[(new_data['Code groupe DISE'] == name) & (new_data['Portail déployée'] == old_portail) & (new_data['old_portail'] == group.iloc[i]['Portail déployée']),'to_remove']=True

        new_data = new_data.drop(new_data[new_data['to_remove'] == True].index)

        # Grouper les données par client
        grouped = new_data.groupby('Code groupe DISE')

        for name, group in grouped:
            portail_deployes = group.loc[(new_data['Code groupe DISE'] == name)]
            for i in range(len(portail_deployes) - 1):
                if (portail_deployes.iloc[i]['trimestre_digital'] == portail_deployes.iloc[i+1]['trimestre_digital']) and (portail_deployes.iloc[i+1]['migré'] == True):
                    new_data.loc[(new_data['Code groupe DISE'] == name) & (new_data['migré'] == False) & (new_data['trimestre_digital'] == group.iloc[i]['trimestre_digital']),'to_remove']=True

        new_data = new_data.drop(new_data[new_data['to_remove'] == True].index)

        # Obtenir la plus récente valeur de la colonne 'trimestre_digital'
        plus_recente = new_data['trimestre_digital'].max()
        
        # Ajout pie graph pour les clients GLM AC migrés 
        df_migrated = new_data[(new_data['trimestre_digital']==plus_recente) & (new_data['Portail déployée']=='GLM AC')]
        for i, val in enumerate(df_migrated['Portail déployée']):
          if df_migrated['old_portail'].iloc[i] == '':
                df_migrated['old_portail'].iloc[i]= df_migrated['Portail déployée'].iloc[i]

        counts = df_migrated['old_portail'].value_counts()

        # plotting the pie chart
        fig11 = px.pie(df_migrated, names=counts.index, values =counts,width=800, height=400) # names=counts.index
        fig11.update_traces(textinfo="percent+label+value")
        # Ajout Statut déploiement par date de Kickoff (GLM AC) par client
        st.subheader("Répartition des déploiements GLM AC par portail initial")
        st.write(fig11)


        count_portail_migre = pd.DataFrame(new_data.groupby(['trimestre_digital','Portail déployée'])['Code groupe DISE'].count()).reset_index()
        count_portail_migre = count_portail_migre.rename(columns={'Code groupe DISE': 'nb déploiement par portail'})

        fig5 = px.scatter(new_data, x="trimestre_digital",y="Code groupe DISE", hover_name="title",color="Portail déployée") 
        fig5.update_layout(height=500,width =900, yaxis_title=None,xaxis_title="Trimestre")

        #Ajout Statut déploiement par date de Kickoff (GLM AC) par client
        st.subheader("Déploiement Digital par Client")
        st.write(fig5) 

        # Réorganiser les données
        df_pivot = pd.pivot_table(count_portail_migre, 
                                  values='nb déploiement par portail', 
                                  index='trimestre_digital', 
                                  columns='Portail déployée', 
                                  fill_value=0, 
                                  aggfunc='sum')

        # Réinitialiser l'index et convertir la colonne en trimestres
        df_pivot = df_pivot.reset_index()
        df_pivot['trimestre_digital'] = pd.to_datetime(df_pivot['trimestre_digital']).dt.to_period('Q')

        # Convertir les données en format long
        df_long_quarter = pd.melt(df_pivot, id_vars=['trimestre_digital'], var_name='Portail déployé', value_name='nb de portail')
        df_long=df_long_quarter.copy()
        df_long['trimestre_digital'] = df_long_quarter['trimestre_digital'].dt.strftime('%Y-%m-%d')

        fig6 = px.bar(df_long, x="trimestre_digital", y='nb de portail', color='Portail déployé', text='nb de portail')
        fig6.update_layout(height=400,width =800)

        #Ajout Statut déploiement par date de Kickoff (GLM AC) par client
        st.subheader("Déploiement Digital par portail")
        st.write(fig6) 

        df_long = df_long.sort_values('trimestre_digital')

        fig7 = px.bar(df_long, x="Portail déployé", y='nb de portail',
             animation_frame="trimestre_digital", animation_group="Portail déployé",color = "Portail déployé",
             range_y=[0, df_long['nb de portail'].max()])
        fig7.update_layout(height=400,width =800)

        #Ajout du graphique animé sur la migration client sur les portails digitaux
        st.subheader("Migration des clients sur les portails Digitaux")
        st.write(fig7)

        st.header('Nombre de lignes Digitales')

        # ne prendre qu'une valeur si plusieurs ligne avec le même code DISE sur un même trimestre digital
        data_grouped = pd.DataFrame(new_data.groupby(['Code groupe DISE', 'trimestre_digital']).first().reset_index())
        data_grouped = data_grouped.sort_values('trimestre_digital')

        # plotting the bar plot for lines Digitalized
        fig12 = px.bar(data_grouped, x="trimestre_digital", y="Nb_actifs", hover_name='title',color='Portail déployée')
        fig12.update_layout(height=600,width =800, yaxis_title="Nb de lignes")
        st.write(fig12)

if choice == "Project Manager":
        st.header('Project Manager')

        df = pd.read_csv('dataset.csv', index_col=None)
        df_non_deployed = df[df['statut deploiement'].isin(['Non déployé'])]
        df_deployed = df[df['statut deploiement'].isin(['Déployé'])]
        df_ongoing = df[df['statut deploiement'].isin(['En cours'])]
        df_deploiement = df[(df['statut deploiement']=='Déployé') | (df['statut deploiement']=='En cours')]
        df_deploiement = df_deploiement[df_deploiement['Portail déployée']=='GLM AC']
        df_deploiement = df_deploiement.sort_values(by='quarterc', ascending=True)

        # plotting the bar plot
        fig8 = px.bar(df_deploiement.groupby(["Phase d'avancement"])['title'].count().reset_index(), x="Phase d'avancement", y='title')
        fig8.update_layout(height=400,width =800, yaxis_title="Nb de Client")

        #Ajout du graphique animé sur la migration client sur les portails digitaux
        st.subheader("Déploiement en cours par phase de déploiement")
        st.write(fig8) 
        
        df_avancement = pd.DataFrame(df_deploiement.groupby(["Phase d'avancement", 'title']).agg(sum_col1=("Phase d'avancement", 'sum')).reset_index())
        df_avancement = df_avancement.rename(columns={"Phase d'avancement": "Phase d'avancement", 'title': 'Clients'})
        df_avancement = df_avancement.drop(columns='sum_col1')
        st.write(df_avancement)

        # plotting the bar plot
        fig9 = px.bar(df_ongoing.groupby(["Chef de projet"])['title'].count().reset_index(), x="Chef de projet", y='title')
        fig9.update_layout(height=400,width =800, yaxis_title="Nb de Client")

        #Ajout du graphique animé sur la migration client sur les portails digitaux
        st.subheader("Nombre de déploiement en cours par CDP")
        st.write(fig9)

if choice == "Test":
        st.header('Test fonctions')
        st.header("Download Your Kantree Dataset") # ou st.subheader()
        file = st.file_uploader("Download Your File", key="1")
        if file: 
            df = pd.read_csv(file, index_col=None)
            df= df.drop(columns=['application déployée'])

        df.to_csv('dataset_test.csv', index=None)
        
        df_2 = pd.read_csv('dataset_test.csv', index_col=None)
        df_Tosca = pd.read_csv('dataset_Tosca.csv', index_col=None)
        df_Planning_data = pd.read_csv('dataset_Planning.csv', index_col=None)
        
        df_2 = cleaning_data(df_2)
        df_2 = nb_actif_2(df_2, df_Tosca)
        data = data_by_trimestre(df_2)
        
        # On sélectionne les lignes où la colonne "Phase d'avancement" est égale à "Pipe déploiement"
        mask = df_2["Phase d'avancement"] == 'Pipe déploiement'

        # On met à jour la colonne 'statut déploiement' pour les lignes sélectionnées
        df_2.loc[mask, 'statut deploiement'] = 'En cours'
        
        resultats = Client_MWM_EWOCS (df_2, data)

        ######## Clients MWM #############
        st.subheader('Clients MWM')
        df_mwm = resultats['MWM']

        # Créer une fonction pour supprimer les doublons dans la colonne 'état' pour chaque client dans la colonne 'title'
        def remove_duplicates(df):
            if 'état' in df.columns:
                if len(df['état'].unique()) > 1:
                    df = df.loc[df['état'] != 'MWM']
            return df

        # Appliquer la fonction personnalisée pour supprimer les doublons dans la colonne 'état' pour chaque client dans la colonne 'title'
        df_mwm = df_mwm.groupby('title').apply(remove_duplicates).reset_index(drop=True)
        df_mwm['trimestre_deployable_GLM']=df_mwm['quarterc']

        counts_MWM = df_mwm['état'].value_counts()
        
        st.write(df_mwm)
        
        # créer un graphique pie
        fig = px.pie(data_frame=df_mwm, #resultats['MWM']
                      values=counts_MWM.values,  # utiliser les valeurs de counts_MWM
                      names=counts_MWM.index,  # utiliser les noms de chaque état
                      hole=0.4,  # ajouter un trou au milieu du pie chart
                    width=800, height=400)  

        # ajouter un titre
        fig.update_layout(title_text='Répartition des clients MWM déployés ou en cours de déploiement sur GLM AC')
        fig.update_traces(textinfo="percent+label+value")

        # afficher le graphique
        #Ajout du graphique animé sur la migration client sur les portails digitaux
        st.subheader("Répartition des clients MWM déployés ou en cours de déploiement sur GLM AC")
        st.write(fig)

        # Obtenir la plus récente valeur de la colonne 'trimestre_digital'
        plus_recente = data['trimestre_digital'].max()
        
        df_concat= client_MWM(df_mwm, df_Planning_data, plus_recente)
        counts_MWM_GLM = df_concat['état'].value_counts()
        st.write(counts_MWM_GLM)

        # créer un graphique pie
        fig1 = px.pie(data_frame=df_concat,
                      values=counts_MWM_GLM.values,  # utiliser les valeurs de counts_MWM
                      names=counts_MWM_GLM.index,  # utiliser les noms de chaque état
                      hole=0.4,  # ajouter un trou au milieu du pie chart
                      width=800, height=400)  

        # ajouter un titre
        fig1.update_layout(title_text='Répartition des clients MWM déployés ou en cours de déploiement sur GLM AC')
        fig1.update_traces(textinfo="percent+label+value")
        st.subheader("Répartition des clients MWM déployés ou en cours de déploiement sur GLM AC : version 2")
        st.write(fig1)

        df_concat['trimestre_deployable_GLM'] = df_concat['trimestre_deployable_GLM'].astype(str)
        df_concat = df_concat.sort_values('trimestre_deployable_GLM')
        st.write(df_concat)
        fig2 = px.bar(df_concat, x='trimestre_deployable_GLM',
                      hover_name='title', text='title',color='état',
                      category_orders={'trimestre_deployable_GLM': ['2020Q2', '2021Q4', '2022Q2', '2022Q3','2022Q4','2023Q1','2023Q2','2023Q3','2023Q4','2024Q1','2024Q2','2024Q3']})
        
        fig2.update_layout(height=600,width =1200,xaxis_title="Trimestre (Kick off)",
                          yaxis_title="Nombre de déploiement",
                          title = "Planning prévisionnel de déploiement GLM AC pour les clients MWM")
        st.write(fig2)

        # Export CSV du fichier df_mwm
        if st.button('Exporter en CSV'):
          # Exportez le fichier CSV
          csv = df_mwm.to_csv(index=False)
          b64 = base64.b64encode(csv.encode()).decode()
          href = f'<a href="data:file/csv;base64,{b64}" download="donnees.csv">Télécharger le fichier CSV</a>'
          st.markdown(href, unsafe_allow_html=True)
