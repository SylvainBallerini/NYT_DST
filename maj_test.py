from maj import total, select_sql, get_mondays
import pytest
import pandas as pd
from datetime import datetime
from unittest.mock import patch


config = {
    "user": "root",            # L'utilisateur par défaut de MySQL
    "password": "123456", # Le mot de passe que vous avez défini lors du démarrage du conteneur
    "host": "0.0.0.0",        # L'adresse IP du conteneur MySQL (localhost)
    #"host":"nyt_mysql",
    "database": "nyt",   # Nom de la base de données que vous avez créée
    "port": 3306               # Port par défaut de MySQL
}

def test_total():
    #Les use cases :
    """La somme de plusieurs éléments d'une liste doit être correcte"""
    assert(total([1.0, 2.0, 3.0])) == 6.0

    """1 - 1 = 0"""
    assert total([1,-1]) == 0

    """-1 -1 = -2"""
    assert total([-1,-1]) == -2

    #Les edge cases :
    """La somme doit être égal à l'unique élément"""
    assert(total([1.0])) == 1.0

    """La somme d'une liste vide doit être 0"""
    assert total([]) == 0

def test_select_sql():


    query = "SELECT count(*) FROM data_rank"

    df = select_sql(config, query)

    # Assurez-vous que le résultat est un DataFrame
    assert isinstance(df, pd.DataFrame)

    # Assurez-vous que le DataFrame n'est pas vide (ajustez selon vos attentes)
    assert not df.empty

    query = "SELECT count(*) FROM data_book"

    df = select_sql(config, query)

                # Assurez-vous que le résultat est un DataFrame
    assert isinstance(df, pd.DataFrame)

                # Assurez-vous que le DataFrame n'est pas vide (ajustez selon vos attentes)
    assert not df.empty

    query = "SELECT MAX(date) FROM data_rank"

    df = select_sql(config, query)

    assert len(df) == 1
