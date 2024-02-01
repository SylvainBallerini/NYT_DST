Contexte�:
Le New York Time dispose d�une API qui permet de connaitre les meilleures ventes de livres et dans plusieurs cat�gories (Business, Fiction etc)

Tous les lundis il met � jour les meilleurs Bestseller du moment.

Nous avons comme information sur un livre�:
Son titre
Son Auteur
Ses dimensions
Son type
Son rang actuel (sur 15 dans cette cat�gorie)
Le nombre de semaine o� il est dans les bestsellers

Mon application a donc pour objectifs�:
1) R�cup�ration chaque semaine des nouveaux Bestseller
2) Entrainer un mod�le de ML supervis� pour pr�dire la r�ussite d�un livre
3) Une application web pour obtenir des informations
4) Une API pour obtenir des informations sur les livres


L�application se divise en 5 parties�:

La base de donn�es MySQL qui poss�de 3 tables�:
	Data_book avec l�ensemble des informations des livres
	Data_rank avec l�ensemble des rangs des livres par date
	Machine_learning�: qui contient les mod�les qu�on a entrain�	

L�application en Streamlit 
	App.py
	Ml_super.py
	Presentation.py
	Dashboard.py
	
Un script pour faire les MAJ
	Maj.py

Un script pour entrainer les mod�les
	Train_ml.py

Deux scripts pour les jobs
	nyt_cron.sh  
       nyt_cron_ml.sh 





