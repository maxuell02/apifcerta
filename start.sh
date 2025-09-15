#!/bin/bash
set -e

# Instalar cliente Firebird no container
apt-get update
apt-get install -y firebird3.0-client

# Definir variável para o driver Firebird localizar a lib
export LD_LIBRARY_PATH=/usr/lib/firebird:$LD_LIBRARY_PATH

# Rodar a API FastAPI normalmente
uvicorn main:app --host 0.0.0.0 --port $PORT
