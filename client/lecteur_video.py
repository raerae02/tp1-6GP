import cv2
import requests
import time

class LecteurVideo:
    def __init__(self, parent, videos):
        self.parent = parent
        self.videos = videos
        self.video_index = 0  

        self.play_video()
        
    def marquer_video_courante(self, id_video):
        requests.post('http://localhost:5000/video/current', json={"id_video": id_video})

    def terminer_video_courante(self, id_video, temps_jouer):
        requests.put('http://localhost:5000/video/current', json={"id_video": id_video, "temps_jouer": temps_jouer})


    def play_video(self):
            if self.video_index < len(self.videos):
                video = self.videos[self.video_index]
                self.parent.afficher_nom_video(video['nom_video'])
                video_path = "./client/videos/" + video['nom_video'] 
                id_video = video['id_video']
                
                self.marquer_video_courante(id_video)
                
                cap = cv2.VideoCapture(video_path)
                debut_lecture = time.time() 

                while cap.isOpened():
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
                print("Fin des vidéos.")
                self.parent.afficher_nom_video(" ")
                self.window.destroy()
                self.parent.videos_en_lecture = False 

