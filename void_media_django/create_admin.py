import os
import django
from django.contrib.auth import get_user_model

# Ensure this matches your project folder name exactly
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'void_media.settings')
django.setup()

User = get_user_model()
username = 'RedFox'
email = 'montherrt@gmail.com'
password = 'foxsmurf123'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"Superuser {username} created successfully!")
else:
    print(f"Superuser {username} already exists, skipping creation.")
