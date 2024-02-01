Contexte :
Le New York Time dispose d’une API qui permet de connaitre les meilleures ventes de livres et dans plusieurs catégories (Business, Fiction etc)

Tous les lundis il met à jour les meilleurs Bestseller du moment.

Nous avons comme information sur un livre :
Son titre
Son Auteur
Ses dimensions
Son type
Son rang actuel (sur 15 dans cette catégorie)
Le nombre de semaine où il est dans les bestsellers

Mon application a donc pour objectifs :
1) Récupération chaque semaine des nouveaux Bestseller
2) Entrainer un modèle de ML supervisé pour prédire la réussite d’un livre
3) Une application web pour obtenir des informations
4) Une API pour obtenir des informations sur les livres


L’application se divise en 5 parties :

La base de données MySQL qui possède 3 tables :
	Data_book avec l’ensemble des informations des livres
	Data_rank avec l’ensemble des rangs des livres par date
	Machine_learning : qui contient les modèles qu’on a entrainé	

L’application en Streamlit 
	App.py
	Ml_super.py
	Presentation.py
	Dashboard.py
	
Un script pour faire les MAJ
	Maj.py

Un script pour entrainer les modèles
	Train_ml.py

Deux scripts pour les jobs
	nyt_cron.sh  
       nyt_cron_ml.sh 





