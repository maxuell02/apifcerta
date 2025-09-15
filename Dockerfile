# Base mínima do Python
FROM python:3.11-slim

# Instala cliente Firebird (necessário para fdb)
RUN apt-get update && apt-get install -y firebird3.0-client && rm -rf /var/lib/apt/lists/*

# Define variável para localizar o fbclient
ENV LD_LIBRARY_PATH=/usr/lib/firebird:$LD_LIBRARY_PATH

# Define diretório de trabalho
WORKDIR /app

# Copia dependências e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código da API
COPY . .

# Expõe porta
EXPOSE 8000

# Comando inicial
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
