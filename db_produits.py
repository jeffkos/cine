import sqlite3

conn = sqlite3.connect('cinebuzz.db')
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS produits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        categorie TEXT NOT NULL,
        description TEXT,
        prix REAL NOT NULL,
        image_url TEXT
    )
''')

# Exemples de produits
produits = [
    ("Popcorn salé", "Snack", "Popcorn croustillant salé", 3.5, "/static/img/popcorn.jpg"),
    ("Coca-Cola 50cl", "Boisson", "Soda rafraîchissant", 2.0, "/static/img/coca.jpg"),
    ("Menu duo", "Menu", "2 popcorns + 2 boissons", 8.0, "/static/img/menu.jpg")
]

c.executemany("INSERT INTO produits (nom, categorie, description, prix, image_url) VALUES (?, ?, ?, ?, ?)", produits)

conn.commit()
conn.close()

print("✅ Table 'produits' créée avec exemples.")
