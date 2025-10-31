# e_commerce1/startup.py
import os
from django.contrib.auth import get_user_model
from django.db import OperationalError, ProgrammingError

def ensure_superuser():
    if os.environ.get("ENABLE_STARTUP_SUPERUSER") != "1":
        return
    try:
        User = get_user_model()
        u = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        e = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        p = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        if all([u, e, p]) and not User.objects.filter(username=u).exists():
            User.objects.create_superuser(username=u, email=e, password=p)
            print(f"[startup] Superuser '{u}' criado.")
    except (OperationalError, ProgrammingError) as exc:
        print(f"[startup] skip: {exc}")
