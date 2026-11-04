Projet Bar 



Présentation :

Ce projet consiste à modéliser le fonctionnement d'un bar en Python.

Le bar comprend deux employés :

Un serveur, chargé de prendre les commandes et de servir les clients.

Un bariste, chargé de préparer les cocktails.

Les échanges entre les employés s'effectuent au moyen de deux accessoires : un pic pour les commandes en attente et un bar pour les consommations préparées.




Objectifs :

L'objectif est de développer progressivement une simulation du fonctionnement du bar, en passant d'une exécution séquentielle à une exécution concurrente avec asyncio.

Avancement :


Partie 1 — Exécution séquentielle

Étape 1 : Implémentation des classes et du fonctionnement séquentiel.  Check 

Étape 2 : Lecture des commandes depuis un fichier.     En cours

Étape 3 : Mise en place d'un système de journalisation (logs).



Partie 2 — Programmation concurrente

Introduction des coroutines.

Utilisation de asyncio.Queue.

Coopération entre les tâches.

Gestion des tâches du serveur.


Partie 3 — Extension

Ajout d'un second serveur.

Gestion de la productivité des employés.