from api.database import creer_connexion_cloud
from datetime import datetime

def synchroniser_donnees(data):
    try:
        conn_cloud = creer_connexion_cloud()
        if not conn_cloud :
            return False

        cloud_cursor = conn_cloud.cursor()

        # Verifier si l'objet existe dans la base de données
        id_objet = data['objet']
        cloud_cursor.execute("SELECT id_objet FROM objets WHERE id_objet = %s", (id_objet,))
        objet_existe = cloud_cursor.fetchone()

        if not objet_existe:
            # Inserer l'objet si il n'existe pas
            cloud_cursor.execute("""
                INSERT INTO objets (id_objet, nom_objet, local_objet, is_localisation)
                VALUES (%s, %s, %s, %s)
            """, (id_objet, 'Unknown', 'Unknown', False))
            
        for video in data['videos']:
            id_video = video['video']
            date_str = video['date']
            date_jour = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z').strftime('%Y-%m-%d') # convertir la date en format 'YYYY-MM-DD'
            nb_jouer = video['nb']
            temps_jouer = video['temps']

            # Verifier si la video existe dans videos_objets
            cloud_cursor.execute("SELECT id_video FROM videos_objets WHERE id_video = %s", (id_video,))
            video_existe = cloud_cursor.fetchone()

            if not video_existe:
                # Inserer la video si elle n'existe pas
                cloud_cursor.execute("""
                    INSERT INTO videos_objets (id_video, id_objet, nom_video, taille_video, md5_video, ordre_video)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (id_video, id_objet, 'Unknown', 0, '', 0))

            # Inserer ou mettre a jour les statistiques de la video pour la journée
            query_cloud = """
            INSERT INTO videos_par_jour (date_jour, id_video, id_objet, nb_jouer, temps_jouer)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE nb_jouer = nb_jouer + VALUES(nb_jouer), temps_jouer = temps_jouer + VALUES(temps_jouer)
            """
            cloud_cursor.execute(query_cloud, (date_jour, id_video, id_objet, nb_jouer, temps_jouer))

        conn_cloud.commit()
        return True
    except Exception as e:
        print(f"Erreur lors de la synchronisation des données: {e}")
        return False
    finally:
        if cloud_cursor: cloud_cursor.close()
        if conn_cloud: conn_cloud.close()
