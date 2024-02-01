import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import mysql.connector
import sys

# Dashboard pour obtenir des informations sur les livres

# permet d'adapter host de la BDD si on est en mode Dev ou Docker
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

# les types de livres
type_book = [
    "Combined Print and E-Book Fiction",
    "Combined Print and E-Book Nonfiction",
    "Hardcover Fiction",
    "Hardcover Nonfiction",
    "Trade Fiction Paperback",
    "Paperback Nonfiction",
    "Business Books"
]

# permet de faire un Select en SQL sur la BDD et returne un DF
def select_sql(config, query):
    param = config

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

# création d'une méga table avec les tables livres et rang
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

# le visuel Streamlit
def app():
    st.title("Dashboard")

    df_book = select_sql(config, "SELECT * FROM data_book ")
    st.dataframe(df_book.head(), use_container_width=True)

    df_br = select_data_rank_book(config)
    st.dataframe(df_br.head(), use_container_width=True)
    st.dataframe(df_br[['weeks_on_list', "book_image_width", "book_image_height"]].describe())

    select_type = st.selectbox("Sélectionnez un type de livre", df_br.type_book.unique())

    df = df_br[df_br['type_book'] == select_type]

    st.write("Filtre sur les livres qui sont restés un minimum dans les bests sellers")

    min_weeks = st.number_input('Entrez un nombre ', min_value=0, value=0)

    df = df[df['weeks_on_list'] >= min_weeks]

    st.dataframe(df, use_container_width=True)

    top_10 = df.sort_values('weeks_on_list', ascending = False).head(10)

    # Création d'un bar chart avec plotly express
    fig = px.bar(top_10, x="title", y="weeks_on_list", title="Top 10 des livres restés le plus longtemps dans les meilleurs ventes")

    # Afficher le graphique avec Streamlit
    st.plotly_chart(fig)    
