import sqlite3

conn = sqlite3.connect("reservations.db")
c = conn.cursor()

try:
    c.execute("ALTER TABLE reservations ADD COLUMN user_id INTEGER")
    print("✅ Colonne 'user_id' ajoutée à reservations.")
except sqlite3.OperationalError as e:
    print(f"ℹ️ {e}")

conn.commit()
conn.close()
