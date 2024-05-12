import requests
import time
import json
import os
from datetime import datetime

# Configuration
SERVER_URL = 'http://4.206.210.212:5000/synchronize'
BUFFER_FILE = 'data_buffer.json'
ID_OBJET = 1  
LOCALISATION = 'Montreal'

def fetch_videos_jouees():
    try:
        response = requests.get('http://localhost:5000/video/jouees', timeout=10)
        response.raise_for_status()
        videos_jouees = response.json()
        return videos_jouees
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch videos jouees: {e}")
        return []

def collect_data():
    # Simulate collecting video data
    print("Collecting data...")
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

def send_data_to_server(data):
    try:
        response = requests.post(SERVER_URL, json=data, timeout=10)
        response.raise_for_status()
        print(f"Data sent successfully: {response.json()}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Failed to send data: {e}")
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

