#!/bin/bash

# Atualiza pacotes e instala cliente Firebird
apt-get update
apt-get install -y firebird3.0-client

# Define variável de ambiente para o fbclient
export LD_LIBRARY_PATH=/usr/lib/firebird:$LD_LIBRARY_PATH

# Inicia o servidor FastAPI
uvicorn main:app --host 0.0.0.0 --port $PORT
