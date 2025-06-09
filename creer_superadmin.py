import sqlite3
import bcrypt

# Connexion à la base cinebuzz.db
conn = sqlite3.connect('cinebuzz.db')
c = conn.cursor()

# Données du compte à créer
username = "superadmin"
mot_de_passe = "admin2025"
role = "superadmin"

# Hachage sécurisé du mot de passe
hashed = bcrypt.hashpw(mot_de_passe.encode('utf-8'), bcrypt.gensalt())

try:
    c.execute("INSERT INTO admins (username, password_hash, role) VALUES (?, ?, ?)",
              (username, hashed, role))
    conn.commit()
    print("✅ Superadmin créé avec succès.")
except sqlite3.IntegrityError:
    print("⚠️ Ce compte existe déjà.")

conn.close()
