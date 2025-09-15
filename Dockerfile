FROM python:3.11-slim

# Instala Firebird client (necessário para o fdb funcionar)
RUN apt-get update && apt-get install -y libfbclient2 && rm -rf /var/lib/apt/lists/*

# Configura caminho da biblioteca
ENV LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH

WORKDIR /app

# Copia dependências e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código
COPY . .

# Expõe porta da API
EXPOSE 8000

# Start do servidor
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
