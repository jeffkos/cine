import sqlite3

conn = sqlite3.connect('cinebuzz.db')
c = conn.cursor()

# Ajouter la colonne 'role' si elle n'existe pas
try:
    c.execute("ALTER TABLE admins ADD COLUMN role TEXT DEFAULT 'moderator'")
    print("✅ Colonne 'role' ajoutée avec succès.")
except sqlite3.OperationalError as e:
    print(f"ℹ️ {e} (probablement déjà ajoutée)")

conn.commit()
conn.close()
