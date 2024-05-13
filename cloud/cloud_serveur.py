from flask import Flask, request, jsonify, send_from_directory
import requests
from api.sync import synchroniser_donnees_cloud_avec_locale
from api.database import creer_connexion_cloud
from flask_cors import CORS as cors
import os



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
    print("response_data: ", response_data)
    return response_data

# Synchroniser les données avec la base de données cloud, puis retourner les vidéos pour l'objet spécifié
def synchronize_data(data):
    success = synchroniser_donnees_cloud_avec_locale(data)
    print("success: ", success)
    if success:
        try:
            response_data = get_videos_for_object(data['objet'])
            return response_data, 200
        except Exception as e:
            return {"success": False, "message": str(e)}, 500
    else:
        return {"success": False}, 500

# Synchroniser les données avec la base de données cloud
@app.route('/synchronize', methods=['POST'])
def synchronize():
    data = request.json
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

@app.route('/upload_video', methods=['POST'])
def upload_video():
    video_file = request.files['video']
    if not video_file:
        return jsonify({"success": False, "message": "No video file provided"}), 400
    
    # Handle the video upload here, e.g., save the file to a cloud storage
    
    return jsonify({"success": True}), 200
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)