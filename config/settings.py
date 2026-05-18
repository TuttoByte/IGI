import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = ["*",  "igi-r7qs.onrender.com"]

DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL")
    )
}

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]