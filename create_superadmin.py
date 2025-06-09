import sqlite3
import bcrypt

conn = sqlite3.connect("cinebuzz.db")
c = conn.cursor()

username = "admin"
email = "admin@cinebuzz.com"
mot_de_passe = "admin123"

# Hachage du mot de passe
hashed = bcrypt.hashpw(mot_de_passe.encode('utf-8'), bcrypt.gensalt())

# Supprimer un ancien si doublon
c.execute("DELETE FROM admins WHERE email = ?", (email,))

# Insérer le nouvel admin
c.execute("INSERT INTO admins (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
          (username, email, hashed, "superadmin"))

conn.commit()
conn.close()

print("✅ Admin créé : admin@cinebuzz.com / Mot de passe : admin123")
