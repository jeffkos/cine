import os
import shutil
from datetime import datetime

# Liste des bases à sauvegarder
DATABASES = ['cinebuzz.db', 'reservations.db']

# Dossier de sauvegarde
BACKUP_FOLDER = 'backups'

# Crée le dossier s’il n'existe pas
os.makedirs(BACKUP_FOLDER, exist_ok=True)

# Date actuelle (YYYYMMDD-HHMM)
date_str = datetime.now().strftime("%Y%m%d-%H%M")

# Sauvegarde de chaque fichier .db
for db_file in DATABASES:
    if os.path.exists(db_file):
        backup_name = f"{os.path.splitext(db_file)[0]}_{date_str}.db"
        backup_path = os.path.join(BACKUP_FOLDER, backup_name)
        shutil.copy2(db_file, backup_path)
        print(f"✅ Sauvegardé : {db_file} → {backup_path}")
    else:
        print(f"⚠️ Fichier introuvable : {db_file}")
