# ------------------------------
# Dockerfile para FastAPI + Firebird
# ------------------------------

# Imagem base
FROM python:3.11-slim

# Variáveis de ambiente para evitar perguntas do apt
ENV DEBIAN_FRONTEND=noninteractive

# Atualiza pacotes e instala dependências do sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        g++ \
        gcc \
        libcurl4-openssl-dev \
        unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Define diretório da aplicação
WORKDIR /app

# Copia requirements e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Expõe a porta padrão do FastAPI
EXPOSE 8000

# Comando para rodar a API com Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
