import sqlite3

# Connexion à la base (elle sera créée si elle n'existe pas)
conn = sqlite3.connect('cinebuzz.db')
c = conn.cursor()

# Création de la table "films"
c.execute('''
    CREATE TABLE IF NOT EXISTS films (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titre TEXT NOT NULL,
        date TEXT NOT NULL,
        horaires TEXT NOT NULL,
        version TEXT NOT NULL,
        tmdb_id INTEGER
    )
''')

conn.commit()
conn.close()
print("Base de données initialisée ✅")
