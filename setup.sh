#!/bin/bash

# Script de setup para o Stream Deck Custom

echo "🚀 Configurando Stream Deck Custom..."

# Cria venv se não existir
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativa venv
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Instala dependências
echo "📥 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

# Cria .env se não existir
if [ ! -f ".env" ]; then
    echo "⚙️  Criando arquivo .env..."
    cp .env.example .env
    echo "✅ Arquivo .env criado. Configure as credenciais se necessário."
fi

echo ""
echo "✅ Setup concluído!"
echo ""
echo "Para iniciar o servidor, execute:"
echo "  ./run.sh"
echo ""
echo "Ou manualmente:"
echo "  source venv/bin/activate"
echo "  uvicorn main:app --reload"
echo ""

