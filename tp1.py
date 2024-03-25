import tkinter as tk
import RPi.GPIO as GPIO
import os 
import cv2


#la fonction pour jouer la musique 
def play_video(video_path):
    cap = cv2.VideoCapture(video_path)
    
    while cap.isOpened():
        ret , frame = cap.read()
        if not ret : 
            break
            
        cv2.imshow('Video', frame)
        
        #press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
    cap.release()
    cv2.destroyAllWindows()


def get_video_paths(folder_path):
    video_paths = []
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path) and file_name.endswith('.mp4'):
            video_paths.append(file_path)
    return video_paths
    
# List of video paths
video_paths = get_video_paths("/home/e2067396/Desktop/tp/videos")

def is_folder_empty(folder_path):
    return len(os.listdir(folder_path)) == 0

folder_path = "/home/e2067396/Desktop/tp/videos"
video_path = "/home/e2067396/Desktop/tp/videos/1.mp4"



ledPin = 12       # define ledPin
sensorPin = 11    # define sensorPin

def setup():
    GPIO.setmode(GPIO.BOARD)        # use PHYSICAL GPIO Numbering
    GPIO.setup(ledPin, GPIO.OUT)    # set ledPin to OUTPUT mode
    GPIO.setup(sensorPin, GPIO.IN)  # set sensorPin to INPUT mode

def loop():
    while True:
        if GPIO.input(sensorPin)==GPIO.HIGH:
            GPIO.output(ledPin,GPIO.HIGH) # turn on led
            print ('led turned on >>>')
        else :
            GPIO.output(ledPin,GPIO.LOW) # turn off led
            print ('led turned off <<<')
            play_video(video_path)


def destroy():
    GPIO.cleanup()                     # Release GPIO resource
    
    
class Application(tk.Tk):
        def __init__(self):
            tk.Tk.__init__(self)
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
                    





def on_escape(event=None):
            app.destroy()
    
if __name__ == "__main__":

    
    #si la repertoire est vide , l'interface de l'application va apparaitre
    if is_folder_empty(folder_path):
        
        app = Application()
        app.bind("<Escape>",on_escape)
        app.attributes('-fullscreen', True)
        app.title("Controleur de videos")
        app.mainloop()
    
    #sinon , le detecteur de mouvement va s'executer
    else :
        print ('Program is starting...')
        setup()

        try:
            loop()
            

        except KeyboardInterrupt:  # Press ctrl-c to end the program.
            destroy()
        

