import sqlite3
from datetime import date, timedelta
import requests

from config import TMDB_API_KEY, CINE_DB


def column_exists(conn, table, column):
    cur = conn.execute(f"PRAGMA table_info({table})")
    return column in [row[1] for row in cur.fetchall()]


def ajouter_films_depuis_tmdb(nombre=5):
    url = f"https://api.themoviedb.org/3/trending/movie/day?api_key={TMDB_API_KEY}&language=fr-FR"
    reponse = requests.get(url)
    films = reponse.json().get('results', [])[:nombre]

    with sqlite3.connect(CINE_DB) as conn:
        has_salle = column_exists(conn, 'films', 'salle')
        for i, film in enumerate(films):
            titre = film.get('title')
            tmdb_id = film.get('id')
            jour = date.today() + timedelta(days=i)
            horaires = "10h,15h,20h"
            version = "VOSTFR"
            params = (titre, jour.isoformat(), horaires, version, tmdb_id)
            if has_salle:
                conn.execute(
                    "INSERT INTO films (titre, date, horaires, version, tmdb_id, salle) VALUES (?, ?, ?, ?, ?, ?)",
                    params + ("Utex",)
                )
            else:
                conn.execute(
                    "INSERT INTO films (titre, date, horaires, version, tmdb_id) VALUES (?, ?, ?, ?, ?)",
                    params
                )
        conn.commit()
    print(f"✅ {len(films)} films ajoutés depuis TMDb")


if __name__ == '__main__':
    ajouter_films_depuis_tmdb()
