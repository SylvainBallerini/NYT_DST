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

if len(sys.argv) > 1:
    host = sys.argv[1]
else :
    host = "0.0.0.0"

config = {
    "user": "root",            # L'utilisateur par défaut de MySQL
    "password": "123456", # Le mot de passe que vous avez défini lors du démarrage du conteneur
    "host": host,        # L'adresse IP du conteneur MySQL (localhost)
    #"host":"nyt_mysql",
    "database": "nyt",   # Nom de la base de données que vous avez créée
    "port": 3306               # Port par défaut de MySQL
}

# Exécute un select sur la BDD et retourne un dataFrame
def select_sql(config, query):
    #param = config
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
    """
    for row in results:
       print(row)
    """
    
    df = pd.DataFrame(results, columns=[desc[0] for desc in cursor.description])    
    # Affichage du DataFrame
    #print(df)    
    # Fermer le curseur et la connexion
    cursor.close()
    connection.close()

    return df

def clean_dataframe_VE(df, column_name):
    # Calcul des quartiles
    Q1 = df[column_name].quantile(0.25)
    Q3 = df[column_name].quantile(0.75)

    print(f"Q1 = {Q1}")
    print(f"Q3 = {Q3}")
    
    # Calcul de l'écart interquartile
    IQR = Q3 - Q1
    
    # Détermination des limites pour les valeurs extrêmes
    lower_limit = Q1 - 1.5 * IQR
    upper_limit = Q3 + 1.5 * IQR

    print(f"lower_limit = {lower_limit}")
    print(f"upper_limit = {upper_limit}")
    
    # Filtrage du DataFrame pour exclure les valeurs extrêmes
    cleaned_df = df[(df[column_name] >= lower_limit) & (df[column_name] <= upper_limit)]
    
    return cleaned_df

def select_data_rank_book(config):

    df_book = select_sql(config, "select * from data_book")

    df_rank = select_sql(config, "select * from data_rank")

    df_rank_max = df_rank[['id_book','weeks_on_list','type_book']]
    df_rank_max = df_rank_max.groupby(['id_book','type_book'])['weeks_on_list'].max().reset_index()

    df = df_rank_max.merge(df_book, left_on="id_book", right_on="id_book")

    return df

def prepare_df_ml(df):

    print(df.head())

    df['weeks_on_list'] = df['weeks_on_list'].astype(int)

    df_ml = df[['author','publisher','weeks_on_list','type_book']]

    print(df_ml.describe())

    df_ml = clean_dataframe_VE(df_ml, 'weeks_on_list')

    print(df_ml.describe())

    df_ml = pd.get_dummies(df_ml, columns=['author','publisher','type_book'])

    return df_ml

def train_model(df_ml,type_model, model):

    print("train model")
    print(type_model)
    print(model)
    

    y = df_ml[['weeks_on_list']]
    X = df_ml.drop('weeks_on_list', axis=1)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

    print("Scaler")

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)


    print("Modele")
    #model = DecisionTreeRegressor()
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


def train_all_model():

    models = []

    dico_model = {}    
    dico_model['name'] = 'DecisionTreeRegressor'
    dico_model['model'] =  DecisionTreeRegressor()
    models.append(dico_model)

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
        print(m['name'])
        print(m['model'])
        df = select_data_rank_book(config)
        df_ml = prepare_df_ml(df)
        train_model(df_ml,m['name'], m['model'])

train_all_model()

        
        
    
    
           




    

