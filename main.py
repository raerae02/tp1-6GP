import threading
import time
from raspberrypi.controleur_video import ControleurVideos
from api.serveur import app, set_controller_instance
from api.objet import run_data_collection


def run_api():
    print("Starting Flask API server...")

    app.run(debug=True, port=5000, use_reloader=False)


if __name__ == "__main__":
    print("Initializing server...")

    api_thread = threading.Thread(target=run_api)
    api_thread.daemon = True  
    api_thread.start()
        
    print("Server started. API thread is running.")
    
    print("Initializing data collection...")
    data_collection_thread = threading.Thread(target=run_data_collection)
    data_collection_thread.daemon = True
    data_collection_thread.start()
    print("Data collection thread is running.")
    
    time.sleep(2) 

    print("starting contoleur video")
    
    controller_instance = ControleurVideos()
    set_controller_instance(controller_instance)

    controller_instance.mainloop()