# e_commerce1/startup.py
import os
from django.contrib.auth import get_user_model
from django.db import OperationalError, ProgrammingError

def ensure_superuser():
    """
    Cria o superuser se DJANGO_SUPERUSER_* estiverem definidos.
    Idempotente: se já existir, não cria outro.
    """
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
    except (OperationalError, ProgrammingError):
        # DB ainda não pronto (ex.: antes de migrate) — ignora silenciosamente.
        pass
