import threading
from client.controleur_video import ControleurVideos
from api.serveur import app


def run_api():
    app.run(debug=True, port=5000, use_reloader=False)

if __name__ == "__main__":
    api_thread = threading.Thread(target=run_api)
    api_thread.daemon = True  
    api_thread.start()
    
    app = ControleurVideos()
    app.mainloop()