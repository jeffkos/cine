import sqlite3
import bcrypt

conn = sqlite3.connect('cinebuzz.db')
c = conn.cursor()

# Table utilisateurs
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )
''')

conn.commit()
conn.close()
print("✅ Table 'users' créée avec succès.")
