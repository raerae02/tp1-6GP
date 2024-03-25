import tkinter as tk


class Application(tk.Tk):
        def __init__(self):
            super().__init__() 
            self.title("Contrôleur de Vidéos")  
            self.geometry("400x300")  
            self.creer_widgets()
            
        
        def creer_widgets(self):
            self.etiquette = tk.Label(self,text="controleur de videos")
            self.espace = tk.Label(self,text=" ")
            self.etiquette.pack()
            self.espace.pack()
            
            self.text_1 = tk.Label (self, text="Video en cours: ")
            self.text_1.place(relx= 0.01 , rely = 0.05, anchor = 'nw')
            self.text_1.pack(anchor = 'nw')

            self.text_2 = tk.Label (self, text="Nombre joue aujourd'hui: ")
            self.text_2.place(relx= 0.01 , rely = 0.075, anchor = 'nw')
            self.text_2.pack(anchor = 'nw')


            self.text_3 = tk.Label (self, text="Nombre total des videos joues aujourd'hui: ")
            self.text_3.place(relx= 0.01 , rely = 0.1, anchor = 'nw')
            self.text_3.pack(anchor = 'nw')
            
            self.espace = tk.Label()
            self.espace.pack()
            

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
                    

