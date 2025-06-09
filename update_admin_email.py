import sqlite3

conn = sqlite3.connect("cinebuzz.db")
c = conn.cursor()

c.execute("UPDATE admins SET email = 'admin@cinebuzz.com' WHERE id = 1")
conn.commit()
conn.close()

print("✅ Email mis à jour.")
