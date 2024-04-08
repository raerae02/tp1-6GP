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
        self.arret_demande = False
        self.debut_lecture = 0
          
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
        playback_thread = threading.Thread(target=self.demarrer_video)
        playback_thread.start()

    def demarrer_video(self):
        while self.video_index < len(self.videos) and not self.arret_demande:
            video = self.videos[self.video_index]
            self.parent.afficher_nom_video(video['nom_video'])
            video_path = "./client/videos/" + video['nom_video']
            id_video = video['id_video']
            print("demarrer video : " +str(id_video) + " " + video_path)
            
            self.marquer_video_courante(id_video)
            
            cap = cv2.VideoCapture(video_path)
            self.debut_lecture = time.time()

            while cap.isOpened() and not self.arret_demande:
                ret, frame = cap.read()
                if ret:
                    # Convertir l'image en RGB pour l'affichage dans Tkinter
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(frame)
                    photo = ImageTk.PhotoImage(image=image)

                    self.canvas_video.config(image=photo)
                    self.canvas_video.image = photo
                    self.canvas_video.update_idletasks() 
                    time.sleep(1/30)
                else:
                    break
            
            # Calculer la durée de la lecture
            duree_lecture = time.time() - self.debut_lecture
            cap.release()
            
            self.terminer_video_courante(id_video, duree_lecture)
            
            self.video_index += 1
            if self.video_index >= len(self.videos) or self.arret_demande:
                # Toutes les vidéos ont déjà été jouées ou arrêt demandé
                print("Toutes les vidéos ont été jouées ou arrêt demandé.")
                self.parent.afficher_nom_video(" ")
                self.parent.lecteur_video_actuel = None
                self.parent.videos_en_lecture = False
                self.fenetre_video.destroy()
                break  

    def arreter_lecture(self):
        if self.video_index > 0 and self.video_index <= len(self.videos):
            id_video = self.videos[self.video_index - 1]['id_video'] 
            temps_jouer = time.time() - self.debut_lecture 
            self.terminer_video_courante(id_video, temps_jouer)
        
        self.arret_demande = True
        self.video_index = 0  
        self.parent.videos_en_lecture = False 
        self.fenetre_video.destroy()  
