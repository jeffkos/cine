# 🎬 Cinébuzz

**Cinébuzz** est une plateforme web de réservation de billets de cinéma, conçue en Python. Elle permet aux utilisateurs de consulter les films à l'affiche, réserver en ligne, voir les bandes-annonces, et découvrir les snacks disponibles dans leur salle préférée. Chaque film est proposé dans deux salles&nbsp;: **Utex** et **Shopping Mall**, avec trois séances fixes (10h, 15h et 20h).

---

## 🚀 Fonctionnalités principales

- 🎥 Liste des films à l'affiche
- 🗓️ Programmation hebdomadaire dynamique
- 📽️ Détails des films : synopsis, durée, casting, bande-annonce
- 🛒 Réservation en ligne avec ou sans paiement
- 🍿 Boutique de snacks et boissons
- 👤 Espace membre et interface d'administration

---

## 🛠️ Technologies utilisées

- **Backend** : Python + Flask
- **Frontend** : HTML, CSS (Tailwind), JavaScript
- **Base de données** : SQLite (ou MongoDB si besoin)
- **API** : TMDB (pour récupérer les informations des films)
- **Hébergement** : Render, Vercel ou Heroku

---

## 📁 Structure du projet


### Ajouter des films automatiquement

Un script utilitaire `import_tmdb_films.py` permet de peupler la base avec les films tendance du moment sur TMDb :

```bash
python import_tmdb_films.py
```

Il ajoute quelques films avec des horaires par défaut (10h, 15h et 20h).

