import tkinter as tk


class Application(tk.Tk):
    def __init__(self):
        super().__init__() 
        self.title("Contrôleur de Vidéos")  
        self.geometry("400x300")  
        self.creer_widgets()
    
    def creer_widgets(self):
        # Labele au début de l'écran
        self.etiquette = tk.Label(self, text="Contrôleur des vidéos")
        self.etiquette.grid(row=0, column=0, columnspan=3, pady=(10, 20))  

        # Lables
        self.text_1 = tk.Label(self, text="Vidéo en cours :")
        self.text_1.grid(row=1, column=0, sticky='w', padx=10)

        self.text_2 = tk.Label(self, text="Nombre joué aujourd'hui :")
        self.text_2.grid(row=2, column=0, sticky='w', padx=10)

        self.text_3 = tk.Label(self, text="Nombre total des vidéos jouées aujourd'hui :")
        self.text_3.grid(row=3, column=0, sticky='w', padx=10)

        # buttons
        self.boutons_locatisation = tk.Button(self, text="Localisation / Arrêt")
        self.boutons_locatisation.grid(row=4, column=0, columnspan=3, pady=(20, 5))

        self.boutons_suivant = tk.Button(self, text="Passer au vidéo suivant")
        self.boutons_suivant.grid(row=5, column=0, columnspan=3, pady=5)  

        self.boutons_arreter = tk.Button(self, text="Arrêter les vidéos")
        self.boutons_arreter.grid(row=6, column=0, padx=(50, 2), pady=5)  

        self.boutons_demarrer = tk.Button(self, text="Démarrer les vidéos")
        self.boutons_demarrer.grid(row=6, column=2, padx=(2, 50), pady=5) 
