import sqlite3

conn = sqlite3.connect('reservations.db')
c = conn.cursor()

# Ajouter la colonne canal
try:
    c.execute("ALTER TABLE reservations ADD COLUMN canal TEXT DEFAULT 'email'")
    print("✅ Colonne 'canal' ajoutée.")
except sqlite3.OperationalError as e:
    print(f"ℹ️ canal : {e}")

# Ajouter la colonne alerte_minutes
try:
    c.execute("ALTER TABLE reservations ADD COLUMN alerte_minutes INTEGER DEFAULT 60")
    print("✅ Colonne 'alerte_minutes' ajoutée.")
except sqlite3.OperationalError as e:
    print(f"ℹ️ alerte_minutes : {e}")

conn.commit()
conn.close()
