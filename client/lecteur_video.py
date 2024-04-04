import cv2
import requests
import time
import threading

class LecteurVideo:
    def __init__(self, parent, videos):
        self.parent = parent
        self.videos = videos
        self.video_index = 0
        self.arret_demande = False  
          
    def marquer_video_courante(self, id_video):
        requests.post('http://localhost:5000/video/current', json={"id_video": id_video})

    def terminer_video_courante(self, id_video, temps_jouer):
        requests.put('http://localhost:5000/video/current', json={"id_video": id_video, "temps_jouer": temps_jouer})
        self.parent.stats = self.parent.obtenir_stats_jour()
        self.parent.mise_a_jour_ui_avec_stats(self.parent.stats)

    def debuter_video_playback(self):
        playback_thread = threading.Thread(target=self.demarrer_video)
        playback_thread.start()

    def demarrer_video(self):
        if self.video_index < len(self.videos):
            video = self.videos[self.video_index]
            self.parent.afficher_nom_video(video['nom_video'])
            video_path = "./client/videos/" + video['nom_video']
            id_video = video['id_video']
            
            self.marquer_video_courante(id_video)
            
            cap = cv2.VideoCapture(video_path)
            debut_lecture = time.time()

            while cap.isOpened():
                if self.arret_demande:  
                    print("Arrêt demandé.")
                    break
                ret, frame = cap.read()
                if ret:
                    cv2.imshow('Video', frame)
                    if cv2.waitKey(25) & 0xFF == ord('q'):
                        break
                else:
                    break
            
            # Calculer la durée de la lecture
            duree_lecture = time.time() - debut_lecture
            cap.release()
            cv2.destroyAllWindows()
            
            self.terminer_video_courante(id_video, duree_lecture)
            
            self.video_index += 1  
            
        else:
            # Si on entre ici, c'est que toutes les vidéos ont déjà été jouées
            print("Toutes les vidéos ont été jouées.")
            self.parent.afficher_nom_video(" ")
            self.parent.videos_en_lecture = False

    def arreter_lecture(self):
        self.arret_demande = True
        cv2.destroyAllWindows()
