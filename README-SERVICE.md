# Executando como Serviço no macOS

Esta solução permite que o Stream Deck rode como um serviço em background no macOS, executando comandos diretamente na sua máquina (não em Docker).

## Instalação do Serviço

### 1. Instalar o serviço

```bash
./install-service.sh
```

Isso irá:
- Criar o diretório de logs
- Configurar o serviço para iniciar automaticamente no login
- Iniciar o serviço imediatamente

### 2. Verificar se está rodando

```bash
launchctl list | grep streamdeck
```

Você deve ver algo como:
```
12345	0	com.cyd.streamdeck
```

## Gerenciamento do Serviço

### Iniciar o serviço

```bash
launchctl start com.cyd.streamdeck
```

### Parar o serviço

```bash
launchctl stop com.cyd.streamdeck
```

### Reiniciar o serviço

```bash
launchctl stop com.cyd.streamdeck
launchctl start com.cyd.streamdeck
```

### Ver logs

```bash
# Logs normais
tail -f logs/stream-deck.log

# Logs de erro
tail -f logs/stream-deck-error.log
```

### Ver status

```bash
launchctl list | grep streamdeck
```

## Desinstalar o Serviço

```bash
./uninstall-service.sh
```

## Executar Manualmente (sem serviço)

Se preferir executar manualmente sem instalar como serviço:

```bash
./start.sh
```

Ou usando o script antigo:

```bash
./run.sh
```

## Acessar a aplicação

Após iniciar, a aplicação estará disponível em:
- **Interface Web**: http://localhost:8000
- **API**: http://localhost:8000/api

## Vantagens desta solução

✅ **Comandos executam na sua máquina**: Todos os comandos são executados diretamente no macOS, não em um container isolado

✅ **Roda em background**: O serviço inicia automaticamente no login e continua rodando

✅ **Reinicia automaticamente**: Se o serviço cair, o macOS o reinicia automaticamente

✅ **Logs organizados**: Logs são salvos em `logs/stream-deck.log` e `logs/stream-deck-error.log`

✅ **Fácil de gerenciar**: Comandos simples para iniciar, parar e verificar status

## Solução de Problemas

### Serviço não inicia

1. Verifique os logs de erro:
   ```bash
   cat logs/stream-deck-error.log
   ```

2. Verifique se a venv está configurada corretamente:
   ```bash
   ls -la venv/
   ```

3. Tente executar manualmente para ver erros:
   ```bash
   ./start.sh
   ```

### Serviço para de funcionar

1. Verifique os logs:
   ```bash
   tail -f logs/stream-deck.log
   ```

2. Reinicie o serviço:
   ```bash
   launchctl stop com.cyd.streamdeck
   launchctl start com.cyd.streamdeck
   ```

### Porta 8000 já está em uso

Se outra aplicação estiver usando a porta 8000:

1. Encontre o processo:
   ```bash
   lsof -i :8000
   ```

2. Pare o processo ou altere a porta no `start.sh` e no `main.py`

## Notas

- O serviço usa `launchd`, o sistema de gerenciamento de serviços do macOS
- Os logs são salvos em `logs/` no diretório do projeto
- O serviço inicia automaticamente quando você faz login no macOS
- Todos os comandos são executados com as permissões do seu usuário

