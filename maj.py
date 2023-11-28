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
    "host": "0.0.0.0",        # L'adresse IP du conteneur MySQL (localhost)
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

def total(nbs):
    return sum(nbs)

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

#Exécute un insert dans la table data_book et retourne l'ID du livre
def insert_sql_book(config, book):
    
    param = config
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    
    #query = "INSERT INTO data_book_2 (amazon_product_url) VALUES ('{}')".format(url)
    #print(query)
    #cursor.execute(query)

    query = "INSERT INTO data_book (title, author, book_uri, publisher, description, price, contributor, book_image, book_image_width, book_image_height, amazon_product_url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
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

# Exécute un insert dans la table data_rank 
def insert_sql_rank(config, book, id_book, type_book, date):

    param = config
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()

    id_book = int(id_book)   

    query = "INSERT INTO data_rank (type_book, id_book, date, book_rank, rank_last_week, weeks_on_list) VALUES (%s, %s, %s, %s, %s, %s)"
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

#df_max = select_sql(config, "SELECT MAX(date) FROM data_rank")

#print(df_max)
#print(df_max['MAX(date)'].iloc[0])    

# Initialise l'API du new york time
def Api_nyt():
    my_key = 'w07stZlATDr68hfQOml0zUnNcWJFxinm'
    #my_key = 'rb6HJKRHaF7XIRAQ9P9vG21Ka55KiTlx'
    return NYTAPI(my_key, parse_dates=True)

# Retourne la date de la dernière mise à jour
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

# Récupération des best seller en fonction du jour et du type
def get_best_seller(monday, type_b):
    nyt = Api_nyt()
    books = nyt.best_sellers_list(
                name = type_b,
                #date = datetime.strptime(allM[0],'%Y-%m-%d')
                #date = datetime.strptime('2023-11-06', '%Y-%m-%d')
                date = datetime.strptime(monday, '%Y-%m-%d')                
                )

    return books
    

#print(books[0])

#url = "https://www.amazon.com/dp/1984818589?tag=NYTBSREV-20"
#url = "http://www.amazon.com/Safe-Haven-Nicholas-Sparks/dp/044654759X?tag=NYTBSREV-20"

# Création de la requête pour vérifier si un livre existe via son URL AMAZON
def book_in_data(url):
    
    book = "'%" + url + "%'"
    escape = "ESCAPE '*'"
    query = "select id_book, amazon_product_url from data_book where amazon_product_url like {} {}".format(book, escape) 
    
    return select_sql(config, query)

# Vérification si un livre est présent ou pas dans la table data_book
# Dans le cas où le livre n'existe pas on le crée
# Dans les deux cas on récupère l'ID du livre pour mettre à jour la table data_rank
def recovery_id_book(book):

    url = book['amazon_product_url']
    #print(f"url book {url}")
        
    id_book = 0
    df = book_in_data(url)
    
    if df.empty:
        print("not in data book")
        #Création du livre dans data_book
        id_book = insert_sql_book(config, book)
    else:
        print("in data book")
        id_book = df['id_book'].iloc[0]

    return id_book

# Récupération des lundi depuis la dernière MAJ
# retourne une liste de Lundi ou rien si les tables sont à jours
def get_mondays():
    
    start_date = last_maj()
    today = datetime.now().date()
    
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

    #LOG
    print(f"LOG Liste des lundi {mondays[1:]}")
    return mondays[1:]

# Fonction principale qui permet le suivi via les logs de l'évolution de la pipeline
def maj_data():
    print(f"LOG Début MAJ")
    
    for monday in get_mondays():    

        print(f"LOG Début maj {monday}")

        # boucle sur les différents types de livre
        for t in type_book:
            print(f"LOG Début maj type = {t}")
            #print(get_best_seller(monday, type_book[0])[0])
            books = get_best_seller(monday, t)
            print(f"LOG nombre de livre {len(books)}")

            # Boucle sur chaque livre 
            for nb, book in enumerate(books):
                #print(book)
                #print(f"LOG book {nb} = {book['title']}, {book['author']}, {t}")
                #print(book["amazon_product_url"])
                
                id_book = recovery_id_book(book)
                #print(f"id_book {id_book}")
                insert_sql_rank(config, book, id_book, t, monday)

        print(f"LOG Fin maj {monday}")
    print(f"LOG FIN MAJ")    

maj_data()    
