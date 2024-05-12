import tkinter as tk
from datetime import datetime

class AffichageDateHeure(tk.Tk):
    def __init__(self, controleur):
        super().__init__()
        self.controleur = controleur
        self.title("Affichage de la date et de l'heure")
        self.attributes('-fullscreen', True)  
        self.afficher_date_heure()
        self.bind("<Escape>", self.fermer_fenetre)  


    def afficher_date_heure(self):
        label_date_heure = tk.Label(self, text="", font=('Helvetica', 48))
        label_date_heure.pack(expand=True)

        def mettre_a_jour():
            maintenant = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            label_date_heure.config(text=maintenant)
            self.after(1000, mettre_a_jour)  

        mettre_a_jour()
    
    def fermer_fenetre(self, event=None):
        self.destroy() 
        self.controleur.deiconify()
