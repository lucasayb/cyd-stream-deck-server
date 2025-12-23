#!/bin/bash

# Script para corrigir dependências após mudança de passlib para bcrypt direto

echo "🔧 Corrigindo dependências..."

# Ativa venv
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Ambiente virtual não encontrado. Execute ./setup.sh primeiro."
    exit 1
fi

# Remove passlib se estiver instalado
echo "🗑️  Removendo passlib..."
pip uninstall -y passlib 2>/dev/null || true

# Instala bcrypt se não estiver instalado
echo "📦 Instalando bcrypt..."
pip install bcrypt

echo ""
echo "✅ Dependências corrigidas!"
echo ""
echo "Agora você pode executar: ./run.sh"

