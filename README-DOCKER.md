# Executando com Docker

## Requisitos
- Docker

## Como usar

### Construir a imagem

```bash
# Construir a imagem (inclui banco de dados e uploads atuais)
docker build -t cyd-stream-deck .
```

**Importante**: O banco de dados (`stream_deck.db`) e os uploads (`uploads/`) serão incluídos na imagem durante o build.

### Executar o container

```bash
# Executar com volume para uploads (recomendado)
docker run -d \
  --name cyd-stream-deck \
  -p 8000:8000 \
  -v $(pwd)/uploads:/app/uploads \
  --restart unless-stopped \
  cyd-stream-deck
```

### Executar sem volume (usa uploads da imagem)

```bash
docker run -d \
  --name cyd-stream-deck \
  -p 8000:8000 \
  --restart unless-stopped \
  cyd-stream-deck
```

### Comandos úteis

```bash
# Ver logs
docker logs -f cyd-stream-deck

# Parar o container
docker stop cyd-stream-deck

# Iniciar o container
docker start cyd-stream-deck

# Remover o container
docker rm cyd-stream-deck

# Reconstruir após mudanças
docker build -t cyd-stream-deck .
docker stop cyd-stream-deck && docker rm cyd-stream-deck
docker run -d --name cyd-stream-deck -p 8000:8000 -v $(pwd)/uploads:/app/uploads --restart unless-stopped cyd-stream-deck
```

## Acessar a aplicação

Após iniciar, a aplicação estará disponível em:
- **Interface Web**: http://localhost:8000
- **API**: http://localhost:8000/api

## Persistência de dados

- **Banco de dados**: Está **embutido na imagem Docker**. Qualquer mudança no banco dentro do container será perdida ao recriar o container. Para atualizar o banco na imagem, reconstrua a imagem após fazer backup do banco atualizado.
- **Uploads de imagens**: 
  - Se usar `-v $(pwd)/uploads:/app/uploads`: Os uploads são persistidos no diretório local do projeto
  - Se não usar volume: Os uploads ficam apenas no container (perdidos ao remover o container)

## Atualizando banco de dados e uploads na imagem

Se você fez mudanças e quer incluí-las na imagem:

```bash
# 1. Pare e remova o container atual
docker stop cyd-stream-deck && docker rm cyd-stream-deck

# 2. Reconstrua a imagem com os dados atualizados
docker build -t cyd-stream-deck .

# 3. Execute novamente
docker run -d --name cyd-stream-deck -p 8000:8000 -v $(pwd)/uploads:/app/uploads --restart unless-stopped cyd-stream-deck
```

## Nota sobre comandos do sistema

A aplicação executa comandos do sistema via `subprocess`. No Docker, os comandos serão executados dentro do container Linux. Se você precisar executar comandos específicos do macOS, considere usar comandos compatíveis ou ajustar conforme necessário.

