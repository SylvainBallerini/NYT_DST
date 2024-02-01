import mysql.connector
import pandas as pd
from datetime import datetime
import pandas as pd
from datetime import datetime, timedelta, date
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import sys
import json


# API FastAPI pour obtenir des informations sur les livres

#modification de la variable host entre dev et docker

if len(sys.argv) > 5:
    host = "nyt_mysql"
else :
    host = "0.0.0.0"


# Paramètres de connexion à la base de données
config = {
    "user": "root",
    "password": "123456",
    "host":host,
    "database": "nyt",
    "port": 3306
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

    cursor.execute(query)
    # Récupérer les résultats
    results = cursor.fetchall()
    # Afficher les résultats
    for row in results:
       print(row)

    df = pd.DataFrame(results, columns=[desc[0] for desc in cursor.description])


    # Fermer le curseur et la connexion
    cursor.close()
    connection.close()

    return df

#Test de l'API Fast API
@api.get("/")
def get_index():
    return {"Hello": "World"}

# Permet de connaitre le nombre de livre dans data_book
@api.get("/nb_book")
def get_nb_book():
    print("get_nb_book")
    query = "select count(*) from data_book"
    res = select_sql(config, query)
    nb_book = res['count(*)'].iloc[0].item()
    print(nb_book)

    return nb_book

# Permet de connaitre les livres avec leur id et leur titre
@api.get("/list_book")
def get_list_book():
    print("get_list_book")
    query = "select id_book, title from data_book "
    res = select_sql(config, query)

    # Convertir le DataFrame en JSON
    json_data = json.loads(res.to_json(orient='records'))

    return JSONResponse(content=json_data)

# permet d'obtenir plus d'information sur un livre
# comme son auteur, ses dimensions, etc
@api.get("/info_book/{id_book}")
def get_info_book(id_book: int):
    #print("get_info_book")

    query = "select distinct(id_book) from data_book"
    id_book_unique = select_sql(config, query)
    id_book_unique = list(id_book_unique['id_book'].unique())

    #print(id_book_unique)

    if id_book not in id_book_unique:
        return "Erreur cette ID de livre n'existe pas"

    query = "select * from data_book where id_book = {}".format(id_book)

    res = select_sql(config, query)

    # Convertir le DataFrame en JSON
    json_data = json.loads(res.to_json(orient='records'))

    return JSONResponse(content=json_data)
