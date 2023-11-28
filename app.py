import mysql.connector
import pandas as pd
from datetime import datetime
import pandas as pd
from pynytimes import NYTAPI
from datetime import datetime, timedelta, date
import streamlit as st

import presentation
import ml_super
import dashboard


# Paramètres de connexion à la base de données
config = {
    "user": "root",            # L'utilisateur par défaut de MySQL
    "password": "123456", # Le mot de passe que vous avez défini lors du démarrage du conteneur
    "host": "172.17.0.2",        # L'adresse IP du conteneur MySQL (localhost)
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

PAGES = {
    "Présentation" : presentation,
    "Dashboard" : dashboard,
    "Machine Learning Supervisé": ml_super
}

# Create the sidebar for navigation
st.sidebar.title("Navigation")

# Select the page using a radio element in the sidebar
selection = st.sidebar.radio("Allez à", list(PAGES.keys()))

# Get the corresponding object or function for the selected page
page = PAGES[selection]

# Run the application of the selected page
page.app()
