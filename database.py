import sqlite3

conn = sqlite3.connect("database.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS resumes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    score REAL
)
""")

conn.commit()
conn.close()

print("Database created successfully!")