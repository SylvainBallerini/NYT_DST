import mysql.connector
import pandas as pd
from datetime import datetime
import pandas as pd
from pynytimes import NYTAPI
from datetime import datetime, timedelta, date

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

def insert_sql(config, url):
    
    param = config
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    
    query = "INSERT INTO data_book_2 (amazon_product_url) VALUES ('{}')".format(url)
    print(query)
    cursor.execute(query)
    connection.commit()
    connection.close()
    return cursor.lastrowid
    


df_max = select_sql(config, "SELECT MAX(date) FROM data_rank")

#print(df_max)
#print(df_max['MAX(date)'].iloc[0])    

def Api_nyt():
    my_key = 'w07stZlATDr68hfQOml0zUnNcWJFxinm'
#my_key = 'rb6HJKRHaF7XIRAQ9P9vG21Ka55KiTlx'
    return NYTAPI(my_key, parse_dates=True)

def last_maj():
    df_max = select_sql(config, "SELECT MAX(date) FROM data_rank")
    
    return df_max['MAX(date)'].iloc[0]


print(f"last_maj {last_maj()}")

nyt = Api_nyt()
books = nyt.best_sellers_list(
            name = type_book[0],
            #date = datetime.strptime(allM[0],'%Y-%m-%d')
            date = datetime.strptime('2023-11-06', '%Y-%m-%d')
            #date = '2023-11-06'
            )

#print(books[0])

#url = "https://www.amazon.com/dp/1984818589?tag=NYTBSREV-20"
url = "http://www.amazon.com/Safe-Haven-Nicholas-Sparks/dp/044654759X?tag=NYTBSREV-20"

def book_in_data(url):
    #query = "select amazon_product_url from data_book where amazon_product_url like '%044654759X%'"
    #query = 'select amazon_product_url from data_book where amazon_product_url like "%044654759X%"'
    #book_1 = "'%http://www.amazon.com/Safe-Haven-Nicholas-Sparks/dp/044654759X?tag=NYTBSREV-20%'"
    #url = "http://www.amazon.com/Safe-Haven-Nicholas-Sparks/dp/044654759X?tag=NYTBSREV-20"
    book = "'%" + url + "%'"
    #print(book_1)
    #print(book_2)
    escape = "ESCAPE '*'"
    query = "select id_book, amazon_product_url from data_book_2 where amazon_product_url like {} {}".format(book, escape) 
    print(query)
    return select_sql(config, query)

print(book_in_data(url))

#insert_sql("test",config)

#Récupération de l'ID du livre dans la BDD
def recovery_id_book(url):
    print(f"url in recovery {url}")
    
    id_book = 0
    df = book_in_data(url)
    #print(df)
    if df.empty:
        print("not in data book")
        #Création du livre dans data_book
        id_book = insert_sql(config, url)
    else:
        print("in data book")
        id_book = df['id_book'].iloc[0]

    print(id_book)

recovery_id_book(url)

url = "http://www.amazon.com/dp/1984818589?tag=NYTBSREV-20"
recovery_id_book(url)


        
        
        





    

