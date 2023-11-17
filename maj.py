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

#nyt = Api_nyt()

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

def insert_sql_book(config, book):
    
    param = config
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    
    #query = "INSERT INTO data_book_2 (amazon_product_url) VALUES ('{}')".format(url)
    #print(query)
    #cursor.execute(query)

    query = "INSERT INTO data_book_2 (title, author, book_uri, publisher, description, price, contributor, book_image, book_image_width, book_image_height, amazon_product_url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(query,[
        book['title'],
        book['author'],
        book['book_uri'],
        book['publisher'],
        book['description'],
        book['price'],
        book['contributor'],
        book['book_image'],
        book['book_image_width'],
        book['book_image_height'],
        book['amazon_product_url']
        ])
        
    connection.commit()
    connection.close()
    return cursor.lastrowid

def insert_sql_rank(config, book, id_book, type_book, date):

    param = config
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()

    print("Vals for rank")
    print(type(book['rank']))
    print(type(book['rank_last_week']))
    print(type(book['weeks_on_list']))

    print(type(type_book))
    print(type(id_book))
    print(type(date))

    id_book = int(id_book)   

    print(type(id_book)) 

    query = "INSERT INTO data_rank_2 (type_book, id_book, date, book_rank, rank_last_week, weeks_on_list) VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.execute(query,[
            type_book,
            id_book,
            date,
            book['rank'],
            book['rank_last_week'],
            book['weeks_on_list']
            ])

    connection.commit()
    connection.close()
    print("INSERT RANK DONE")

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


#print(f"last_maj {last_maj()}")

#nyt = Api_nyt()
"""
books = nyt.best_sellers_list(
            name = type_book[0],
            #date = datetime.strptime(allM[0],'%Y-%m-%d')
            date = datetime.strptime('2023-11-06', '%Y-%m-%d')
            #date = '2023-11-06'
            )
"""


def get_best_seller(monday, type_b):
    nyt = Api_nyt()
    books = nyt.best_sellers_list(
                name = type_book[0],
                #date = datetime.strptime(allM[0],'%Y-%m-%d')
                #date = datetime.strptime('2023-11-06', '%Y-%m-%d')
                date = datetime.strptime(monday, '%Y-%m-%d')                
                )

    return books
    

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
    #print(query)
    return select_sql(config, query)


#print(book_in_data(url))

#insert_sql("test",config)

#Récupération de l'ID du livre dans la BDD
def recovery_id_book(book):

    url = book['amazon_product_url']
    print(f"url book {url}")
        
    id_book = 0
    df = book_in_data(url)
    #print(df)
    if df.empty:
        print("not in data book")
        #Création du livre dans data_book
        id_book = insert_sql_book(config, book)
    else:
        print("in data book")
        id_book = df['id_book'].iloc[0]

    return id_book

# Test récupération de l'ID du livre

#print(recovery_id_book(url))

#url = "http://www.amazon.com/dp/1984818589?tag=NYTBSREV-20"
#print(recovery_id_book(url))

def get_mondays():
    # Obtention de la date d'aujourd'hui
    #start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    #print(start_date)
    #start_date = datetime.strptime(start_date, "%Y-%m-%d")
    #today = datetime.strptime(today, "%Y-%m-%d")
    start_date = last_maj()
    today = datetime.now().date()

    #print(f"Date d'aujourd'hui {today}")
    
    # Liste pour stocker les dates des lundis
    mondays = []

    # Boucle pour itérer sur les dates depuis la date de départ jusqu'à aujourd'hui
    current_date = start_date
    while current_date <= today:
        # Vérification si la date est un lundi
        if current_date.weekday() == 0:  # 0 correspond au lundi
            mondays.append(current_date.strftime('%Y-%m-%d'))
        
        # Passage à la date suivante
        current_date += timedelta(days=1)
    
    #print(mondays[1:])
    return mondays[1:]

print(f"{get_mondays()}")

for monday in get_mondays():
    print(monday)
    print(get_best_seller(monday, type_book[0])[0])
    book = get_best_seller(monday, type_book[0])[0]
    print(book)
    id_book = recovery_id_book(book)
    print(f"id_book {id_book}")
    insert_sql_rank(config, book, id_book, type_book[0], monday)

    
    
    




        
        
        





    

