from api.database import creer_connexion_cloud, creer_connexion
from datetime import datetime
from datetime import datetime

def synchroniser_donnees_cloud_avec_locale(data):
    try:
        print("synchroniser les données cloud avec locale")
        conn_cloud = creer_connexion_cloud()
        if not conn_cloud:
            return False
        print("conn_cloud: ", conn_cloud)

        cloud_cursor = conn_cloud.cursor()

        # Verifier si l'objet existe dans la base de données
        id_objet = data['objet']
        nom_objet = data['nom_objet']
        objet_ip = data['objet_ip']
        cloud_cursor.execute("SELECT id_objet FROM objets WHERE id_objet = %s", (id_objet,))
        objet_existe = cloud_cursor.fetchone()

        if not objet_existe:
            # Inserer l'objet si il n'existe pas
            cloud_cursor.execute("""
                INSERT INTO objets (id_objet, nom_objet, local_objet, is_localisation, objet_ip)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_objet, nom_objet, 'New York', False, objet_ip))
            print("Objet ajouté dans la table objets", data)
        else:
            # Mettre à jour l'adresse IP de l'objet
            cloud_cursor.execute("""
                UPDATE objets SET objet_ip = %s WHERE id_objet = %s
            """, (objet_ip, id_objet))

        # Récupérer le maximum de l'ordre actuel pour l'objet
        cloud_cursor.execute("SELECT MAX(ordre_video) FROM videos_objets WHERE id_objet = %s", (id_objet,))
        max_ordre_result = cloud_cursor.fetchone()
        ordre_video = max_ordre_result[0] if max_ordre_result[0] is not None else 0

        for video in data['videos']:
            id_video = video['video']
            nom_video = video['nom_video']
            date_str = video['date']
            date_jour = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z').strftime('%Y-%m-%d') # convertir la date en format 'YYYY-MM-DD'
            nb_jouer = video['nb']
            temps_jouer = video['temps']

            # Vérifier si la vidéo existe dans videos_objets
            cloud_cursor.execute("SELECT id_video FROM videos_objets WHERE id_video = %s", (id_video,))
            video_existe = cloud_cursor.fetchone()

            if not video_existe:
                # Incrémenter l'ordre
                ordre_video += 1

                # Insérer la vidéo si elle n'existe pas
                cloud_cursor.execute("""
                    INSERT INTO videos_objets (id_video, id_objet, nom_video, taille_video, md5_video, ordre_video)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (id_video, id_objet, nom_video, 0, '', ordre_video))
                print("Vidéo ajoutée dans la table videos_objets", video)

            # Insérer ou mettre à jour les statistiques de la vidéo pour la journée
            query_cloud = """
            INSERT INTO videos_par_jour (date_jour, id_video, id_objet, nb_jouer, temps_jouer)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE nb_jouer = nb_jouer + VALUES(nb_jouer), temps_jouer = temps_jouer + VALUES(temps_jouer)
            """
            cloud_cursor.execute(query_cloud, (date_jour, id_video, id_objet, nb_jouer, temps_jouer))
            print("Vidéo ajoutée dans la table videos_par_jour", video)

        conn_cloud.commit()
        return True
    except Exception as e:
        print(f"Erreur lors de la synchronisation des données cloud avec le local: {e}")
        return False
    finally:
        if cloud_cursor: cloud_cursor.close()
        if conn_cloud: conn_cloud.close()
       
def synchroniser_donnees_locale_avec_cloud(videos):
    conn_locale = None
    cursor = None
    try:
        conn_locale = creer_connexion()
        if not conn_locale:
            print("Failed to establish local database connection")
            return False
        cursor = conn_locale.cursor()

        for video in videos:
            if 'id_video' not in video or 'nom_video' not in video:
                print(f"Manquant des informations pour la video: {video}")
                continue  # Skip la video si elle ne contient pas les informations requises

            query = """
            INSERT INTO videos (id_video, nom_video, taille_video, md5_video, ordre)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE nom_video=VALUES(nom_video), taille_video=VALUES(taille_video),
            md5_video=VALUES(md5_video), ordre=VALUES(ordre)
            """
            cursor.execute(query, (video['id_video'], video['nom_video'], video['taille_video'], video['md5_video'], video['ordre_video']))
        conn_locale.commit()
        print("Data synchronized successfully")
        return True
    except Exception as e:
        print(f"Error while synchronizing local data with cloud: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn_locale:
            conn_locale.close()
