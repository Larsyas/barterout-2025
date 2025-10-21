# Usar imagem base com Python
FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema (necessárias para Django e Pillow)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos do projeto
COPY . /app

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Coletar arquivos estáticos
RUN python manage.py collectstatic --noinput

# Definir variáveis de ambiente padrão
ENV PYTHONUNBUFFERED=1

# Expor porta
EXPOSE 8080

# Comando de execução (gunicorn é recomendado no Cloud Run)
CMD ["gunicorn", "e_commerce1.wsgi:application", "--bind", "0.0.0.0:8080"]
