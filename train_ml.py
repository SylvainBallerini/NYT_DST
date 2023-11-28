import pandas as pd
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import mysql.connector
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error

config = {
    "user": "root",            # L'utilisateur par défaut de MySQL
    "password": "123456", # Le mot de passe que vous avez défini lors du démarrage du conteneur
    "host": "0.0.0.0",        # L'adresse IP du conteneur MySQL (localhost)
    #"host":"nyt_mysql",
    "database": "nyt",   # Nom de la base de données que vous avez créée
    "port": 3306               # Port par défaut de MySQL
}

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

df_book = select_sql(config, "select * from data_book")

df_rank = select_sql(config, "select * from data_rank")

df_rank_max = df_rank[['id_book','weeks_on_list','type_book']]
df_rank_max = df_rank_max.groupby(['id_book','type_book'])['weeks_on_list'].max().reset_index()

df = df_rank_max.merge(df_book, left_on="id_book", right_on="id_book")

print(df.head())

df['weeks_on_list'] = df['weeks_on_list'].astype(int)

df_ml = df[['author','publisher','weeks_on_list','type_book']]

print(df_ml.describe())

df_ml = clean_dataframe_VE(df_ml, 'weeks_on_list')

print(df_ml.describe())

df_ml = pd.get_dummies(df_ml, columns=['author','publisher','type_book'])

y = df_ml[['weeks_on_list']]
X = df_ml.drop('weeks_on_list', axis=1)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

print("Scaler")

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)


print("Modele")
model = DecisionTreeRegressor()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
print(f'Mean Squared Error: {mse}')
