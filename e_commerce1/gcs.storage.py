# e_commerce1/gcs_storage.py
from storages.backends.gcloud import GoogleCloudStorage
from django.conf import settings


class PublicMediaStorage(GoogleCloudStorage):
    """
    Storage para GCS que:
    - usa GCS para salvar os arquivos (upload, delete, etc.)
    - gera URL pública simples, SEM signed URL (não precisa de chave privada)
    """

    def url(self, name):
        # Garante uma URL do tipo https://storage.googleapis.com/bucket/arquivo.jpg
        base_url = settings.MEDIA_URL.rstrip("/")
        return f"{base_url}/{name.lstrip('/')}"
