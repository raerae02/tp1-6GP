import tkinter as tk
import os
import requests
from client.affichage_date_heure import AffichageDateHeure
from client.lecteur_video import LecteurVideo
# import RPi.GPIO as GPIO

# ledPin = 12
# sensorPin = 11    


# def setup():
#     GPIO.setmode(GPIO.BOARD)        # use PHYSICAL GPIO Numbering
#     GPIO.setup(ledPin, GPIO.OUT)    # set ledPin to OUTPUT mode
#     GPIO.setup(sensorPin, GPIO.IN)  # set sensorPin to INPUT mode

# setup()

class ControleurVideos(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Contrôleur de Vidéos")
        self.geometry("600x300")
        
        self.nom_video_en_cours = tk.StringVar(value="Vidéo en cours : ")
        self.nb_jouer_aujourdhui = tk.StringVar(value="Nombre joué aujourd'hui : ")
        self.temps_jouer_aujourdhui = tk.StringVar(value="Temps joué aujourd'hui : ")
        self.nb_total_videos_joues = tk.StringVar(value="Nombre total des vidéos jouées aujourd'hui : ")
        
        self.lecteur_video_actuel = None
        self.videos_en_lecture = False

        self.stats = self.obtenir_stats_jour()
        self.creer_widgets()
        self.mise_a_jour_ui_avec_stats(self.stats)

        self.after(30000, self.demarrer_videos)

    def creer_widgets(self):
        # Label au début de l'écran
        self.etiquette = tk.Label(self, text="Contrôleur des vidéos")
        self.etiquette.grid(row=0, column=0, columnspan=3, pady=(10, 20))

        # Labels 
        self.text_1 = tk.Label(self, textvariable=self.nom_video_en_cours)
        self.text_1.grid(row=1, column=0, sticky='w', padx=10)
        
        self.text_2 = tk.Label(self, textvariable=self.nb_jouer_aujourdhui)
        self.text_2.grid(row=2, column=0, sticky='w', padx=10)
        
        self.text_3 = tk.Label(self, textvariable=self.temps_jouer_aujourdhui)
        self.text_3.grid(row=2, column=1, sticky='w', padx=0)

        self.text_4 = tk.Label(self, textvariable=self.nb_total_videos_joues)
        self.text_4.grid(row=3, column=0, sticky='w', padx=10)

        # Boutons
        self.boutons_locatisation = tk.Button(self, text="Localisation / Arrêt", command = self.allumer_led)
        self.boutons_locatisation.grid(row=4, column=0, pady=(20, 5), padx=(20, 0))
        self.boutons_locatisation.place(x=70, y=135)

        self.boutons_suivant = tk.Button(self, text="Passer au vidéo suivant")
        self.boutons_suivant.grid(row=5, column=0, pady=5, padx=(40, 0))
        self.boutons_suivant.place(x=60, y=170)

        self.boutons_arreter = tk.Button(self, text="Arrêter les vidéos", command=self.arreter_videos)
        self.boutons_arreter.grid(row=6, column=0, padx=(60, 10), pady=5)
        self.boutons_arreter.place(x=20, y=205)

        self.boutons_demarrer = tk.Button(self, text="Démarrer les vidéos", command=self.demarrer_videos)
        self.boutons_demarrer.grid(row=6, column=1, padx=(10, 60), pady=5)
        self.boutons_demarrer.place(x=140, y=205)

    def clignoter_led(self, count):
        if count <= 0:
            return
        GPIO.output(ledPin, GPIO.HIGH)  # allumer l'LED
        self.after(500, lambda: GPIO.output(ledPin, GPIO.LOW))  # éteindre l'LED après 500ms
        self.after(1000, lambda: self.clignoter_led(count - 1))  # appeler la fonction récursive pour le clignotement suivant

    def allumer_led(self):
        self.clignoter_led(3)  # clignoter l'LED trois fois


    def lister_videos(self, dossier):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        videos_dir = os.path.join(script_dir, 'videos')
        extensions = ['.mp4', '.avi']
        fichiers = [f for f in os.listdir(videos_dir) if os.path.isfile(os.path.join(videos_dir, f))]
        return [f for f in fichiers if any(f.endswith(ext) for ext in extensions)]
    
    def lister_videos(self):
        reponse = requests.get('http://localhost:5000/videos')
        if reponse.status_code == 200:
            return reponse.json()
        return []

    def obtenir_stats_jour(self):
        reponse = requests.get('http://localhost:5000/stats/jour')
        if reponse.status_code == 200:
            return reponse.json()
        return {}
        
    def demarrer_videos(self):
        if not self.videos_en_lecture:
            videos = self.lister_videos()

            if videos:
                self.videos_en_lecture = True  
                self.lecteur_video_actuel = LecteurVideo(self, videos)
                self.lecteur_video_actuel.debuter_video_playback()
            else:
                self.afficher_ecran_date_heure()


    def afficher_ecran_date_heure(self):
        self.withdraw()
        fenetre_date_heure = AffichageDateHeure(self)
        fenetre_date_heure.mainloop()
        
    def afficher_nom_video(self, nom_video):
        self.nom_video_en_cours.set("Vidéo en cours : " + nom_video)
        self.update_idletasks()

    def mise_a_jour_ui_avec_stats(self, stats, id_video_actuelle=None):
        if stats:

            stats_video_actuelle = self.trouver_stats_video(id_video_actuelle)
            if stats_video_actuelle:
                self.nb_jouer_aujourdhui.set("Nombre joué aujourd'hui : {}".format(stats_video_actuelle['nb_jouer']))
                self.temps_jouer_aujourdhui.set("Temps joué aujourd'hui : {} secondes".format(stats_video_actuelle['temps_total']))
            else:
                self.nb_jouer_aujourdhui.set("Nombre joué aujourd'hui : 0")
                self.temps_jouer_aujourdhui.set("Temps joué aujourd'hui : 0 secondes")
            
            stats_globales = stats['stats_globales']
            nb_total_videos_joues = stats_globales['nb_jouer_total']
            self.nb_total_videos_joues.set("Nombre total des vidéos jouées aujourd'hui : {}".format(nb_total_videos_joues))
                        
        else:
            self.nb_jouer_aujourdhui.set("Nombre joué aujourd'hui : 0")
            self.temps_jouer_aujourdhui.set("Temps joué aujourd'hui : 0")
            self.nb_total_videos_joues.set("Nombre total des vidéos jouées aujourd'hui : 0")
            
        self.update_idletasks()


    def arreter_videos(self):
        if self.lecteur_video_actuel:
            print("Arrêt des vidéos.")
            self.lecteur_video_actuel.arreter_lecture()  
            self.lecteur_video_actuel = None
            self.videos_en_lecture = False
            self.afficher_nom_video(" ")
            
    def trouver_stats_video(self, id_video):
        for stat in self.stats['stats_par_video']:
            if stat['id_video'] == id_video:
                return stat
        return None 