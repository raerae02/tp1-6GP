import threading
from client.controleur_video import ControleurVideos
import time
from api.serveur import app


def run_api():
    app.run(debug=True, port=5000, use_reloader=False)

if __name__ == "__main__":
    api_thread = threading.Thread(target=run_api)
    api_thread.daemon = True  
    api_thread.start()
        
    time.sleep(2) 
    
    app = ControleurVideos()
    app.mainloop()  