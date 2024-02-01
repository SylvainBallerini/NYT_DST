import mysql.connector
import pandas as pd
from datetime import datetime
import pandas as pd
from datetime import datetime, timedelta, date
import streamlit as st

# Les pages / module pour la navigation dans streamlit
import presentation
import ml_super
import dashboard

# C'est le fichier pour lancer Streamlit


# Paramètres de connexion à la base de données
config = {
    "user": "root",
    "password": "123456",
    "host": "172.17.0.2",
    #"host":"nyt_mysql",
    "database": "nyt",
    "port": 3306
}

# pour le menu à gauche dans pour streamlit
PAGES = {
    "Présentation" : presentation,
    "Dashboard" : dashboard,
    "Machine Learning Supervisé": ml_super
}

# Création d'une barre de navigation
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Allez à", list(PAGES.keys()))
page = PAGES[selection]

# Pour lancer l'application streamlit
page.app()
