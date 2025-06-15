import os
from dotenv import load_dotenv

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(24))

CINE_DB = os.getenv("CINE_DB", "cinebuzz.db")
RESERVATIONS_DB = os.getenv("RESERVATIONS_DB", "reservations.db")

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
