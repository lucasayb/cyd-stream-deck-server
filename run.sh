#!/bin/bash

# Script para iniciar o servidor Stream Deck

# Ativa a venv se existir
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Inicia o servidor
uvicorn main:app --reload --host 0.0.0.0 --port 62641
