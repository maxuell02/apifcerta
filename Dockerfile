# Base: Python 3.11 slim
FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /app

# Evita buffers de stdout
ENV PYTHONUNBUFFERED=1

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    firebird-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia código da aplicação
COPY . .

# Porta exposta
EXPOSE 8000

# Comando para rodar a API no Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
