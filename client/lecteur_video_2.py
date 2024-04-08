import cv2
import requests
import time
import threading
import tkinter as tk
from PIL import Image, ImageTk

class LecteurVideo:
    def __init__(self, parent, videos):
        self.parent = parent
        self.videos = videos
        self.video_index = 0
        self.playback_thread = None
        self.stop_event = threading.Event() 

        self.debut_lecture = 0
        self.setup_ui()
        
    def setup_ui(self):
        self.fenetre_video = tk.Toplevel(self.parent)
        self.fenetre_video.title("Lecture Vidéo")
        self.fenetre_video.geometry("800x600")
        self.canvas_video = tk.Label(self.fenetre_video)
        self.canvas_video.pack()
          
    def marquer_video_courante(self, id_video):
        requests.post('http://localhost:5000/video/current', json={"id_video": id_video})

    def terminer_video_courante(self, id_video, temps_jouer):
        requests.put('http://localhost:5000/video/current', json={"id_video": id_video, "temps_jouer": temps_jouer})
        self.parent.stats = self.parent.obtenir_stats_jour()
        self.parent.mise_a_jour_ui_avec_stats(self.parent.stats, id_video)

    def debuter_video_playback(self):
        self.stop_event.clear()
        self.playback_thread = threading.Thread(target=self.jouer_video, daemon=True)
        self.playback_thread.start()

    def arreter_video_playback(self):
        print("Arrêter la lecture de la vidéo.")
        self.stop_event.set()
        
    def jouer_video(self):
        if self.video_index < len(self.videos):
            video = self.videos[self.video_index]
            video_path = "./client/videos/" + video['nom_video']
            id_video = video['id_video']
            self.mettre_a_jour_info_video(video)
            debut_lecture = time.time()
            cap = cv2.VideoCapture(video_path)
            while not self.stop_event.is_set() and cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    self.afficher_frame(frame)
                    time.sleep(1/30)  
                else:
                    break
            cap.release()
            duree_lecture = time.time() - debut_lecture
            self.terminer_video_courante(id_video, duree_lecture)
            self.video_index += 1
            if self.video_index >= len(self.videos):
                self.video_index = 0  
        self.cleanup_after_playback()
                
    def mettre_a_jour_info_video(self, video):
        self.parent.afficher_nom_video(video['nom_video'])
        self.marquer_video_courante(video['id_video'])

    
    def afficher_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame)
        photo = ImageTk.PhotoImage(image=image)
        def mettre_a_jour_image():
            if self.canvas_video.winfo_exists(): 
                self.canvas_video.config(image=photo)
                self.canvas_video.image = photo
    
        self.fenetre_video.after(0, mettre_a_jour_image)
        
    def calculer_duration_video(self):
        if self.debut_lecture:
            return time.time() - self.debut_lecture
        return 0
    
    def cleanup_after_playback(self):
        self.fenetre_video.after(0, self.nettoyer_lecteur_video)
                
    def nettoyer_lecteur_video(self):
        if self.fenetre_video.winfo_exists():  
            self.fenetre_video.destroy()
        self.parent.afficher_nom_video(" ")
        self.parent.lecteur_video_actuel = None
        self.parent.videos_en_lecture = False
        
    def jouer_prochaine_video(self):
        print("Jouer prochaine vidéo.")
        self.arreter_video_playback()  
        self.video_index = (self.video_index + 1) % len(self.videos)  
        self.debuter_video_playback() 
       