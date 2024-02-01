import streamlit as st

# page de Présentation de Streamlit

def app():
    st.title("Présentation")

    multi = """
    Contexte :
    Le New York Time dispose d’une API qui permet de connaitre les meilleures ventes de livres et dans plusieurs catégories (Business, Fiction etc)

    Tous les lundis il met à jour les meilleurs Bestseller du moment.

    Nous avons comme information sur un livre :

    Son titre , son Auteur , ses dimensions, son type

    Son rang actuel (sur 15 dans cette catégorie)

    Le nombre de semaine où il est dans les bestsellers

    Mon application a donc pour objectifs :

        1)	Récupération chaque semaine des nouveaux Bestsellers

        2)	Entrainer un modèle de Machine Learning supervisé pour prédire la réussite d’un livre

        3)	Une application web pour obtenir des informations

        4)	Une API pour obtenir des informations sur les livres
    """

    st.markdown(multi)
