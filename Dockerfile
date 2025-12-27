FROM python:3.9-slim

# Define diretório de trabalho
WORKDIR /app

# Instala dependências do sistema necessárias
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia arquivos de requisitos
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação, banco de dados e uploads
COPY . .

# Garante permissões corretas
RUN mkdir -p uploads && \
    chmod 755 uploads && \
    if [ -f stream_deck.db ]; then chmod 644 stream_deck.db; fi

# Define volume para uploads (permite montar volume do host)
VOLUME ["/app/uploads"]

# Expõe a porta da aplicação
EXPOSE 62641

# Comando para iniciar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "62641"]
