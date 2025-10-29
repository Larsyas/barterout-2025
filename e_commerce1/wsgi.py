"""
WSGI config for e_commerce1 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'e_commerce1.settings')

application = get_wsgi_application()

# Chamada de startup (após a app estar pronta)
from e_commerce1.startup import ensure_superuser  # <-- importa do arquivo que criamos
ensure_superuser()