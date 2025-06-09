import sqlite3

conn = sqlite3.connect("cinebuzz.db")
c = conn.cursor()

try:
    c.execute("ALTER TABLE admins ADD COLUMN email TEXT UNIQUE")
    print("✅ Colonne 'email' ajoutée à la table admins.")
except sqlite3.OperationalError as e:
    print(f"ℹ️ {e}")

conn.commit()
conn.close()
