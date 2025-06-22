import pyodbc
import bcrypt

# Database connection
def get_db_connection():
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=FRENZY\\SQLEXPRESS;"
        "DATABASE=DYPATU_StudentDB;"
        "Trusted_Connection=yes;"
    )
    return pyodbc.connect(conn_str)

# Connect to the database
conn = get_db_connection()
cursor = conn.cursor()

# Fetch all users
cursor.execute("SELECT user_id, username FROM Users")
users = cursor.fetchall()

# Re-hash a default password for each user (e.g., reset to a known password)
default_password = "Test@123".encode('utf-8')
hashed_password = bcrypt.hashpw(default_password, bcrypt.gensalt())

# Update each user's password
for user in users:
    user_id = user[0]
    cursor.execute(
        "UPDATE Users SET password = ? WHERE user_id = ?",
        (hashed_password, user_id)
    )

conn.commit()
conn.close()
print("User passwords updated successfully!")