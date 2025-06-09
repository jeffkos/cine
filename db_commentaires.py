import sqlite3

# Connexion à la base cinebuzz.db
conn = sqlite3.connect('cinebuzz.db')
c = conn.cursor()

# Création de la table "commentaires"
c.execute('''
    CREATE TABLE IF NOT EXISTS commentaires (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        film_id INTEGER,
        auteur TEXT NOT NULL,
        commentaire TEXT NOT NULL
    )
''')

conn.commit()
conn.close()

print("✅ Table 'commentaires' créée avec succès dans cinebuzz.db.")
