import sqlite3

conn = sqlite3.connect('cinebuzz.db')
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS commentaires (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        film_id INTEGER,
        auteur TEXT,
        commentaire TEXT
    )
''')

conn.commit()
conn.close()
