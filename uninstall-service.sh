#!/bin/bash

# Script para desinstalar o serviço Stream Deck do macOS

echo "🛑 Desinstalando serviço Stream Deck..."

# Para o serviço se estiver rodando
launchctl stop com.cyd.streamdeck 2>/dev/null

# Remove o serviço
launchctl unload "$HOME/Library/LaunchAgents/com.cyd.streamdeck.plist" 2>/dev/null || launchctl unload -w "$HOME/Library/LaunchAgents/com.cyd.streamdeck.plist" 2>/dev/null

# Remove o arquivo plist
rm -f "$HOME/Library/LaunchAgents/com.cyd.streamdeck.plist"

echo "✅ Serviço desinstalado com sucesso!"

