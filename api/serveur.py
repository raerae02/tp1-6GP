from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

def create_connection():
    connection = None
    try:
        print('Connecting to the MySQL database...')
        connection = mysql.connector.connect(
            host='localhost',  # Use the IP address of the Docker container
            port='3306',
            user='root',
            password='password',
            database='videos_db'
        )
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

@app.route('/videos', methods=['GET'])
def lister_videos():
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM videos ORDER BY ordre"
    cursor.execute(query)
    videos = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(videos)

@app.route('/video/current', methods=['POST'])
def marquer_video_courante():
    data = request.json
    connection = create_connection()
    cursor = connection.cursor()
    query = """
    INSERT INTO video_courant (id_video, debut_video, fin_video, temps_jouer)
    VALUES (%s, NOW(), NULL, 0)
    """
    cursor.execute(query, (data['id_video'],))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"success": True}), 201

@app.route('/video/current', methods=['PUT'])
def terminer_video_courante():
    data = request.json
    connection = create_connection()
    cursor = connection.cursor()
    query = """
    UPDATE video_courant
    SET fin_video = NOW(), temps_jouer = %s
    WHERE id_video = %s AND fin_video IS NULL
    """
    cursor.execute(query, (data['temps_jouer'], data['id_video']))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"success": True})