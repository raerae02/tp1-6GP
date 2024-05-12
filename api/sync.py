from datetime import datetime
from api.database import creer_connexion_cloud

def synchroniser_donnees(data):
    try:
        conn_cloud = creer_connexion_cloud()
        if not conn_cloud:
            print("Failed to connect to the cloud database.")
            return False

        cloud_cursor = conn_cloud.cursor()

        for video in data['videos']:
            id_objet = data['objet']
            id_video = video['video']
            date_jour = video['date']

            try:
                # Attempt to parse the date
                date_parsed = datetime.strptime(date_jour, '%a, %d %b %Y %H:%M:%S GMT')
                date_jour_sql = date_parsed.strftime('%Y-%m-%d')
            except ValueError as ve:
                print(f"Date parsing error: {ve}")
                continue  # Skip this video if the date is incorrect

            nb_jouer = video['nb']
            temps_jouer = video['temps']

            # Upsert video and stats data
            cloud_cursor.execute("""
                INSERT INTO videos_objets (id_video, id_objet, nom_video, taille_video, md5_video, ordre_video)
                VALUES (%s, %s, 'Unknown', 0, '', 0)
                ON DUPLICATE KEY UPDATE id_objet = VALUES(id_objet)
            """, (id_video, id_objet))

            cloud_cursor.execute("""
                INSERT INTO videos_par_jour (date_jour, id_video, id_objet, nb_jouer, temps_jouer)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE nb_jouer = nb_jouer + VALUES(nb_jouer), temps_jouer = temps_jouer + VALUES(temps_jouer)
            """, (date_jour_sql, id_video, id_objet, nb_jouer, temps_jouer))

        conn_cloud.commit()
        print("Data synchronization completed successfully.")
        return True
    except Exception as e:
        print(f"Unhandled error during data synchronization: {e}")
        return False
    finally:
        if conn_cloud.is_connected():
            cloud_cursor.close()
            conn_cloud.close()

