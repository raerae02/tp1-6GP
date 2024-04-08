from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

def create_connection():
    connection = None
    try:
        print('Connecting to the MySQL database...')
        connection = mysql.connector.connect(
            host='localhost',  
            user='root',
            password='password',
            database='videos_db'
        )
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

@app.route('/videos', methods=['GET'])
def lister_videos():
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM videos ORDER BY ordre"
    cursor.execute(query)
    videos = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(videos)

@app.route('/video/current', methods=['POST'])
def marquer_video_courante():
    data = request.json
    connection = create_connection()
    cursor = connection.cursor()
    query = """
    INSERT INTO video_courant (id_video, debut_video, fin_video, temps_jouer)
    VALUES (%s, NOW(), NULL, 0)
    """
    cursor.execute(query, (data['id_video'],))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"success": True}), 201

@app.route('/video/current', methods=['PUT'])
def terminer_video_courante():
    data = request.json
    connection = create_connection()
    cursor = connection.cursor()
    query = """
    UPDATE video_courant
    SET fin_video = NOW(), temps_jouer = %s
    WHERE id_video = %s AND fin_video IS NULL
    """
    cursor.execute(query, (data['temps_jouer'], data['id_video']))
    mettre_a_jour_stats(data['id_video'], data['temps_jouer'])
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"success": True})

def mettre_a_jour_stats(id_video, temps_jouer):
    connection = create_connection()
    cursor = connection.cursor()
    
    # Vérifier si une entrée pour aujourd'hui et cette vidéo existe déjà
    query = """
    SELECT id_nb FROM nb_video_jour
    WHERE date_jour = CURDATE() AND id_video = %s
    """
    cursor.execute(query, (id_video,))
    result = cursor.fetchone()
    
    if result:
        # Mise à jour de l'entrée existante
        query = """
        UPDATE nb_video_jour
        SET nb_jouer = nb_jouer + 1, temps_total = temps_total + %s
        WHERE id_nb = %s
        """
        cursor.execute(query, (temps_jouer, result[0]))
    else:
        # Création d'une nouvelle entrée
        query = """
        INSERT INTO nb_video_jour (date_jour, id_video, nb_jouer, temps_total)
        VALUES (CURDATE(), %s, 1, %s)
        """
        cursor.execute(query, (id_video, temps_jouer))
    
    connection.commit()
    cursor.close()
    connection.close()
    
@app.route('/stats/jour', methods=['GET'])
def obtenir_stats_jour():
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Requête pour les statistiques par vidéo
    query_stats_par_video = """
    SELECT id_video, SUM(nb_jouer) AS nb_jouer, SUM(temps_total) AS temps_total
    FROM nb_video_jour
    WHERE date_jour = CURDATE()
    GROUP BY id_video
    """
    cursor.execute(query_stats_par_video)
    stats_par_video = cursor.fetchall()

    # Requête pour les statistiques totales
    query_stats_globales = """
    SELECT SUM(nb_jouer) AS nb_jouer_total, SUM(temps_total) AS temps_total
    FROM nb_video_jour
    WHERE date_jour = CURDATE()
    """
    cursor.execute(query_stats_globales)
    stats_globales = cursor.fetchone()  

    cursor.close()
    connection.close()
    
    reponse = {
        'stats_par_video': stats_par_video,
        'stats_globales': stats_globales
    }
    
    return jsonify(reponse)
