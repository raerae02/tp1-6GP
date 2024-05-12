from flask import Flask, request, jsonify
from api.sync import synchroniser_donnees

app = Flask(__name__)

# Synchroniser les données avec la base de données cloud
@app.route('/synchronize', methods=['POST'])
def synchronize():
    data = request.json
    success = synchroniser_donnees(data)
    return jsonify({"success": success}), 200 if success else 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)