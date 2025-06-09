import sqlite3
import bcrypt

conn = sqlite3.connect("cinebuzz.db")
c = conn.cursor()

# Supprime l'ancienne table si elle existe
c.execute("DROP TABLE IF EXISTS admins")

# Crée la table propre avec toutes les colonnes nécessaires
c.execute('''
    CREATE TABLE admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'moderateur'
    )
''')

# Crée un compte admin par défaut
mot_de_passe = "admin123"
hashed = bcrypt.hashpw(mot_de_passe.encode('utf-8'), bcrypt.gensalt())
c.execute("INSERT INTO admins (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
          ("admin", "admin@cinebuzz.com", hashed, "superadmin"))

conn.commit()
conn.close()

print("✅ Table admins recréée avec succès.")
print("🧑‍💼 Admin : admin@cinebuzz.com / Mot de passe : admin123")
