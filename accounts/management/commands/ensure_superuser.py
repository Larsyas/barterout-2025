# accounts/management/commands/ensure_superuser.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Cria/atualiza um superusuário para o modelo Account custom."

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True)
        parser.add_argument("--password", required=True)
        parser.add_argument("--first-name", default="Admin")
        parser.add_argument("--last-name", default="User")
        parser.add_argument("--username", default="admin")
        parser.add_argument("--phone-number", default="00000000000")
        parser.add_argument("--document", default="DOC-SUPERUSER")
        parser.add_argument("--address", default="--")

    def handle(self, *args, **o):
        U = get_user_model()

        # defaults exigidos pelo seu MyAccountManager.create_user(...)
        defaults = dict(
            first_name=o["first_name"],
            last_name=o["last_name"],
            username=o["username"],
            phone_number=o["phone_number"],
            document=o["document"],
            address=o["address"],
            TCM_wallet=0,
        )

        # cria se não existir; se existir, atualiza campos obrigatórios vazios
        obj, _ = U.objects.get_or_create(email=o["email"], defaults=defaults)

        for k, v in defaults.items():
            if hasattr(obj, k) and (getattr(obj, k, None) in (None, "")):
                setattr(obj, k, v)

        # flags de admin
        obj.is_active = True
        obj.is_staff = True
        obj.is_superuser = True
        obj.is_admin = True
        obj.is_superadmin = True

        obj.set_password(o["password"])
        obj.save()

        self.stdout.write(self.style.SUCCESS(f"Superuser pronto (id={obj.pk}, email={obj.email})."))
