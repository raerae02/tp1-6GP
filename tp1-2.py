import tkinter as tk
import RPi.GPIO as GPIO
import os
import cv2


folder_path = "/home/e2067396/Desktop/tp/videos"
videos = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.mp4')]
current_video_index = 0

ledPin = 12       # define ledPin
sensorPin = 11    # define sensorPin

def play_video(video_path):
    cap = cv2.VideoCapture(video_path)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow('Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(ledPin, GPIO.OUT)
    GPIO.setup(sensorPin, GPIO.IN)

def loop():
    global current_video_index
    while True:
        if GPIO.input(sensorPin) == GPIO.HIGH:
            GPIO.output(ledPin, GPIO.HIGH)  # Motion detected
            print('Motion detected. Playing video:', videos[current_video_index])
            play_video(videos[current_video_index])
            current_video_index = (current_video_index + 1) % len(videos)  # Move to the next video
        else:
            GPIO.output(ledPin, GPIO.LOW)

def destroy():
    GPIO.cleanup()

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
                    
if __name__ == "__main__":
    print('Program is starting...')
    setup()
    try:
        if not videos:  # If the videos list is empty, show the application window
            app = Application()
            app.bind("<Escape>", on_escape)
            app.attributes('-fullscreen', True)
            app.title("Video Controller")
            app.mainloop()
        else:  # If there are videos, start the motion detection loop
            loop()
    except KeyboardInterrupt:
        destroy()
