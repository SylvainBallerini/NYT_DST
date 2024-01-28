import mysql.connector
import pandas as pd
from datetime import datetime
import pandas as pd
from datetime import datetime, timedelta, date
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import sys
import json


#modification de la variable host entre dev et docker
"""
if len(sys.argv) > 1:
    host = sys.argv[1]
else :
    #host = "0.0.0.0"
    host = "nyt_mysql"
"""
# Paramètres de connexion à la base de données
config = {
    "user": "root",            # L'utilisateur par défaut de MySQL
    "password": "123456", # Le mot de passe que vous avez défini lors du démarrage du conteneur
    "host":"nyt_mysql",
    "database": "nyt",   # Nom de la base de données que vous avez créée
    "port": 3306               # Port par défaut de MySQL
}

api = FastAPI()

# Exécute un select sur la BDD et retourne un dataFrame
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

@api.get("/")
def get_index():
    return {"data":"Hello bjour bsoir all"}

@api.get("/nb_book")
def get_nb_book():
    print("get_nb_book")
    query = "select count(*) from data_book"
    res = select_sql(config, query)
    nb_book = res['count(*)'].iloc[0].item()
    print(nb_book)

    return nb_book

@api.get("/list_book")
def get_list_book():
    print("get_list_book")
    query = "select id_book, title from data_book "
    res = select_sql(config, query)

    # Convertir le DataFrame en JSON
    json_data = json.loads(res.to_json(orient='records'))

    # Renvoyer une réponse JSON avec les données
    return JSONResponse(content=json_data)

@api.get("/info_book/{id_book}")
def get_info_book(id_book: int):
    print("get_info_book")
    query = "select * from data_book where id_book = {}".format(id_book)
    res = select_sql(config, query)

    # Convertir le DataFrame en JSON
    json_data = json.loads(res.to_json(orient='records'))

    # Renvoyer une réponse JSON avec les données
    return JSONResponse(content=json_data)
