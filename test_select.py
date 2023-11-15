import mysql.connector
import pandas as pd

# Paramètres de connexion à la base de données
config = {
    "user": "root",            # L'utilisateur par défaut de MySQL
    "password": "123456", # Le mot de passe que vous avez défini lors du démarrage du conteneur
    "host": "172.17.0.2",        # L'adresse IP du conteneur MySQL (localhost)
    #"host":"nyt_mysql",
    "database": "nyt",   # Nom de la base de données que vous avez créée
    "port": 3306               # Port par défaut de MySQL
}

# Établir une connexion
conn = mysql.connector.connect(**config)

# Créer un curseur
cursor = conn.cursor()

# Exécuter une requête SELECT
query = "SELECT MAX(date) FROM data_rank"  # Remplacez "mytable" par le nom de votre table
cursor.execute(query)

# Récupérer les résultats
results = cursor.fetchall()

# Afficher les résultats
for row in results:
    print(row)

#df = pd.DataFrame(results, columns=[desc[0] for desc in cursor.description])

# Affichage du DataFrame
#print(df)

# Fermer le curseur et la connexion
cursor.close()
conn.close()
