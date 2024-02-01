import pandas as pd
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import mysql.connector
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression, Lasso, Ridge
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from joblib import dump, load
from datetime import date
import sys

# fichier pour Entrainer 3 modèles de ML supervisé avec l'ensemble des données
# on garde les modèles dans la BDD sous forme de BLOB avec les 3 scores et la date


#modification de la variable host entre dev et docker

if len(sys.argv) > 1:
    host = sys.argv[1]
else :
    host = "0.0.0.0"

config = {
    "user": "root",
    "password": "123456",
    "host": host,
    "database": "nyt",
    "port": 3306
}

# Exécute un select sur la BDD et retourne un dataFrame
def select_sql(config, query):

    # Établir une connexion
    connection = mysql.connector.connect(**config)
    # Créer un curseur
    cursor = connection.cursor()
    # Exécuter une requête SELECT
    cursor.execute(query)
    # Récupérer les résultats
    results = cursor.fetchall()
    # Afficher les résultats

    df = pd.DataFrame(results, columns=[desc[0] for desc in cursor.description])

    # Fermer le curseur et la connexion
    cursor.close()
    connection.close()

    return df

# pour  remplacer les outliers par les limites basse ou haute
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

def select_data_rank_book(config):

    df_book = select_sql(config, "select * from data_book")

    df_rank = select_sql(config, "select * from data_rank")

    df_rank_max = df_rank[['id_book','weeks_on_list','type_book']]
    df_rank_max = df_rank_max.groupby(['id_book','type_book'])['weeks_on_list'].max().reset_index()

    df = df_rank_max.merge(df_book, left_on="id_book", right_on="id_book")

    return df

# preparation du df avant l'entrainement
def prepare_df_ml(df):

    df['weeks_on_list'] = df['weeks_on_list'].astype(int)

    df['type_book'] = df['type_book'].apply(lambda x: x.lower())

    df_ml = df[['author','publisher','weeks_on_list','type_book']]

    df_ml = replace_outlier(df_ml, 'weeks_on_list')

    df_ml = pd.get_dummies(df_ml, columns=['author','publisher','type_book'])

    return df_ml

# fonction pour entrainer les modèles et les sauvegarder dans la BDD avec nom, les 3 scores et le modèle
def train_model(df_ml,type_model, model):

    print("train model")
    print(type_model)
    print(model)


    y = df_ml[['weeks_on_list']]
    X = df_ml.drop('weeks_on_list', axis=1)

    print(X.shape)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)


    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)


    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    print(f'Mean Squared Error: {mse}')

    mae = mean_absolute_error(y_test, y_pred)
    print(f"Mean absolute error: {mae}")

    r_squared = r2_score(y_test, y_pred)
    print(f"r2_score : {r_squared}")

    # Création d'un dictionnaire contenant les informations du modèle
    info_model = {
        'date': date.today(),
        'name': type_model,
        'mse_score': mse,
        'mae_score': mae,
        'r_squared_score': r_squared
    }

    print(f"info_model = {info_model}")

    save_modele(config, model, info_model)


def save_modele(config, model, info_model):

    # Enregistrer le modèle dans un fichier temporaire
    model_filename = 'modele_entraiment.joblib'
    dump(model, model_filename)

    connection = mysql.connector.connect(**config)
    # Créer un curseur
    cursor = connection.cursor()

    # Enregistrer le modèle dans la base de données MySQL
    with open(model_filename, 'rb') as model_file:
        model_data = model_file.read()
        cursor.execute("INSERT INTO machine_learning (date, name_model, blob_model, mse_score, mae_score, r_squared_score) VALUES (%s, %s, %s, %s, %s, %s)",
        (info_model['date'], info_model['name'], model_data, info_model['mse_score'], info_model['mae_score'], info_model['r_squared_score'])
        )

        # Commit et fermer la connexion
    connection.commit()
    connection.close()

#chaque modele est mis dans un dico qui comporte son nom et son modele pour le suivi jusqu'à la BDD
def train_all_model():

    models = []

    dico_model = {}
    dico_model['name'] = 'DecisionTreeRegressor'
    dico_model['model'] =  DecisionTreeRegressor()
    models.append(dico_model)

    #suppresion du modele Regression Linear qui ne peut pas suivre avec autant de variable
    """
    dico_model = {}
    dico_model['name'] = 'LinearRegression'
    dico_model['model'] =  LinearRegression()
    models.append(dico_model)
    """

    dico_model = {}
    dico_model['name'] = 'Lasso'
    dico_model['model'] =  Lasso(alpha=0.01)
    models.append(dico_model)

    dico_model = {}
    dico_model['name'] = 'Ridge'
    dico_model['model'] =  Ridge(alpha=0.01)
    models.append(dico_model)


    for m in models:
        #print(m['name'])
        #print(m['model'])
        df = select_data_rank_book(config)
        df_ml = prepare_df_ml(df)
        train_model(df_ml,m['name'], m['model'])

#train_all_model()

def main():
    train_all_model()

if __name__ == "__main__":
    main()
