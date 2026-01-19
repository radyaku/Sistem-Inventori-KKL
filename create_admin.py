import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "asset_management.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

USERNAME = "admin"
EMAIL = "admin@example.com"
PASSWORD = "admin123"

if not User.objects.filter(username=USERNAME).exists():
    print("Creating superuser...")
    User.objects.create_superuser(USERNAME, EMAIL, PASSWORD)
else:
    print("Superuser already exists.")
