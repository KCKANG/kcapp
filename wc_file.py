from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)

@app.route('/users')
def show_users():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='123456',
        database='mydb'
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('users.html', users=users)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

