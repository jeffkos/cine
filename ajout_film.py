import sqlite3
from datetime import date

def ajouter_film(titre, date_proj, horaires, version, tmdb_id):
    conn = sqlite3.connect('cinebuzz.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO films (titre, date, horaires, version, tmdb_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (titre, date_proj, horaires, version, tmdb_id))
    conn.commit()
    conn.close()
    print(f"✅ Film '{titre}' ajouté pour le {date_proj}")

# Test : on ajoute un film pour aujourd'hui
ajouter_film("Inception", date.today().isoformat(), "14h,17h,20h", "VOSTFR", 27205)
