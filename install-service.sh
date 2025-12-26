#!/bin/bash

# Script para instalar o serviço Stream Deck no macOS

# Obtém o diretório absoluto do projeto
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "🚀 Instalando serviço Stream Deck..."

# Cria diretório de logs se não existir
mkdir -p "$PROJECT_DIR/logs"

# Torna os scripts executáveis
chmod +x "$PROJECT_DIR/start.sh"

# Copia o plist e substitui PROJECT_PATH pelo caminho real
sed "s|PROJECT_PATH|$PROJECT_DIR|g" "$PROJECT_DIR/com.cyd.streamdeck.plist" > "$HOME/Library/LaunchAgents/com.cyd.streamdeck.plist"

# Carrega o serviço
launchctl load "$HOME/Library/LaunchAgents/com.cyd.streamdeck.plist" 2>/dev/null || launchctl load -w "$HOME/Library/LaunchAgents/com.cyd.streamdeck.plist"

echo "✅ Serviço instalado com sucesso!"
echo ""
echo "O serviço será iniciado automaticamente no login."
echo ""
echo "Comandos úteis:"
echo "  Iniciar:   launchctl start com.cyd.streamdeck"
echo "  Parar:     launchctl stop com.cyd.streamdeck"
echo "  Status:    launchctl list | grep streamdeck"
echo "  Logs:      tail -f $PROJECT_DIR/logs/stream-deck.log"

