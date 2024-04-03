import cv2
import tkinter as tk
from tkinter import Toplevel

class LecteurVideo:
    def __init__(self, parent, videos):
        self.parent = parent
        self.videos = videos
        self.video_index = 0  # Commencer par la première vidéo
        self.window = Toplevel(self.parent)
        self.window.title("Lecteur de Vidéos")
        self.play_video()

    def play_video(self):
        if self.video_index < len(self.videos):
            video_path = self.videos[self.video_index]
            cap = cv2.VideoCapture(video_path)

            # Cette partie est simplifiée pour la démonstration.
            # Vous devrez mettre en place une boucle de lecture appropriée
            # et gérer l'affichage des frames dans la fenêtre Tkinter ou Toplevel.
            while cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    # Afficher le frame (à intégrer dans Tkinter)
                    cv2.imshow('Video', frame)
                    cv2.waitKey(25)  # Attendre 25ms ou jusqu'à ce qu'une touche soit pressée
                else:
                    break

            cap.release()
            cv2.destroyAllWindows()
            self.video_index += 1  # Passer à la vidéo suivante
        else:
            print("Fin des vidéos.")
            self.window.destroy()

    # Ajoutez d'autres méthodes au besoin pour contrôler la lecture (pause, suivant, précédent, etc.)
