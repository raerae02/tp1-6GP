import mysql.connector
from mysql.connector import Error


# Créer une connexion à la base de données locale
def creer_connexion():
    connexion = None
    try:
        print('Connexion à la base de données...')
        connexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='password',
            database='videos_db',
        )
    except Error as e:
        print(f"Erreur lors de la connexion à la base de données: {e}")
        
    return connexion

# Créer une connexion à la base de données AZURE
def creer_connexion_cloud():
    connexion = None
    try:
        print('Connexion à la base de données...')
        connexion = mysql.connector.connect(
            host='4.206.210.212',
            user='root',
            password='FrhMakKha1234',
            database='objets_bd'
        )
    except Error as e:
        print(f"Erreur lors de la connexion à la base de données: {e}")

    return connexion