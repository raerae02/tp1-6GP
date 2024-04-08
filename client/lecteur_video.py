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
        self.debut_lecture = 0
        
        self.arret_demande = threading.Event()  
        self.playback_thread = None  
        
        self.initialiser_fenetre_video()
    
    def initialiser_fenetre_video(self):
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

    # On debute les threads pour la lecture des vidéos
    def debuter_video_playback(self):
        # Si un thread de lecture est déjà en cours, on l'arrête
        if self.playback_thread is not None and self.playback_thread.is_alive():
            self.arret_demande.set()  
            self.playback_thread.join()  
            
        self.arret_demande.clear()  
        self.playback_thread = threading.Thread(target=self.demarrer_video) 
        self.playback_thread.start()


    def demarrer_video(self):
        while self.video_index < len(self.videos) and not self.arret_demande.is_set():
            video = self.videos[self.video_index]
            self.parent.afficher_nom_video(video['nom_video'])
            video_path = "./client/videos/" + video['nom_video']
            id_video = video['id_video']
            print("demarrer video : " +str(id_video) + " " + video_path)
            
            self.marquer_video_courante(id_video)
            
            cap = cv2.VideoCapture(video_path)
            self.debut_lecture = time.time()

            while cap.isOpened() and not self.arret_demande.is_set():
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
                if self.arret_demande.is_set():
                    break
            if self.arret_demande.is_set():
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
    
    def passer_au_video_suivant(self):
        if not self.playback_thread or not self.playback_thread.is_alive():
            print("Aucune vidéo en cours de lecture.")
            return

        if self.video_index >= 0 and self.video_index < len(self.videos):
            id_video = self.videos[self.video_index]['id_video']
            temps_jouer = time.time() - self.debut_lecture  
            print("Passer au vidéo suivante : " + str(id_video) + " " + str(temps_jouer))
            self.terminer_video_courante(id_video, temps_jouer)

        self.arret_demande.set()
        
        self.verifier_fin_thread()


    def verifier_fin_thread(self):
        if self.playback_thread.is_alive():
            self.fenetre_video.after(100, self.verifier_fin_thread)
        else:
            self.on_fin_thread()

    def on_fin_thread(self):
        self.video_index += 1
        if self.video_index >= len(self.videos):
            print("Toutes les vidéos ont déjà été jouées.")
            self.video_index = 0  

        self.arret_demande.clear()
        print("Passer au vidéo suivante.")
        self.debuter_video_playback()