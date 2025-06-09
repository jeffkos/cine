import sqlite3

def add_column(db, table, column_sql):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    try:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {column_sql}")
        print(f"✅ Colonne '{column_sql.split()[0]}' ajoutée à {table}.")
    except sqlite3.OperationalError as e:
        print(f"ℹ️ {table}: {e}")
    conn.commit()
    conn.close()

add_column('cinebuzz.db', 'films', "salle TEXT DEFAULT 'Utex'")
add_column('reservations.db', 'reservations', "salle TEXT DEFAULT 'Utex'")
