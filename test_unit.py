from maj import total, select_sql, get_mondays, get_best_seller, recovery_id_book
from train_ml import replace_outlier, prepare_df_ml
import pytest
import pandas as pd
from datetime import datetime
from unittest.mock import patch
from pynytimes import NYTAPI
import numpy as np


config = {
    "user": "root",
    "password": "123456",
    "host": "0.0.0.0",
    "database": "nyt",
    "port": 3306
}

# Test basique de vérification
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

# Test SQL
def test_select_sql():


    query = "SELECT count(*) FROM data_rank"

    df = select_sql(config, query)

    # Assurez-vous que le résultat est un DataFrame
    assert isinstance(df, pd.DataFrame)

    # Assurez-vous que le DataFrame n'est pas vide )
    assert not df.empty

    query = "SELECT count(*) FROM data_book"

    df = select_sql(config, query)

    # Assurez-vous que le résultat est un DataFrame
    assert isinstance(df, pd.DataFrame)

    # Assurez-vous que le DataFrame n'est pas vide
    assert not df.empty

    query = "SELECT MAX(date) FROM data_rank"

    df = select_sql(config, query)

    assert len(df) == 1

# Vérification de L'API
def test_Api_nyt():
    my_key = 'w07stZlATDr68hfQOml0zUnNcWJFxinm'

    # Créez une instance de la classe NYTAPI en utilisant la fonction Api_nyt
    api_instance = NYTAPI(my_key, parse_dates=True)

    # vérification si l'instance est bien de type NYTAPI
    assert isinstance(api_instance, NYTAPI)

# Test vérification du contenu de l'API NYT
def test_get_best_seller():

    type_book = [
        "Combined Print and E-Book Fiction",
        "Combined Print and E-Book Nonfiction",
        "Hardcover Fiction",
        "Hardcover Nonfiction",
        "Trade Fiction Paperback",
        "Paperback Nonfiction",
        "Business Books"
    ]

    for type in type_book:

        data = get_best_seller("2024-01-01",type)

        # Vérification du retour
        assert data

        # vérification si c'est une list
        assert isinstance(data, list)

        # vérification taille de la liste
        assert len(data) > 5

#Test train_ml
def test_replace_outlier():
    data = pd.DataFrame({'col': [1, 2,5.5, 3, 10, 20,25.5, 30,20,25,100,200]})

    Q1 = data['col'].quantile(0.25)
    Q3 = data['col'].quantile(0.75)
    IQ = Q3 - Q1

    upper_limit = Q3 + 1.5 * IQ
    lower_limit = Q1 - 1.5 * IQ

    # Appel de la fonction pour remplacer les outliers
    result = replace_outlier(data, 'col')

    # Vérification que les outliers ont été remplacés
    assert result['col'].max() <= upper_limit
    assert result['col'].min() >= lower_limit

# Test préparation du df pour le machine learning
def test_prepare_df_ml():
    # Création d'un DataFrame de test
    data = {
        'author': ['Author1', 'Author2', 'Author1', 'Author3'],
        'publisher': ['Publisher1', 'Publisher2', 'Publisher1', 'Publisher3'],
        'weeks_on_list': [1, 5, 10, 20],
        'type_book': ['Type1', 'Type2', 'Type1', 'Type3']
    }
    df = pd.DataFrame(data)

    # Appel de la fonction pour préparer le DataFrame
    df_ml = prepare_df_ml(df)

    # Vérification qu'il y a au moins une colonne 'type_book' dans le DataFrame transformé
    assert any(col.startswith('type_book_') for col in df_ml.columns)
