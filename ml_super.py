import streamlit as st
import pandas as pd
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import mysql.connector
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error
from joblib import dump, load
from datetime import date
import sys

# ce fichier fait partie de Streamlit il permet de faire des Prédiction en fonction
# des dernières modèles ainsi qu'en choissant des Paramètres telle que l'auteur, le type et l'éditeur

#modification de la variable host entre dev et docker

if len(sys.argv) > 1:
    host = "0.0.0.0"
else :
    host = "nyt_mysql"

# Paramètres de connexion à la base de données
config = {
    "user": "root",
    "password": "123456",
    "host" : host,
    "database": "nyt",
    "port": 3306
}

def app():

    print("app 00")
    df = select_data_rank_book(config)
    df_ml = prepare_df_ml(df)
    print(f"df_ml {df_ml.shape}")

    st.title("Apprentissage automatique supervisé")

    df_bdd_ml = select_sql(config, "SELECT date, name_model, mse_score, mae_score, r_squared_score FROM machine_learning")
    st.dataframe(df_bdd_ml)

    df['type_book'] = df['type_book'].apply(lambda x: x.lower())

    st.text("Sélectionnez les features pour prédire combien de semaine un livre au maximum va rester dans les bests sellers")

    S_author = set(df['author'].unique())
    author = st.selectbox("Quel auteur ?", S_author)

    st.write("Vous avez sélectionné : ", author)

    S_publisher = set(df['publisher'].unique())
    publisher = st.selectbox("Quel éditeur ?", S_publisher)

    st.write("Vous avez sélectionné : ", publisher)


    S_type_book = set(df['type_book'].unique())
    type_book = st.selectbox("Quel type de livre ?", S_type_book)

    st.write("Vous avez sélectionné : ", type_book)

    df_predict = create_df_for_predict(author, publisher, type_book)


    df_predict = pd.get_dummies(df_predict, columns=['author','publisher','type_book'])

    X = df_ml.drop('weeks_on_list', axis=1)

    missing_cols = set(X.columns) - set(df_predict.columns)
    df_predict = pd.concat([df_predict, pd.DataFrame(0, index=df_predict.index, columns=list(missing_cols))], axis=1)
    df_predict = df_predict[X.columns]


    model_DTR = load_model(config, 'DecisionTreeRegressor')
    print(model_DTR.predict(df_predict))
    predict_DTR = model_DTR.predict(df_predict)
    st.write("Prédiction avec DecisionTreeRegressor", predict_DTR)

    model_Ridge = load_model(config, 'Ridge')
    predict_ridge = model_Ridge.predict(df_predict)
    st.write("Prédiction avec Ridge", predict_ridge)

    model_Lasso = load_model(config, 'Lasso')
    predict_lasso = model_Lasso.predict(df_predict)
    st.write("Prédiction avec Lasso", predict_lasso)


def load_model(config, type_model):
    connection = mysql.connector.connect(**config)
    # Créer un curseur
    cursor = connection.cursor()

    type_model = "'" + type_model + "'"

    query = "SELECT blob_model FROM machine_learning WHERE date = (select max(date) from machine_learning) and name_model like {}".format(type_model)

    #print(query)

    # Récupérer le modèle depuis la base de données MySQL
    cursor.execute(query)

    model_data = cursor.fetchone()[0]

    # Enregistrer le modèle récupéré dans un fichier temporaire
    loaded_model_filename = 'modele_charge.joblib'
    with open(loaded_model_filename, 'wb') as loaded_model_file:
        loaded_model_file.write(model_data)

    # Charger le modèle
    model = load(loaded_model_filename)

    #print(model)

    return model

# Exécute un select sur la BDD et retourne un dataFrame
def select_sql(config, query):
    #param = config
    # Établir une connexion
    connection = mysql.connector.connect(**config)
    # Créer un curseur
    cursor = connection.cursor()
    # Exécuter une requête SELECT

    cursor.execute(query)
    # Récupérer les résultats
    results = cursor.fetchall()

    df = pd.DataFrame(results, columns=[desc[0] for desc in cursor.description])

    # Fermer le curseur et la connexion
    cursor.close()
    connection.close()

    return df

# Récupération des tables livres et rangs dont on fait une jointure et qu'on return en dataframe
def select_data_rank_book(config):

    print("Dans select_data_rank_book")

    df_book = select_sql(config, "select * from data_book")
    df_book = df_book[['author','publisher',"id_book"]]

    df_rank = select_sql(config, "select * from data_rank")
    df_rank = df_rank[["type_book","id_book","weeks_on_list"]]
    df_rank['weeks_on_list'] = df_rank['weeks_on_list'].astype(int)

    df_rank_max = df_rank[['id_book','weeks_on_list','type_book']]
    df_rank_max = df_rank_max.groupby(['id_book','type_book']).max().reset_index()

    print(f" select_data_rank_book : df_rank_max {df_rank_max.head()}")

    df = df_rank_max.merge(df_book, left_on="id_book", right_on="id_book")

    print(f" select_data_rank_book : df {df.head()}")

    return df

def create_df_for_predict(author, publisher, type_book):
    print(author)
    print(publisher)
    print(type_book)
    return pd.DataFrame({"author":[author], "publisher":[publisher], "type_book":[type_book]})

def prepare_df_ml(df):

    print("Dans prepare_df_ml")
    #print(df.head())

    df['weeks_on_list'] = df['weeks_on_list'].astype(int)

    df['type_book'] = df['type_book'].apply(lambda x: x.lower())

    df_ml = df[['author','publisher','weeks_on_list','type_book']]

    #print(df_ml.describe())

    df_ml = replace_outlier(df_ml, 'weeks_on_list')

    #print(df_ml.describe())

    df_ml = pd.get_dummies(df_ml, columns=['author','publisher','type_book'])

    return df_ml


# pour les remplacer par les limites basse ou haute
def replace_outlier(data, col):
    Q1 = data[col].quantile(0.25)
    Q3 = data[col].quantile(0.75)
    IQ = Q3 - Q1

  #print(f"IQ = {IQ}")

    upper_limit = Q3 + 1.5*IQ
    lower_limit = Q1 - 1.5*IQ

  #print(f"limite haute = {upper_limit}, limite basse = {lower_limit}")

    data.loc[data[col] > upper_limit, col] = upper_limit
    data.loc[data[col] < lower_limit, col] = lower_limit

    return data
