# Usar imagem base com Python
FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema (necessárias para Django e Pillow)
RUN apt-get update && apt-get install -y \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar apenas requirements.txt primeiro para usar cache do Docker
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o projeto
COPY . .

# Definir variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Expor porta
EXPOSE 8080

# Comando para rodar o Django no Cloud Run
# O collectstatic e migrate serão rodados em entrypoint (em tempo de execução)
CMD ["gunicorn", "e_commerce1.wsgi:application", "--bind", "0.0.0.0:8080"]
