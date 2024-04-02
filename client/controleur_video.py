import tkinter as tk
import os
from affichage_date_heure import AffichageDateHeure

class ControleurVideos(tk.Tk):
    def __init__(self):
        super().__init__() 
        self.title("Contrôleur de Vidéos")  
        self.geometry("400x300")  
        self.creer_widgets()
        self.after(30000, self.demarrer_videos)
    
    def creer_widgets(self):
        # Label au début de l'écran
        self.etiquette = tk.Label(self, text="Contrôleur des vidéos")
        self.etiquette.grid(row=0, column=0, columnspan=3, pady=(10, 20))  

        # Labels 
        self.text_1 = tk.Label(self, text="Vidéo en cours :")
        self.text_1.grid(row=1, column=0, sticky='w', padx=10)

        self.text_2 = tk.Label(self, text="Nombre joué aujourd'hui :")
        self.text_2.grid(row=2, column=0, sticky='w', padx=10)

        self.text_3 = tk.Label(self, text="Nombre total des vidéos jouées aujourd'hui :")
        self.text_3.grid(row=3, column=0, sticky='w', padx=10)

        # Boutons
        self.boutons_locatisation = tk.Button(self, text="Localisation / Arrêt")
        self.boutons_locatisation.grid(row=4, column=0, pady=(20, 5), padx=(20, 0))  

        self.boutons_suivant = tk.Button(self, text="Passer au vidéo suivant")
        self.boutons_suivant.grid(row=5, column=0, pady=5, padx=(40, 0))  

        self.boutons_arreter = tk.Button(self, text="Arrêter les vidéos")
        self.boutons_arreter.grid(row=6, column=0, padx=(60, 10), pady=5)  

        self.boutons_demarrer = tk.Button(self, text="Démarrer les vidéos", command=self.demarrer_videos)
        self.boutons_demarrer.grid(row=6, column=1, padx=(10, 60), pady=5)

    def lister_videos(self, dossier):
        extensions = ['.mp4', '.avi'] 
        fichiers = [f for f in os.listdir(dossier) if os.path.isfile(os.path.join(dossier, f))]
        return [f for f in fichiers if any(f.endswith(ext) for ext in extensions)]

    def demarrer_videos(self):
        videos = self.lister_videos('./client/videos')
        if videos:
            print("Lancer la lecture des vidéos ici.")
        else:
            self.afficher_ecran_date_heure()

    def afficher_ecran_date_heure(self):
        self.withdraw() 
        fenetre_date_heure = AffichageDateHeure(self)
        fenetre_date_heure.mainloop()