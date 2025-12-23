# Stream Deck Custom - API e Interface Web

Sistema completo para gerenciar um Stream Deck customizado com 6 botões, permitindo configurar ícones, cores e comandos através de uma interface web protegida por autenticação.

## Características

- ✅ 6 botões configuráveis
- ✅ Banco de dados SQLite
- ✅ Interface web discreta com lista (Tailwind CSS)
- ✅ Upload de imagens para ícones
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

## Uso

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
http://localhost:8000
```

3. Faça login com as credenciais padrão:
   - Usuário: `admin`
   - Senha: `admin123`

## Recursos da Interface

- **Lista discreta**: Visualização dos 6 botões em formato de lista (não grid)
- **Bolinha de cor**: Indicador de cor ao lado de cada botão (ao invés de fundo colorido)
- **Upload de imagens**: Envie imagens personalizadas para os ícones dos botões
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
- `POST /api/buttons/{position}/execute` - Executa o comando de um botão (requer autenticação)

### API Pública (para acesso remoto)

- `GET /api/execute/{position}?api_key=SUA_API_KEY` - **Executa um botão via API Key** (público, ideal para C/Cheap Yellow Display)

### API Keys

- `POST /api/api-keys` - Cria uma nova API Key (requer autenticação)
- `GET /api/api-keys` - Lista todas as API Keys (requer autenticação)
- `DELETE /api/api-keys/{key_id}` - Desativa uma API Key (requer autenticação)

## Uso Remoto (API Key)

Para usar com Cheap Yellow Display ou qualquer cliente em C, você precisa:

1. **Criar uma API Key**: Acesse a interface web e vá na seção "API Keys"
2. **Use a URL pública**: 
   ```
   GET http://localhost:8000/api/execute/{position}?api_key=SUA_API_KEY
   ```

### Exemplo em C

Veja o arquivo `example_c.c` para um exemplo completo usando libcurl:

```c
// Compilar: gcc -o client example_c.c -lcurl
execute_button(0, "sua-api-key", "http://localhost:8000");
```

### Exemplo com curl

```bash
curl "http://localhost:8000/api/execute/0?api_key=sua-api-key"
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
├── requirements.txt       # Dependências Python
├── templates/
│   └── index.html        # Interface web
├── uploads/              # Diretório para imagens dos ícones
├── example_c.c           # Exemplo de uso em C
├── example_curl.sh       # Exemplo de uso com curl
└── stream_deck.db        # Banco SQLite (criado automaticamente)
```

## Desenvolvimento

O banco de dados é criado automaticamente na primeira execução. Os 6 botões são inicializados com valores padrão.

Para alterar as credenciais padrão do admin, configure as variáveis de ambiente `ADMIN_USERNAME` e `ADMIN_PASSWORD` no arquivo `.env`.

