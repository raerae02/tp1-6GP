import tkinter as tk


class Application(tk.Tk):
        def __init__(self):
            super().__init__() 
            self.title("Contrôleur de Vidéos")  
            self.geometry("400x300")  
            self.creer_widgets()
            
        
        def creer_widgets(self):
            # Label au debut de lecran
            self.etiquette = tk.Label(self, text="Contrôleur des vidéos")
            self.etiquette.grid(row=0, column=0, columnspan=2, pady=(10, 20))

            # Labels
            self.text_1 = tk.Label(self, text="Vidéo en cours :")
            self.text_1.grid(row=1, column=0, sticky='w', padx=10)

            self.text_2 = tk.Label(self, text="Nombre joué aujourd'hui :")
            self.text_2.grid(row=2, column=0, sticky='w', padx=10)

            self.text_3 = tk.Label(self, text="Nombre total des vidéos jouées aujourd'hui :")
            self.text_3.grid(row=3, column=0, sticky='w', padx=10)

            # Buttons
            self.boutons_locatisation = tk.Button(self, text="Localisation / Arrêt")
            self.boutons_locatisation.grid(row=4, column=0, pady=(20, 5), padx=10)

            self.boutons_suivant = tk.Button(self, text="Passer au vidéo suivant")
            self.boutons_suivant.grid(row=5, column=0, pady=5, padx=10)

            self.boutons_arreter = tk.Button(self, text="Arrêter les vidéos")
            self.boutons_arreter.grid(row=6, column=0, pady=5, padx=10)

            self.boutons_demarrer = tk.Button(self, text="Démarrer les vidéos")
            self.boutons_demarrer.grid(row=7, column=0, pady=5, padx=10)


            #boutons pour la locatisation et arreter
            self.boutons_locatisation = tk.Button(self,text="Localisation/ Arret")
            self.boutons_locatisation.place(relx= 0.1 , rely = 0.2, anchor = 'center')
            # boutons_locatisation.pack()

            #boutons pour jouer la prochaine video
            self.boutons_suivant = tk.Button(self,text="Passer au video suivant")
            self.boutons_suivant.place(relx= 0.1 , rely = 0.25, anchor = 'center')
            # boutons_suivant.pack()

             
            #boutons pour arreter les videos
            self.boutons_arreter = tk.Button(self,text="Arreter les videos")
            self.boutons_arreter.place(relx= 0.065 , rely = 0.3, anchor = 'center')
            # boutons_arreter.pack()

            #boutons pour Demarrer les videos
            self.boutons_demarrer = tk.Button(self,text="Demarrer les videos")
            self.boutons_demarrer.place(relx= 0.15 , rely = 0.3, anchor = 'center')
                    

