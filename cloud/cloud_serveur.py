from flask import Flask, request, jsonify
from api.sync import synchroniser_donnees
from api.database import creer_connexion_cloud
from flask_cors import CORS as cors

app = Flask(__name__)
cors(app)

@app.route('/objets/status', methods=['GET'])
def get_objets_status():
    conn_cloud = creer_connexion_cloud()
    if not conn_cloud:
        return jsonify({"success": False}), 500

    cloud_cursor = conn_cloud.cursor()
    cloud_cursor.execute("SELECT id_objet, nom_objet, local_objet, is_localisation FROM objets")
    objets = cloud_cursor.fetchall()

    cloud_cursor.close()
    conn_cloud.close()

    return jsonify({"success": True, "objets": objets}), 200

# Synchroniser les données avec la base de données cloud
@app.route('/synchronize', methods=['POST'])
def synchronize():
    data = request.json
    success = synchroniser_donnees(data)
    return jsonify({"success": success}), 200 if success else 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)