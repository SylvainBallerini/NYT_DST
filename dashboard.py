import streamlit as st
import pandas as pd
import numpy as np
#import plotly.express as px
#import seaborn as sns
#import matplotlib as plt
import mysql.connector
import sys


if len(sys.argv) > 1:
    host = sys.argv[1]
else :
    host = "0.0.0.0"
    
# Paramètres de connexion à la base de données
config = {
    "user": "root",            # L'utilisateur par défaut de MySQL
    "password": "123456", # Le mot de passe que vous avez défini lors du démarrage du conteneur
    "host": host,        # L'adresse IP du conteneur MySQL (localhost)
    #"host":"nyt_mysql",
    "database": "nyt",   # Nom de la base de données que vous avez créée
    "port": 3306               # Port par défaut de MySQL
}

type_book = [
    "Combined Print and E-Book Fiction",
    "Combined Print and E-Book Nonfiction",
    "Hardcover Fiction",
    "Hardcover Nonfiction",
    "Trade Fiction Paperback",
    "Paperback Nonfiction",
    "Business Books"
]

def select_sql(config, query):
    param = config
    # Établir une connexion
    connection = mysql.connector.connect(**config)    
    # Créer un curseur
    cursor = connection.cursor()    
    # Exécuter une requête SELECT
    #query = "SELECT MAX(date) FROM data_rank"  # Remplacez "mytable" par le nom de votre table
    cursor.execute(query)    
    # Récupérer les résultats
    results = cursor.fetchall()    
    # Afficher les résultats
    for row in results:
       print(row)
    
    df = pd.DataFrame(results, columns=[desc[0] for desc in cursor.description])    
    # Affichage du DataFrame
    #print(df)    
    # Fermer le curseur et la connexion
    cursor.close()
    connection.close()

    return df

def select_data_rank_book(config):

    df_book = select_sql(config, "select * from data_book")

    df_rank = select_sql(config, "select * from data_rank")

    df_rank_max = df_rank[['id_book','weeks_on_list','type_book']]
    df_rank_max = df_rank_max.groupby(['id_book','type_book'])['weeks_on_list'].max().reset_index()

    df = df_rank_max.merge(df_book, left_on="id_book", right_on="id_book")

    df['weeks_on_list'] = df['weeks_on_list'].astype(float)
    df['book_image_width'] = df['book_image_width'].astype(float)
    df['book_image_height'] = df['book_image_height'].astype(float)    

    return df


def app():
    st.title("Dashboard")

    df_book = select_sql(config, "SELECT * FROM data_book")
    st.dataframe(df_book.head(), use_container_width=True)

    df_br = select_data_rank_book(config)
    st.dataframe(df_br.head(), use_container_width=True)
    st.dataframe(df_br[['weeks_on_list', "book_image_width", "book_image_height"]].describe())

    print(df_br.info())
    
    

    
