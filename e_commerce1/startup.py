# e_commerce1/startup.py
import os
from django.contrib.auth import get_user_model
from django.db import OperationalError, ProgrammingError

def ensure_superuser():
    # só roda quando pedirmos explicitamente
    if os.environ.get("ENABLE_STARTUP_SUPERUSER") != "1":
        return
    try:
        User = get_user_model()
        u = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        e = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        p = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        if not all([u, e, p]):
            return
        if not User.objects.filter(username=u).exists():
            User.objects.create_superuser(username=u, email=e, password=p)
            print(f"[startup] Superuser '{u}' criado.")
        else:
            print(f"[startup] Superuser '{u}' já existe.")
    except (OperationalError, ProgrammingError) as exc:
        print(f"[startup] superuser skip (db not ready / readonly): {exc}")
