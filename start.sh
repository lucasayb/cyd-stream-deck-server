#!/bin/bash

# Script para iniciar o servidor Stream Deck
# Este script deve ser executado a partir do diretório do projeto

# Obtém o diretório absoluto do script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Ativa a venv se existir
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Inicia o servidor
uvicorn main:app --host 0.0.0.0 --port 8000

