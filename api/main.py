from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host='localhost',
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

