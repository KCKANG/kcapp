import mysql.connector
import sys

print("🟡 Script started", flush=True)

try:
    print("🔄 Connecting to MySQL...", flush=True)

    conn = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="123456",  # Replace with your actual password
        database="mydb"
    )

    print("✅ Connected to MySQL!", flush=True)

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")

    rows = cursor.fetchall()

    print("📋 Data from users table:", flush=True)
    for row in rows:
        print(row, flush=True)

    cursor.close()
    conn.close()

except mysql.connector.Error as err:
    print("❌ MySQL Error:", err, flush=True)

except Exception as e:
    print("❌ Other Error:", e, flush=True)

input("🔚 Press Enter to exit...")
