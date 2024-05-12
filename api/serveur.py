from datetime import datetime
from flask import Flask, jsonify, request
from api.database import creer_connexion

app = Flask(__name__)

# Get the current date in the correct format
def get_current_date():
    return datetime.now().strftime('%Y-%m-%d')

@app.route('/videos', methods=['GET'])
def lister_videos():
    connection = creer_connexion()
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
    connection = creer_connexion()
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
    connection = creer_connexion()
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
    today_date = get_current_date()
    connection = creer_connexion()
    cursor = connection.cursor()
    
    query = """
    SELECT id_nb FROM nb_video_jour
    WHERE date_jour = %s AND id_video = %s
    """
    cursor.execute(query, (today_date, id_video))
    result = cursor.fetchone()
    
    if result:
        query = """
        UPDATE nb_video_jour
        SET nb_jouer = nb_jouer + 1, temps_total = temps_total + %s
        WHERE id_nb = %s
        """
        cursor.execute(query, (temps_jouer, result[0]))
    else:
        query = """
        INSERT INTO nb_video_jour (date_jour, id_video, nb_jouer, temps_total)
        VALUES (%s, %s, 1, %s)
        """
        cursor.execute(query, (today_date, id_video, temps_jouer))
    
    connection.commit()
    cursor.close()
    connection.close()

@app.route('/stats/jour', methods=['GET'])
def obtenir_stats_jour():
    today_date = get_current_date()
    connection = creer_connexion()
    cursor = connection.cursor(dictionary=True)
    
    query_stats_par_video = """
    SELECT id_video, SUM(nb_jouer) AS nb_jouer, SUM(temps_total) AS temps_total
    FROM nb_video_jour WHERE date_jour = %s GROUP BY id_video
    """
    cursor.execute(query_stats_par_video, (today_date,))
    stats_par_video = cursor.fetchall()

    query_stats_globales = """
    SELECT SUM(nb_jouer) AS nb_jouer_total, SUM(temps_total) AS temps_total
    FROM nb_video_jour WHERE date_jour = %s
    """
    cursor.execute(query_stats_globales, (today_date,))
    stats_globales = cursor.fetchone()  

    cursor.close()
    connection.close()
    
    response = {
        'stats_par_video': stats_par_video,
        'stats_globales': stats_globales
    }
    
    return jsonify(response)

@app.route('/video/jouees', methods=['GET'])
def obtenir_videos_jouees():
    today_date = get_current_date()
    connection = creer_connexion()
    cursor = connection.cursor(dictionary=True)

    
    query = """
    SELECT v.id_video, %s AS date_jour, nvj.nb_jouer, nvj.temps_total
    FROM videos v
    JOIN nb_video_jour nvj ON v.id_video = nvj.id_video
    WHERE nvj.date_jour = %s
    """
    cursor.execute(query, (today_date, today_date))

    videos_jouees = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(videos_jouees)