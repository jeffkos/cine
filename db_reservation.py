import sqlite3

conn = sqlite3.connect('reservations.db')
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        email TEXT NOT NULL,
        telephone TEXT NOT NULL,
        film TEXT NOT NULL,
        date_projection TEXT NOT NULL,
        horaire TEXT NOT NULL
    )
''')

conn.commit()
conn.close()

print("✅ Base de données des réservations créée.")
