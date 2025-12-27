# Stream Deck Custom - API e Interface Web

Sistema completo para gerenciar um Stream Deck customizado com 6 botões, permitindo configurar ícones, cores e comandos através de uma interface web protegida por autenticação.

## Características

- ✅ 6 botões configuráveis
- ✅ Banco de dados SQLite
- ✅ Interface web discreta com lista (Tailwind CSS)
- ✅ Upload de imagens para ícones
- ✅ Conversão de JPG/PNG para BMP de 8 bits
- ✅ Opção de conversão otimizada no frontend
- ✅ Autenticação por usuário e senha
- ✅ Sistema de proteção contra comandos perigosos
- ✅ API REST completa

## Instalação

1. Crie e ative um ambiente virtual:

```bash
python3 -m venv venv
source venv/bin/activate  # No Mac/Linux
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente (opcional):

```bash
cp .env.example .env
# Edite o .env com suas configurações
```

## Modos de Execução

### 1. Execução Manual (Padrão)

#### Uso

1. Inicie o servidor:

```bash
python main.py
```

Ou usando uvicorn diretamente:

```bash
uvicorn main:app --reload
```

2. Acesse a interface web:

```
http://localhost:62641
```

3. Faça login com as credenciais padrão:
   - Usuário: `admin`
   - Senha: `admin123`

### 2. Execução como Serviço no macOS

Esta solução permite que o Stream Deck rode como um serviço em background no macOS, executando comandos diretamente na sua máquina (não em Docker).

#### Instalação do Serviço

##### 1. Instalar o serviço

```bash
./install-service.sh
```

Isso irá:
- Criar o diretório de logs
- Configurar o serviço para iniciar automaticamente no login
- Iniciar o serviço imediatamente

##### 2. Verificar se está rodando

```bash
launchctl list | grep streamdeck
```

Você deve ver algo como:
```
12345	0	com.cyd.streamdeck
```

#### Gerenciamento do Serviço

##### Iniciar o serviço

```bash
launchctl start com.cyd.streamdeck
```

##### Parar o serviço

```bash
launchctl stop com.cyd.streamdeck
```

##### Reiniciar o serviço

```bash
launchctl stop com.cyd.streamdeck
launchctl start com.cyd.streamdeck
```

##### Ver logs

```bash
# Logs normais
tail -f logs/stream-deck.log

# Logs de erro
tail -f logs/stream-deck-error.log
```

##### Ver status

```bash
launchctl list | grep streamdeck
```

#### Desinstalar o Serviço

```bash
./uninstall-service.sh
```

#### Executar Manualmente (sem serviço)

Se preferir executar manualmente sem instalar como serviço:

```bash
./start.sh
```

Ou usando o script antigo:

```bash
./run.sh
```

#### Acessar a aplicação (Serviço)

Após iniciar, a aplicação estará disponível em:
- **Interface Web**: http://localhost:62641
- **API**: http://localhost:62641/api

#### Vantagens da Solução de Serviço

✅ **Comandos executam na sua máquina**: Todos os comandos são executados diretamente no macOS, não em um container isolado

✅ **Roda em background**: O serviço inicia automaticamente no login e continua rodando

✅ **Reinicia automaticamente**: Se o serviço cair, o macOS o reinicia automaticamente

✅ **Logs organizados**: Logs são salvos em `logs/stream-deck.log` e `logs/stream-deck-error.log`

✅ **Fácil de gerenciar**: Comandos simples para iniciar, parar e verificar status

#### Solução de Problemas (Serviço)

##### Serviço não inicia

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

##### Serviço para de funcionar

1. Verifique os logs:
   ```bash
   tail -f logs/stream-deck.log
   ```

2. Reinicie o serviço:
   ```bash
   launchctl stop com.cyd.streamdeck
   launchctl start com.cyd.streamdeck
   ```

##### Porta 62641 já está em uso

Se outra aplicação estiver usando a porta 62641:

1. Encontre o processo:
   ```bash
   lsof -i :62641
   ```

2. Pare o processo ou altere a porta no `start.sh` e no `main.py`

#### Notas (Serviço)

- O serviço usa `launchd`, o sistema de gerenciamento de serviços do macOS
- Os logs são salvos em `logs/` no diretório do projeto
- O serviço inicia automaticamente quando você faz login no macOS
- Todos os comandos são executados com as permissões do seu usuário

### 3. Execução com Docker

#### Requisitos
- Docker

#### Como usar

##### Construir a imagem

```bash
# Construir a imagem (inclui banco de dados e uploads atuais)
docker build -t cyd-stream-deck .
```

**Importante**: O banco de dados (`stream_deck.db`) e os uploads (`uploads/`) serão incluídos na imagem durante o build.

##### Executar o container

```bash
# Executar com volume para uploads (recomendado)
docker run -d \
  --name cyd-stream-deck \
  -p 62641:62641 \
  -v $(pwd)/uploads:/app/uploads \
  --restart unless-stopped \
  cyd-stream-deck
```

##### Executar sem volume (usa uploads da imagem)

```bash
docker run -d \
  --name cyd-stream-deck \
  -p 62641:62641 \
  --restart unless-stopped \
  cyd-stream-deck
```

##### Comandos úteis

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
docker run -d --name cyd-stream-deck -p 62641:62641 -v $(pwd)/uploads:/app/uploads --restart unless-stopped cyd-stream-deck
```

#### Acessar a aplicação (Docker)

Após iniciar, a aplicação estará disponível em:
- **Interface Web**: http://localhost:62641
- **API**: http://localhost:62641/api

#### Persistência de dados (Docker)

- **Banco de dados**: Está **embutido na imagem Docker**. Qualquer mudança no banco dentro do container será perdida ao recriar o container. Para atualizar o banco na imagem, reconstrua a imagem após fazer backup do banco atualizado.
- **Uploads de imagens**:
  - Se usar `-v $(pwd)/uploads:/app/uploads`: Os uploads são persistidos no diretório local do projeto
  - Se não usar volume: Os uploads ficam apenas no container (perdidos ao remover o container)

#### Atualizando banco de dados e uploads na imagem (Docker)

Se você fez mudanças e quer incluí-las na imagem:

```bash
# 1. Pare e remova o container atual
docker stop cyd-stream-deck && docker rm cyd-stream-deck

# 2. Reconstrua a imagem com os dados atualizados
docker build -t cyd-stream-deck .

# 3. Execute novamente
docker run -d --name cyd-stream-deck -p 62641:62641 -v $(pwd)/uploads:/app/uploads --restart unless-stopped cyd-stream-deck
```

#### Nota sobre comandos do sistema (Docker)

A aplicação executa comandos do sistema via `subprocess`. No Docker, os comandos serão executados dentro do container Linux. Se você precisar executar comandos específicos do macOS, considere usar comandos compatíveis ou ajustar conforme necessário.

## Recursos da Interface

- **Lista discreta**: Visualização dos 6 botões em formato de lista (não grid)
- **Bolinha de cor**: Indicador de cor ao lado de cada botão (ao invés de fundo colorido)
- **Upload de imagens**: Envie imagens personalizadas para os ícones dos botões
- **Conversão para BMP**: Opção de converter imagens para formato BMP de 8 bits otimizado
- **Emoji alternativo**: Use emojis como alternativa aos ícones de imagem
- **Execução rápida**: Clique no botão para executar o comando
- **Edição fácil**: Clique no ícone de edição para configurar cada botão

## API Endpoints

### Autenticação

- `POST /api/login` - Faz login e retorna token JWT

### Botões

- `GET /api/buttons` - Lista todos os botões (requer autenticação)
- `GET /api/buttons/{position}` - Obtém um botão específico (requer autenticação)
- `PUT /api/buttons/{position}` - Atualiza um botão (requer autenticação)
- `POST /api/buttons/{position}/upload-icon` - Faz upload de imagem para o ícone (requer autenticação)
- `POST /api/buttons/{position}/convert-to-bmp` - Converte e faz upload de imagem JPG/PNG para BMP de 8 bits como ícone (requer autenticação)
- `POST /api/buttons/{position}/execute` - Executa o comando de um botão (requer autenticação)

### API Pública (para acesso remoto)

- `GET /api/execute/{position}?api_key=SUA_API_KEY` - **Executa um botão via API Key** (público, ideal para C/Cheap Yellow Display)

### Conversão de Imagens

- `POST /api/convert-to-bmp` - Converte uma imagem JPG ou PNG para BMP de 8 bits (requer autenticação)

### API Keys

- `POST /api/api-keys` - Cria uma nova API Key (requer autenticação)
- `GET /api/api-keys` - Lista todas as API Keys (requer autenticação)
- `DELETE /api/api-keys/{key_id}` - Desativa uma API Key (requer autenticação)

## Funcionalidade de Conversão de Imagens para BMP de 8 bits

Este documento descreve a nova funcionalidade de conversão de imagens JPG ou PNG para BMP de 8 bits no Stream Deck API.

### Visão Geral

A nova funcionalidade permite converter imagens JPG ou PNG para o formato BMP de 8 bits, otimizado para dispositivos com restrições de memória ou que exigem formatos específicos.

### Endpoints da API

#### 1. Converter imagem para botão específico

**Endpoint:** `POST /api/buttons/{position}/convert-to-bmp`

**Descrição:** Converte uma imagem JPG ou PNG para BMP de 8 bits e atualiza o ícone de um botão específico.

**Parâmetros:**
- `position` (path): Posição do botão (0-5)
- `file` (form-data): Arquivo de imagem (JPG, JPEG ou PNG)

**Requisitos:**
- Autenticação JWT necessária
- Apenas arquivos JPG, JPEG ou PNG são aceitos

**Exemplo de uso:**
```bash
curl -X POST "http://localhost:62641/api/buttons/0/convert-to-bmp" \
  -H "Authorization: Bearer seu_token_jwt" \
  -F "file=@imagem.jpg"
```

#### 2. Conversão geral de imagem

**Endpoint:** `POST /api/convert-to-bmp`

**Descrição:** Converte qualquer imagem JPG ou PNG para BMP de 8 bits.

**Parâmetros:**
- `file` (form-data): Arquivo de imagem (JPG, JPEG ou PNG)

**Requisitos:**
- Autenticação JWT necessária
- Apenas arquivos JPG, JPEG ou PNG são aceitos

**Exemplo de uso:**
```bash
curl -X POST "http://localhost:62641/api/convert-to-bmp" \
  -H "Authorization: Bearer seu_token_jwt" \
  -F "file=@imagem.png"
```

### Funcionalidades

- **Conversão para 8 bits:** As imagens são convertidas para modo de paleta com até 256 cores
- **Otimização:** Redução de tamanho de arquivo mantendo qualidade visual
- **Compatibilidade:** Formato BMP amplamente suportado
- **Integração:** Funciona com o sistema existente de ícones de botões

### Implementação Técnica

A conversão é feita usando a biblioteca Pillow com os seguintes passos:
1. Abrir a imagem original (JPG/PNG)
2. Converter para modo RGB se necessário
3. Converter para modo de paleta (P) com 256 cores adaptativas
4. Salvar como arquivo BMP

### Exemplo de Código

```python
from PIL import Image

# Abrir imagem
img = Image.open('imagem.jpg')

# Converter para 8 bits (paleta de cores)
if img.mode != 'P':
    img = img.convert('RGB')  # Converter para RGB primeiro se necessário
    img = img.convert('P', palette=Image.ADAPTIVE, colors=256)

# Salvar como BMP
img.save('imagem_8bit.bmp', 'BMP')
```

## Uso Remoto (API Key)

Para usar com Cheap Yellow Display ou qualquer cliente em C, você precisa:

1. **Criar uma API Key**: Acesse a interface web e vá na seção "API Keys"
2. **Use a URL pública**:
   ```
   GET http://localhost:62641/api/execute/{position}?api_key=SUA_API_KEY
   ```

### Exemplo em C

Veja o arquivo `example_c.c` para um exemplo completo usando libcurl:

```c
// Compilar: gcc -o client example_c.c -lcurl
execute_button(0, "sua-api-key", "http://localhost:62641");
```

### Exemplo com curl

```bash
curl "http://localhost:62641/api/execute/0?api_key=sua-api-key"
```

### Exemplo com script

```bash
./example_curl.sh 0 "sua-api-key"
```

## Segurança

O sistema bloqueia automaticamente comandos perigosos como:
- `rm` (com qualquer flag)
- `shutdown`, `reboot`, `halt`, `poweroff`
- `dd`, `mkfs`, `fdisk`
- Comandos com `sudo` perigosos
- Redirecionamentos para dispositivos do sistema
- E outros padrões perigosos

## Estrutura do Projeto

```
cyd-stream-deck/
├── main.py                 # Aplicação FastAPI principal
├── database.py            # Modelos e configuração do banco
├── security.py            # Autenticação e JWT
├── command_validator.py   # Validação de comandos seguros
├── image_utils.py         # Utilitários de conversão de imagem
├── requirements.txt       # Dependências Python
├── templates/
│   ├── index.html        # Interface web
│   └── setup.html        # Página de setup
├── uploads/              # Diretório para imagens dos ícones
├── example_c.c           # Exemplo de uso em C
├── example_curl.sh       # Exemplo de uso com curl
├── run.sh                # Script para executar o servidor
├── start.sh              # Script para iniciar o serviço
├── install-service.sh    # Script para instalar como serviço
├── uninstall-service.sh  # Script para desinstalar o serviço
├── com.cyd.streamdeck.plist  # Configuração do serviço macOS
├── Dockerfile            # Configuração do Docker
└── stream_deck.db        # Banco SQLite (criado automaticamente)
```

## Desenvolvimento

O banco de dados é criado automaticamente na primeira execução. Os 6 botões são inicializados com valores padrão.

Para alterar as credenciais padrão do admin, configure as variáveis de ambiente `ADMIN_USERNAME` e `ADMIN_PASSWORD` no arquivo `.env`.