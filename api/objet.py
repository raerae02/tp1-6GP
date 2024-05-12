import requests
import time
import json
import os
from datetime import datetime
import hashlib
from api.sync import synchroniser_donnees_locale_avec_cloud


# Configuration
SERVER_URL = 'http://4.206.210.212:5000/'
BUFFER_FILE = 'data_buffer.json'
ID_OBJET = 2
LOCALISATION = 'Montreal'
VIDEO_DIR = './../raspberrypi/videos'

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
        "is_display_ads": "yes" if videos_jouees else "no",
        "videos": [
            {
                "video": video["id_video"],
                "date": video["date_jour"],
                "nb": video["nb_jouer"],
                "temps": video["temps_total"]
            } for video in videos_jouees
        ]
    }
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
    

def synchronize_videos(videos):
    for video in videos:
        video_path = os.path.join(VIDEO_DIR, video['nom_video'])
        if not os.path.exists(video_path) or calculate_md5(video_path) != video['md5_video']:
            print(f"Video {video['nom_video']} missing or checksum mismatch. Downloading...")
            download_video(f"{SERVER_URL}/videos/{video['id_video']}", video_path)


def send_data_to_server(data):
    try:
        response = requests.post(f"{SERVER_URL}/synchronize", json=data, timeout=10)
        response.raise_for_status()
        response_data = response.json()
        print(f"Les donnees ont ete envoyer correctement: {response.json()}")
        
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
        print(f"Echec du telechargement de la video: {e}")

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