import requests

API_KEY = "c9c94c93f3d95e664edb61e99f4fd1b1"  # remplace par ta vraie clé

def chercher_film(nom_film):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={nom_film}&language=fr-FR"
    reponse = requests.get(url)
    donnees = reponse.json()

    if donnees['results']:
        film = donnees['results'][0]  # on prend le premier résultat
        return {
            "titre": film['title'],
            "affiche": f"https://image.tmdb.org/t/p/w500{film['poster_path']}",
            "resume": film['overview'],
            "note": film['vote_average'],
            "date_sortie": film['release_date']
        }
    else:
        return None

# Test simple :
film = chercher_film("Le Parrain")
print(film)
