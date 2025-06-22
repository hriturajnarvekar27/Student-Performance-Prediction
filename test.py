import pyodbc

conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=FRENZY\\SQLEXPRESS;" 
        "DATABASE=DYPATU_StudentDB;"
        "Trusted_Connection=yes;"
    )
try:
    conn = pyodbc.connect(conn_str)
    print("connection successful")
except Exception as e:
    print(f"error: {e}")