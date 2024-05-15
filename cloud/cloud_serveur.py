from flask import Flask, request, jsonify, send_from_directory
import requests
from api.sync import synchroniser_donnees_cloud_avec_locale
from api.database import creer_connexion_cloud
from flask_cors import CORS as cors
import os
import magic
from werkzeug.utils import secure_filename
import traceback
from raspberrypi.controleur_video import ControleurVideos



app = Flask(__name__)
cors(app)


VIDEO_DIR = '/home/admis/tp1-6GP/raspberrypi/videos'

def fetch_object_details(id_objet):
    connection = creer_connexion_cloud()
    cursor = connection.cursor(dictionary=True)
    
    query_objet = "SELECT id_objet, nom_objet, local_objet, is_localisation, objet_ip FROM objets WHERE id_objet = %s"
    cursor.execute(query_objet, (id_objet,))
    objet = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    if not objet:
        raise ValueError("Object not found")
    
    return {
        "objet": objet['id_objet'],
        "nom_objet": objet['nom_objet'],
        "local": objet['local_objet'],
        "is_localisation": "yes" if objet['is_localisation'] else "no",
        "objet_ip": objet['objet_ip']
    }

def fetch_video_details(id_objet):
    connection = creer_connexion_cloud()
    cursor = connection.cursor(dictionary=True)
    
    query_videos = """
    SELECT id_video, nom_video, taille_video, md5_video, ordre_video 
    FROM videos_objets WHERE id_objet = %s
    """
    cursor.execute(query_videos, (id_objet,))
    videos = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return videos

def get_videos_for_object(id_objet):
    objet_details = fetch_object_details(id_objet)
    video_details = fetch_video_details(id_objet)
    response_data = {
        **objet_details,
        "videos": video_details
    }
    print("response_data qui sera envoyer au serveur local: ", response_data)
    return response_data

# Synchroniser les données avec la base de données cloud, puis retourner les vidéos pour l'objet spécifié
def synchronize_data(data):
    success = synchroniser_donnees_cloud_avec_locale(data)
    print("Succes de la synchronisation: ", success)
    if success:
        try:
            response_data = get_videos_for_object(data['objet'])
            return response_data, 200
        except Exception as e:
            return {"success": False, "message": str(e)}, 500
    else:
        return {"success": False}, 500

# Endpoint pour la synchronisation des données
@app.route('/synchronize', methods=['POST'])
def synchronize():
    data = request.json
    print("Data recu pour synchronisation: ", data)
    response_data, status_code = synchronize_data(data)
    return jsonify(response_data), status_code

# Obtenir les détails des objets
@app.route('/objets/status', methods=['GET'])
def get_objets_status():
    conn_cloud = creer_connexion_cloud()
    if not conn_cloud:
        return jsonify({"success": False}), 500

    cloud_cursor = conn_cloud.cursor()
    cloud_cursor.execute("SELECT id_objet, nom_objet, local_objet, is_localisation FROM objets")
    objets = cloud_cursor.fetchall()

    cloud_cursor.close()
    conn_cloud.close()

    return jsonify({"success": True, "objets": objets}), 200
    
# Servir les fichiers vidéo
@app.route('/videos/<string:video_name>', methods=['GET'])
def servir_videos(video_name):
    video_path = os.path.join(VIDEO_DIR, video_name)
    print(f"Requested video path: {video_path}")
    
    if os.path.exists(video_path):
        print("Sending video")
        return send_from_directory(VIDEO_DIR, video_name)
    else:
        return jsonify({"success": False, "message": "Video file not found"}), 404

# Envoyer la commande à l'objet spécifié
def envoyer_commande_objet(id_objet, command):
    try:
        conn_cloud = creer_connexion_cloud()
        cursor = conn_cloud.cursor()
        cursor.execute("SELECT objet_ip FROM objets WHERE id_objet = %s", (id_objet,))
        result = cursor.fetchone()
        cursor.close()
        conn_cloud.close()
        print("result: ", result)   
        if result:
            pi_url = f"http://{result[0]}:5000/execute_command"
            print("pi_url: ", pi_url)
            response = requests.post(pi_url, json={"command": command}, timeout=10)
            response.raise_for_status()
            print(f"Command '{command}' sent to Raspberry Pi {id_objet}: {response.json()}")
            return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to send command '{command}' to Raspberry Pi {id_objet}: {e}")
        return {"success": False}

# Envoyer la commande à l'objet spécifié
@app.route('/send_command/<int:id_objet>', methods=['POST'])
def send_command(id_objet):
    command = request.json.get('command')
    response = envoyer_commande_objet(id_objet, command)
    return jsonify(response), 200 if response.get("success") else 500

@app.route('/get-stats', methods=['GET'])
def get_stats():
    try:
        conn_cloud = creer_connexion_cloud()
        if not conn_cloud:
            return jsonify({"success": False, "message": "Failed to connect to cloud database"}), 500
        cloud_cursor = conn_cloud.cursor(dictionary=True)
        
        query = """
            SELECT o.id_objet, o.nom_objet, o.local_objet, o.is_localisation, o.objet_ip,
            SUM(vpj.nb_jouer) AS nb_jouer_total, SUM(vpj.temps_jouer) AS temps_total
            FROM objets o
            LEFT JOIN videos_par_jour vpj ON o.id_objet = vpj.id_objet
            WHERE vpj.date_jour = CURDATE()
            GROUP BY o.id_objet
        """
        cloud_cursor.execute(query)
        stats = cloud_cursor.fetchall()
    except:
        return jsonify({"success": False, "message": "Failed to fetch stats"}), 500
    finally:
        cloud_cursor.close()
        conn_cloud.close()
        
    
    return jsonify({"success": True, "stats": stats}), 200

@app.route('/get-videos/<int:objet_id>', methods=['GET'])
def get_videos(objet_id):
    try:
        conn_cloud = creer_connexion_cloud()
        if not conn_cloud:
            return jsonify({"success": False, "message": "Failed to connect to cloud database"}), 500
        cloud_cursor = conn_cloud.cursor(dictionary=True)
        
        query = """
            SELECT id_video, nom_video, taille_video, md5_video, ordre_video
            FROM videos_objets WHERE id_objet = %s
        """
        cloud_cursor.execute(query, (objet_id,))
        videos = cloud_cursor.fetchall()
    except:
        return jsonify({"success": False, "message": "Failed to fetch videos"}), 500
    finally:
        cloud_cursor.close()
        conn_cloud.close()
        
    
    return jsonify({"success": True, "videos": videos}), 200

@app.route('/upload_video', methods=['POST'])
def upload_video():
    video = request.files['video']
    id_objet = request.form.get('id_objet')
    
    if not video:
        return jsonify({"success": False, "message": "No video uploaded"}), 400

    filename = secure_filename(video.filename)
    save_path = os.path.join(VIDEO_DIR, filename)
    
    with open(save_path, "wb") as f:
        chunk_size = 4096 
        while True:
            chunk = video.stream.read(chunk_size)
            if not chunk:
                break
            f.write(chunk)
    
    video_size = os.path.getsize(save_path)
#    md5_checksum = calculate_md5(save_path)
    save_video_in_database(filename, id_objet, video_size)

    return jsonify({'success': True, 'message': 'Video uploaded successfully!', 'path': save_path}), 200

def save_video_in_database(nom_video, id_objet, video_size):
    print("Saving video in database", nom_video, id_objet, video_size)
    conn_cloud = creer_connexion_cloud()
    if not conn_cloud:
        print("Failed to connect to cloud database")
        return jsonify({"success": False, "message": "Failed to connect to cloud database"}), 500
    cursor = conn_cloud.cursor()
    try:
        query = """
        INSERT INTO videos_objets (id_objet, nom_video, taille_video, md5_video, ordre_video)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (id_objet, nom_video, video_size, '', 0))
        conn_cloud.commit()
        print(f"Rows affected: {cursor.rowcount}")
        if cursor.rowcount == 0:
            print("No rows inserted, check if id_objet exists and is correct.")
    except Exception as e:
        print(f"Erreur lors de l'insertion de la video dans la base de donnees: {e}")
        print(traceback.format_exc())  
        conn_cloud.rollback()
    finally:
        cursor.close()
        conn_cloud.close()


    @app.route('/clignoter_led/<int:id_objet>', methods=['POST'])
    def clignoter_led():
        if ControleurVideos:
            ControleurVideos.clignoter_led(id_objet,3)  # Clignoter la LED 3 fois
            return jsonify({"success": True, "message": "LED clignotée"})
        else:
            return jsonify({"success": False, "message": "Controller instance not set"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)