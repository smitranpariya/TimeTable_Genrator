import sqlite3

# Connect to the database
conn = sqlite3.connect("timetable.db")
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", tables)

# View data in a table
cursor.execute("SELECT * FROM GeneralInfo;")
rows = cursor.fetchall()
for row in rows:
    print(row)

cursor.execute("SELECT * FROM ClassroomDetails;")
rows = cursor.fetchall()
for row in rows:
    print(row)
conn.close()