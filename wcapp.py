from flask import Flask, jsonify
import mysql.connector

app = Flask(__name__)

# Database connection setup
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",  # use your password
        database="mydb"
    )

# Route to show all users
@app.route('/users')
def show_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # Convert rows to list of dictionaries
    users = [{"id": row[0], "name": row[1], "email": row[2]} for row in rows]
    return jsonify(users)

# Run the web app
if __name__ == '__main__':
    app.run(debug=True)
