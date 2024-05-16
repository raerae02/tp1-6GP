import requests
import time
import json
import os
from datetime import datetime
import hashlib
from api.sync import synchroniser_donnees_locale_avec_cloud
import os
from dotenv import load_dotenv


load_dotenv()

# Configuration

BUFFER_FILE = 'data_buffer.json'

SERVER_URL = os.getenv('SERVER_URL')
ID_OBJET = os.getenv('ID_OBJET')
VIDEO_DIR = os.getenv('VIDEO_DIR')
NOM_OBJET = os.getenv('NOM_OBJET')
RASPBERRY_PI_URL = os.getenv('RASPBERRY_PI_URL')

# Methode qui recupere les videos jouees depuis le serveur local
def fetch_videos_jouees():
    try:
        response = requests.get('http://localhost:5000/video/jouees', timeout=10)
        response.raise_for_status()
        videos_jouees = response.json()
        print(f"Videos jouees: {videos_jouees}")
        return videos_jouees
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch videos jouees: {e}")
        return []

def collect_data():
    videos_jouees = fetch_videos_jouees()
    data = {
        "objet": ID_OBJET,
        "nom_objet": NOM_OBJET,
        "objet_ip": RASPBERRY_PI_URL,
        "is_display_ads": "yes" if videos_jouees else "no",
        "videos": [
            {
                "video": video["id_video"],
                "nom_video": video["nom_video"],
                "date": video["date_jour"],
                "nb": video["nb_jouer"],
                "temps": video["temps_total"]
            } for video in videos_jouees
        ]
    }
    print(f"Data collected: {data}")
 
    return data

def save_data_locally(data):
    if os.path.exists(BUFFER_FILE):
        with open(BUFFER_FILE, 'r') as file:
            buffered_data = json.load(file)
    else:
        buffered_data = []

    buffered_data.append(data)
    with open(BUFFER_FILE, 'w') as file:
        json.dump(buffered_data, file)
    
# Methode qui synchronise les videos locales avec les videos du cloud.
# Elle supprime les videos locales qui ne sont plus presentes dans le cloud
# Si une video est manquante ou si le checksum est different, elle sera telechargee
def synchronize_videos(videos):
    for video in videos:
        video_path = os.path.join(VIDEO_DIR, video['nom_video'])
        if not os.path.exists(video_path): # or calculate_md5(video_path) != video['md5_video']:
            print(f"Video {video['nom_video']} missing or checksum mismatch. Downloading...")
            download_video(f"{SERVER_URL}/videos/{video['nom_video']}", video_path)


def send_data_to_server(data):
    try:
        response = requests.post(f"{SERVER_URL}/synchronize", json=data, timeout=10)
        response.raise_for_status()
        response_data = response.json()
        print(f"Les donnees ont ete envoyer correctement: {response_data}")
        
        if response_data and 'is_localisation' in response_data:
            activer_localisation(response_data['objet'], response_data['is_localisation'])
        
        if response_data and 'videos' in response_data:
            synchronize_videos(response_data['videos'])
            synchroniser_donnees_locale_avec_cloud(response_data['videos'])
        return True
    except requests.exceptions.RequestException as e:
        print(f"Echec de l'envoi des donnees: {e}")
        return False

def load_and_send_buffered_data():
    if os.path.exists(BUFFER_FILE):
        with open(BUFFER_FILE, 'r') as file:
            buffered_data = json.load(file)
        
        all_sent = True
        for data in buffered_data:
            if not send_data_to_server(data):
                all_sent = False
                break
        
        if all_sent:
            os.remove(BUFFER_FILE)

def run_data_collection():
    while True:
        print("Data collection cycle started.")
        fetch_and_delete_videos()
        data = collect_data()

        if not send_data_to_server(data):
            print("Saving data locally due to failed connection.")
            save_data_locally(data)
        
        load_and_send_buffered_data()
        
        time.sleep(60)

def download_video(video_url, video_path):
    try:
        response = requests.get(video_url, stream=True)
        response.raise_for_status()
        with open(video_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Telechargement: {video_path}")
    except requests.exceptions.RequestException as e:
        print(f"Echec de telechargement de la video: {e}")

def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
    except FileNotFoundError:
        print(f"File {file_path} not found for MD5 calculation.")
        return None
    return hash_md5.hexdigest()

def activer_localisation(id_objet, is_localisation):
    try:
        if is_localisation not in ['yes', 'no']:
            print(f"Valeur de localisation invalide: {is_localisation}")
            return
        response = requests.post("http://localhost:5000/set-localisation", json={"id_objet": id_objet, "localisation": is_localisation}, timeout=10)
        response.raise_for_status()
        print(f"Localisation {'activée' if is_localisation == 'yes' else 'désactivée'} avec succès")
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de l'activation de la localisation: {e}")
        
def  fetch_and_delete_videos():
    print("Fetching and deleting videos...")
    response = requests.get(f"{SERVER_URL}/get-deleted-videos")
    if response.status_code == 200:
        print("Fetched deleted videos.")
        data = response.json()
        deleted_videos = data['deleted_videos']
        print(f"Deleted videos: {deleted_videos}")
        for video in deleted_videos:
            # if video['id_objet'] == ID_OBJET:
            print(f"Deleting video {video['id_video']}...")
            delete_local_video(video['nom_video'])
            delete_videos_from_database(video['id_video'])
            print(f"Deleted video {video['id_video']} locally.")

def delete_local_video(nom_video):
    video_path = os.path.join(VIDEO_DIR, nom_video)
    if os.path.exists(video_path):
        os.remove(video_path)
        print(f"Deleted video {nom_video} locally.")
    else:
        print(f"Video {nom_video} not found locally.")
        
def delete_videos_from_database(id_video):
    try:
        response = requests.delete("http://localhost:5000/video/{id_video}")
        response.raise_for_status()
        print(f"Deleted video {id_video} from database.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to delete video {id_video} from database: {e}")