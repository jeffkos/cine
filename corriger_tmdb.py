import sqlite3

conn = sqlite3.connect('cinebuzz.db')
c = conn.cursor()

# Voir les films sans TMDb ID
c.execute("SELECT id, titre FROM films WHERE tmdb_id IS NULL OR tmdb_id = ''")
films_sans_id = c.fetchall()

if films_sans_id:
    print("📋 Films sans TMDb ID :")
    for film in films_sans_id:
        print(f"ID base: {film[0]} | Titre: {film[1]}")
else:
    print("✅ Tous les films ont un tmdb_id !")

conn.close()
