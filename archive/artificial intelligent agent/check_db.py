import sqlite3

# Connect directly to your database file
conn = sqlite3.connect("karnataka_police_fir.db")
cursor = conn.cursor()

# Ask SQLite to reveal all hidden table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("\n" + "="*40)
print("🔍 TABLES HIDDEN INSIDE YOUR DATABASE:")
for table in tables:
    print(f" -> {table[0]}")
print("="*40 + "\n")

conn.close()