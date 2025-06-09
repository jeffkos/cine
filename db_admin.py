import sqlite3
import bcrypt

conn = sqlite3.connect('cinebuzz.db')
c = conn.cursor()

username = "superadmin"
mot_de_passe = "admin2025"
role = "superadmin"

hashed = bcrypt.hashpw(mot_de_passe.encode('utf-8'), bcrypt.gensalt())

try:
    c.execute("INSERT INTO admins (username, password_hash, role) VALUES (?, ?, ?)", (username, hashed, role))
    print("✅ Superadmin ajouté.")
except sqlite3.IntegrityError:
    print("⚠️ Ce compte existe déjà.")

conn.commit()
conn.close()
