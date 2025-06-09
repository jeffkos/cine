from flask import Flask, render_template, request
import sqlite3
import requests
from datetime import date
from flask import redirect, url_for
from datetime import timedelta
from flask import jsonify
import csv
from flask import make_response
import io
from flask import Flask, render_template, request, redirect, url_for, session
import os
import bcrypt
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
load_dotenv()
import os
API_KEY = os.getenv("TMDB_API_KEY")




app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2 Mo


def chercher_film(nom_film):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={nom_film}&language=fr-FR"
    reponse = requests.get(url)
    donnees = reponse.json()

    if donnees['results']:
        film = donnees['results'][0]
        return {
            "titre": film['title'],
            "affiche": f"https://image.tmdb.org/t/p/w500{film['poster_path']}" if film['poster_path'] else None,
            "resume": film['overview'],
            "note": film['vote_average'],
            "date_sortie": film['release_date']
        }
    else:
        return None
    

from datetime import date

def films_du_jour():
    conn = sqlite3.connect('cinebuzz.db')
    c = conn.cursor()
    c.execute("SELECT titre, horaires, version, tmdb_id, salle FROM films WHERE date = ?", (date.today().isoformat(),))
    resultats = c.fetchall()
    conn.close()

    # Enrichir avec l’API TMDb
    films = []
    for titre, horaires, version, tmdb_id, salle in resultats:
        url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={API_KEY}&language=fr-FR"
        reponse = requests.get(url).json()
        films.append({
            "titre": titre,
            "horaires": horaires,
            "version": version,
            "salle": salle,
            "affiche": f"https://image.tmdb.org/t/p/w780{reponse['backdrop_path']}" if reponse.get('backdrop_path') else None
        })
    return films


# 🔧 Config upload
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def accueil():
    films = films_du_jour()
    return render_template('index.html', films=films)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    message = ""
    if request.method == 'POST':
        titre = request.form['titre']
        date_proj = request.form['date']
        horaires = request.form['horaires']
        version = request.form['version']
        salle = request.form['salle']
        tmdb_id = request.form['tmdb_id']

        # Sauvegarde dans la base
        conn = sqlite3.connect('cinebuzz.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO films (titre, date, horaires, version, salle, tmdb_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (titre, date_proj, horaires, version, salle, tmdb_id))
        conn.commit()
        conn.close()

        message = f"✅ Film '{titre}' ajouté avec succès pour le {date_proj}."

    return render_template('admin.html', message=message)

from datetime import timedelta

@app.route('/programme')
def programme():
    today = date.today()
    semaine = [today + timedelta(days=i) for i in range(7)]

    conn = sqlite3.connect('cinebuzz.db')
    c = conn.cursor()
    c.execute("SELECT titre, date, horaires, version, tmdb_id, salle FROM films ORDER BY date ASC")
    resultats = c.fetchall()
    conn.close()

    # Organisation des films par jour
    jours_films = {}
    for jour in semaine:
        jour_str = jour.isoformat()
        films_du_jour = [film for film in resultats if film[1] == jour_str]
        liste_films = []

        for titre, date_proj, horaires, version, tmdb_id, salle in films_du_jour:
            url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={API_KEY}&language=fr-FR"
            reponse = requests.get(url).json()
            affiche = f"https://image.tmdb.org/t/p/w300{reponse['poster_path']}" if reponse.get('poster_path') else None

            # ✅ On ajoute le tmdb_id ici pour faire le lien vers la page de détail
            liste_films.append({
                "titre": titre,
                "horaires": horaires,
                "version": version,
                "salle": salle,
                "affiche": affiche,
                "tmdb_id": tmdb_id  # ← Important
            })

        jours_films[jour.strftime("%A %d %B")] = liste_films

    return render_template('programme.html', programme=jours_films)



from flask import jsonify

@app.route('/tmdb_search')
def tmdb_search():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "missing query"}), 400

    url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={query}&language=fr-FR"
    response = requests.get(url).json()

    if response['results']:
        tmdb_id = response['results'][0]['id']
        return jsonify({"tmdb_id": tmdb_id})
    else:
        return jsonify({"tmdb_id": None})


@app.route('/film/<int:tmdb_id>', methods=['GET', 'POST'])
def detail_film(tmdb_id):
    # 🔗 Récupérer les infos détaillées du film via TMDb
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={API_KEY}&language=fr-FR&append_to_response=videos,credits"
    reponse = requests.get(url).json()

    # 🧾 Infos film
    film = {
        "titre": reponse.get("title"),
        "affiche": f"https://image.tmdb.org/t/p/w780{reponse['backdrop_path']}" if reponse.get("backdrop_path") else None,
        "resume": reponse.get("overview"),
        "note": reponse.get("vote_average"),
        "annee": reponse.get("release_date", "")[:4],
        "duree": f"{reponse.get('runtime')} minutes",
        "bande_annonce": None,
        "acteurs": [cast["name"] for cast in reponse.get("credits", {}).get("cast", [])[:5]]
    }

    # 🎬 Chercher la première bande-annonce YouTube
    videos = reponse.get("videos", {}).get("results", [])
    for v in videos:
        if v["type"] == "Trailer" and v["site"] == "YouTube":
            film["bande_annonce"] = f"https://www.youtube.com/watch?v={v['key']}"
            break

    # 📅 Récupérer les projections programmées
    conn = sqlite3.connect('cinebuzz.db')
    c = conn.cursor()
    c.execute("SELECT date, horaires, salle FROM films WHERE tmdb_id = ? ORDER BY date ASC", (tmdb_id,))
    projections = c.fetchall()

    # 💬 Récupérer les commentaires
    c.execute("SELECT auteur, commentaire FROM commentaires WHERE film_id = ?", (tmdb_id,))
    commentaires = c.fetchall()

    # 💬 Traitement d'un commentaire utilisateur connecté
    message = ""
    if request.method == 'POST':
        if session.get('admin') or session.get('user'):
            auteur = session.get('username', 'Utilisateur')
            commentaire = request.form['commentaire']

            c.execute("INSERT INTO commentaires (film_id, auteur, commentaire) VALUES (?, ?, ?)",
                    (tmdb_id, auteur, commentaire))
            conn.commit()
            message = "✅ Votre commentaire a été publié."
            commentaires.append((auteur, commentaire))
    else:
        message = "❌ Vous devez être connecté pour publier un commentaire."

    conn.close()

    return render_template("detail.html",
                           film=film,
                           tmdb_id=tmdb_id,
                           commentaires=commentaires,
                           message=message,
                           projections=projections)





@app.route('/reserver/<int:tmdb_id>', methods=['GET', 'POST'])
def reserver(tmdb_id):
    # Récupérer les infos TMDb du film
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={API_KEY}&language=fr-FR"
    reponse = requests.get(url).json()
    titre_film = reponse.get("title")

    # Récupérer les projections du film dans cinebuzz.db
    conn = sqlite3.connect('cinebuzz.db')
    c = conn.cursor()
    c.execute("SELECT date, horaires, salle FROM films WHERE tmdb_id = ?", (tmdb_id,))
    projections = c.fetchall()
    conn.close()

    message = ""

    if request.method == 'POST':
        nom = request.form['nom']
        email = request.form['email']
        telephone = request.form['telephone']
        date_projection = request.form['date_projection']
        salle_res = request.form['salle']
        horaire = request.form['horaire']
        alerte_minutes = int(request.form.get('alerte_minutes', 60))
        canal = request.form.get('canal', 'email')

        # Récupérer l'user_id s'il est connecté
        user_id = session.get('user_id') if session.get('user') else None

        # Enregistrer la réservation dans reservations.db
        conn = sqlite3.connect('reservations.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO reservations (
                nom, email, telephone, film, date_projection, salle, horaire,
                alerte_minutes, canal, user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            nom, email, telephone, titre_film, date_projection,
            salle_res, horaire, alerte_minutes, canal, user_id
        ))
        conn.commit()
        conn.close()

        message = "✅ Réservation enregistrée avec succès."

    return render_template('reserver.html',
                           film=titre_film,
                           tmdb_id=tmdb_id,
                           projections=projections,
                           message=message)




@app.route('/admin/reservations', methods=['GET'])
def admin_reservations():
    # 🔐 Vérification si l'utilisateur est connecté
    if not session.get('admin'):
        return redirect(url_for('login'))

    film_filter = request.args.get('film')
    date_filter = request.args.get('date')

    conn = sqlite3.connect('reservations.db')
    c = conn.cursor()

    # Requête dynamique avec filtres
    base_query = "SELECT nom, email, telephone, film, date_projection, salle, horaire FROM reservations"
    filters = []
    params = []

    if film_filter:
        filters.append("film LIKE ?")
        params.append(f"%{film_filter}%")
    if date_filter:
        filters.append("date_projection = ?")
        params.append(date_filter)

    if filters:
        base_query += " WHERE " + " AND ".join(filters)

    base_query += " ORDER BY date_projection ASC"
    c.execute(base_query, params)
    data = c.fetchall()

    # Statistiques par film
    c.execute("SELECT film, COUNT(*) FROM reservations GROUP BY film ORDER BY COUNT(*) DESC")
    stats = c.fetchall()

    conn.close()
    return render_template('admin_reservations.html', reservations=data, stats=stats, film_filter=film_filter, date_filter=date_filter)




@app.route('/export/csv')
def export_csv():
    if not session.get('admin'):
        return redirect(url_for('login'))

    conn = sqlite3.connect('reservations.db')
    c = conn.cursor()
    c.execute("SELECT nom, email, telephone, film, date_projection, salle, horaire FROM reservations ORDER BY date_projection ASC")
    data = c.fetchall()
    conn.close()

    # 🧠 Fichier CSV en mémoire
    output = io.StringIO()
    writer = csv.writer(output)

    # Écriture des en-têtes
    writer.writerow(["Nom", "Email", "Téléphone", "Film", "Date", "Salle", "Horaire"])

    # Écriture des lignes
    for row in data:
        writer.writerow(row)

    # Création de la réponse HTTP avec CSV
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=reservations_cinebuzz.csv"
    response.headers["Content-Type"] = "text/csv"
    return response

@app.route('/login', methods=['GET', 'POST'])
def login():
    erreur = ""

    if request.method == 'POST':
        identifiant = request.form['identifiant']  # Peut être email ou username
        password = request.form['password']

        conn = sqlite3.connect('cinebuzz.db')
        c = conn.cursor()

        # 🔍 Cherche l'admin par email ou nom d'utilisateur
        c.execute("""
            SELECT id, username, email, password_hash, role 
            FROM admins 
            WHERE email = ? OR username = ?
        """, (identifiant, identifiant))
        admin = c.fetchone()

        if admin:
            password_hash = admin[3]
            if isinstance(password_hash, str):
                password_hash = password_hash.encode('utf-8')
            if bcrypt.checkpw(password.encode('utf-8'), password_hash):
                session['admin'] = True
                session['admin_id'] = admin[0]
                session['username'] = admin[1]
                session['role'] = admin[4]

                conn.close()
                return redirect(url_for('admin_dashboard') if admin[4] == 'superadmin' else url_for('admin_reservations'))

        # 🔍 Sinon cherche l'utilisateur simple
        c.execute("""
            SELECT id, username, email, password_hash 
            FROM users 
            WHERE email = ? OR username = ?
        """, (identifiant, identifiant))
        user = c.fetchone()
        conn.close()

        if user:
            password_hash = user[3]
            if isinstance(password_hash, str):
                password_hash = password_hash.encode('utf-8')
            if bcrypt.checkpw(password.encode('utf-8'), password_hash):
                session['user'] = True
                session['user_id'] = user[0]
                session['username'] = user[1]
                return redirect(url_for('accueil'))

        erreur = "❌ Identifiants incorrects."

    return render_template("login.html", erreur=erreur)




@app.route('/logout')
def logout():
    session.pop('admin', None)
    session.pop('role', None)
    session.pop('user', None)
    session.pop('user_id', None)
    session.pop('username', None)
    session.clear()
    return redirect(url_for('accueil'))


@app.route('/admin/nouveau', methods=['GET', 'POST'])
def nouveau_admin():
    if not session.get('admin'):
        return redirect(url_for('login'))

    message = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        conn = sqlite3.connect('cinebuzz.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO admins (username, password_hash) VALUES (?, ?)", (username, hashed))
            conn.commit()
            message = f"✅ Admin '{username}' créé avec succès."
        except sqlite3.IntegrityError:
            message = "⚠️ Cet identifiant existe déjà."
        conn.close()

    return render_template('nouveau_admin.html', message=message)

@app.route('/admin/modifier-mdp', methods=['GET', 'POST'])
def modifier_mdp():
    if not session.get('admin'):
        return redirect(url_for('login'))

    message = ""
    if request.method == 'POST':
        username = request.form['username']
        new_password = request.form['new_password']

        hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

        conn = sqlite3.connect('cinebuzz.db')
        c = conn.cursor()
        c.execute("SELECT id FROM admins WHERE username = ?", (username,))
        row = c.fetchone()
        if row:
            c.execute("UPDATE admins SET password_hash = ? WHERE username = ?", (hashed, username))
            conn.commit()
            message = "✅ Mot de passe modifié avec succès."
        else:
            message = "⚠️ Utilisateur introuvable."
        conn.close()

    return render_template('modifier_mdp.html', message=message)


@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('login'))

    conn1 = sqlite3.connect('cinebuzz.db')
    c1 = conn1.cursor()
    c1.execute("SELECT COUNT(*) FROM films")
    total_films = c1.fetchone()[0]

    c1.execute("SELECT COUNT(*) FROM produits")
    total_produits = c1.fetchone()[0]

    c1.execute("SELECT COUNT(*) FROM users")
    total_utilisateurs = c1.fetchone()[0]
    conn1.close()

    conn2 = sqlite3.connect('reservations.db')
    c2 = conn2.cursor()
    c2.execute("SELECT COUNT(*) FROM reservations")
    total_reservations = c2.fetchone()[0]
    conn2.close()

    return render_template(
        "admin_dashboard.html",
        username=session.get('username'),
        total_films=total_films,
        total_produits=total_produits,
        total_reservations=total_reservations,
        total_utilisateurs=total_utilisateurs
    )


@app.route('/admin/gestion-admins', methods=['GET', 'POST'])
def gestion_admins():
    if not session.get('admin') or session.get('role') != 'superadmin':
        return redirect(url_for('login'))

    conn = sqlite3.connect('cinebuzz.db')
    c = conn.cursor()

    if request.method == 'POST':
        username = request.form['username']
        nouveau_role = request.form['role']
        c.execute("UPDATE admins SET role = ? WHERE username = ?", (nouveau_role, username))
        conn.commit()

    c.execute("SELECT username, role FROM admins")
    admins = c.fetchall()
    conn.close()

    return render_template('gestion_admins.html', admins=admins)


@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        conn = sqlite3.connect('cinebuzz.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                      (username, email, hashed))
            conn.commit()
            message = "✅ Compte créé. Vous pouvez maintenant vous connecter."
        except sqlite3.IntegrityError:
            message = "❌ Cet utilisateur ou email existe déjà."
        conn.close()

    return render_template('register.html', message=message)
@app.route('/mon-compte')
def mon_compte():
    if not session.get('user'):
        return redirect(url_for("login"))

    user_id = session.get('user_id')

    conn = sqlite3.connect('reservations.db')
    c = conn.cursor()
    c.execute('''
        SELECT film, date_projection, horaire, canal, alerte_minutes
        FROM reservations
        WHERE user_id = ?
        ORDER BY date_projection DESC
    ''', (user_id,))
    reservations = c.fetchall()
    conn.close()

    return render_template('mon_compte.html', reservations=reservations)


@app.route('/produits')
def produits():
    conn = sqlite3.connect('cinebuzz.db')
    c = conn.cursor()
    c.execute("SELECT nom, categorie, description, prix, image_url FROM produits ORDER BY categorie ASC, nom ASC")
    produits = c.fetchall()
    conn.close()
    return render_template("produits.html", produits=produits)
    

@app.route('/admin/produits', methods=['GET', 'POST'])
def admin_produits():
    if not session.get('admin'):
        return redirect(url_for('login'))

    conn = sqlite3.connect('cinebuzz.db')
    c = conn.cursor()

    # 🟩 Traitement ajout ou modification
    if request.method == 'POST':
        nom = request.form['nom']
        categorie = request.form['categorie']
        description = request.form['description']
        prix = float(request.form['prix'])

        image_url = request.form.get('image_url') or ""
        file = request.files.get('image_file')

        # 📸 Upload fichier si présent
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_url = f"/static/uploads/{filename}"

        if request.form.get('edit_id'):
            # ✏️ Modification produit
            edit_id = int(request.form['edit_id'])
            c.execute('''
                UPDATE produits
                SET nom = ?, categorie = ?, description = ?, prix = ?, image_url = ?
                WHERE id = ?
            ''', (nom, categorie, description, prix, image_url, edit_id))
        else:
            # ➕ Ajout nouveau produit
            c.execute('''
                INSERT INTO produits (nom, categorie, description, prix, image_url)
                VALUES (?, ?, ?, ?, ?)
            ''', (nom, categorie, description, prix, image_url))
        conn.commit()

    # 📊 Récupérer tous les produits
    c.execute("SELECT id, nom, categorie, description, prix, image_url FROM produits ORDER BY categorie, nom")
    produits = c.fetchall()
    conn.close()

    return render_template("admin_produits.html", produits=produits)


@app.route('/admin/produits/supprimer/<int:id>', methods=['POST'])
def supprimer_produit(id):
    if not session.get('admin'):
        return redirect(url_for('login'))

    conn = sqlite3.connect('cinebuzz.db')
    c = conn.cursor()
    c.execute("DELETE FROM produits WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_produits'))


@app.route('/admin/ajouter-film', methods=['GET', 'POST'])
def ajouter_film_manuellement():
    if not session.get('admin'):
        return redirect(url_for('login'))

    results = []
    message = ""

    if request.method == 'POST':
        tmdb_id = request.form['tmdb_id']
        date = request.form['date']
        horaire = request.form['horaire']
        version = request.form['version']
        salle = request.form['salle']

        conn = sqlite3.connect('cinebuzz.db')
        c = conn.cursor()
        titre = request.form['titre']
        c.execute("INSERT INTO films (tmdb_id, titre, date, horaires, version, salle) VALUES (?, ?, ?, ?, ?, ?)",
            (tmdb_id, titre, date, horaire, version, salle))

        conn.commit()
        conn.close()
        message = "✅ Film ajouté au programme."

    elif request.args.get("query"):
        query = request.args.get("query")
        url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&language=fr-FR&query={query}"
        response = requests.get(url).json()
        results = response.get("results", [])

    return render_template("ajouter_film.html", results=results, message=message)

@app.route('/')
def page_accueil():
    conn = sqlite3.connect('cinebuzz.db')
    c = conn.cursor()

    c.execute("SELECT * FROM films WHERE date = ?", (date.today().isoformat(),))
    films_du_jour = [dict(zip([col[0] for col in c.description], row)) for row in c.fetchall()]

    c.execute("SELECT * FROM films WHERE date >= ?", (date.today().isoformat(),))
    films_semaine = [dict(zip([col[0] for col in c.description], row)) for row in c.fetchall()]

    c.execute("SELECT * FROM produits")
    produits = [dict(zip([col[0] for col in c.description], row)) for row in c.fetchall()]

    conn.close()

    return render_template("accueil.html", films_du_jour=films_du_jour, films_semaine=films_semaine, produits=produits)




if __name__ == '__main__':
    app.run(debug=True)



import sqlite3
from datetime import date

def films_du_jour(jour=None):
    if not jour:
        jour = date.today().isoformat()

    conn = sqlite3.connect('cinebuzz.db')
    c = conn.cursor()
    c.execute("SELECT * FROM films WHERE date = ?", (jour,))
    films = c.fetchall()
    conn.close()
    return films

import sqlite3
from datetime import date

def films_du_jour():
    conn = sqlite3.connect('cinebuzz.db')
    c = conn.cursor()
    c.execute("SELECT titre, horaires, version, tmdb_id, salle FROM films WHERE date = ?", (date.today().isoformat(),))
    resultats = c.fetchall()
    conn.close()

    # Enrichir avec TMDb
    films = []
    for titre, horaires, version, tmdb_id, salle in resultats:
        url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={API_KEY}&language=fr-FR"
        reponse = requests.get(url).json()
        films.append({
            "titre": titre,
            "horaires": horaires,
            "version": version,
            "salle": salle,
            "affiche": f"https://image.tmdb.org/t/p/w780{reponse['backdrop_path']}" if reponse.get('backdrop_path') else None
        })
    return films
