import threading
from client.controleur_video import ControleurVideos
import time
from api.serveur import app
from azure.iot.device import IoTHubDeviceClient, Message

CONNECTION_STRING = "HostName=ElieIot.azure-devices.net;DeviceId=collect_temperature;SharedAccessKey=CzAtodBM19DkBpjNFmm/1khP3HJLB0rKbAIoTI+JXwU="


def send_data_to_iot_hub(id_objet, is_display_ads):
    try:
        # Create instance of the device client using the connection string
        client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

        # Connect the client
        client.connect()

        # Create message payload
        message = Message('{{"objet":{}, "is_display_ads":"{}"}}'.format(id_objet, is_display_ads))

        # Send message
        print("Sending message: {}".format(message))
        client.send_message(message)
        print("Message sent successfully.")

        # Disconnect the client
        client.disconnect()

    except Exception as e:
        print("Error sending message:", e)


def send_data_loop():
    while True:
        
        id_objet = "<your-id-objet>"
        is_display_ads = "yes" 
        send_data_to_iot_hub(id_objet, is_display_ads)

        time.sleep(60)


def run_api():
    app.run(debug=True, port=5000, use_reloader=False)


if __name__ == "__main__":
    api_thread = threading.Thread(target=run_api)
    api_thread.daemon = True
    api_thread.start()

    time.sleep(2)

    send_thread = threading.Thread(target=send_data_loop)
    send_thread.daemon = True
    send_thread.start()

    app = ControleurVideos()
    app.mainloop()
