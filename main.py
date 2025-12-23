from fastapi import FastAPI, Depends, HTTPException, status, Form, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import subprocess
import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

from database import get_db, Button, User, ApiKey, init_db
from security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from datetime import datetime, timedelta
from command_validator import validate_command
import secrets
from fastapi import Query

load_dotenv()

app = FastAPI(title="Stream Deck API", version="1.0.0")

# Cria diretório para uploads
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Serve arquivos estáticos (imagens)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Inicializa banco de dados
init_db()

# Cria usuário admin padrão se não existir
def create_default_admin():
    db_gen = get_db()
    db = next(db_gen)
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin_username = os.getenv("ADMIN_USERNAME", "admin")
            admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
            admin = User(
                username=admin_username,
                hashed_password=get_password_hash(admin_password)
            )
            db.add(admin)
            db.commit()
            print(f"Usuário admin criado: {admin_username}")
    finally:
        db.close()

create_default_admin()


# Função para validar API Key
def validate_api_key(api_key: str, db: Session) -> bool:
    """Valida se a API key existe e está ativa"""
    if not api_key:
        return False
    key_obj = db.query(ApiKey).filter(
        ApiKey.key == api_key,
        ApiKey.is_active == 1
    ).first()
    return key_obj is not None


# Models
class ButtonCreate(BaseModel):
    position: int
    icon: str = "📱"
    background_color: str = "#3B82F6"
    command: str
    label: str = ""


class ButtonUpdate(BaseModel):
    icon: Optional[str] = None
    background_color: Optional[str] = None
    command: Optional[str] = None
    label: Optional[str] = None


class ButtonResponse(BaseModel):
    id: int
    position: int
    icon: str
    background_color: str
    command: str
    label: str

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ApiKeyResponse(BaseModel):
    id: int
    key: str
    name: str
    created_at: str
    is_active: bool

    class Config:
        from_attributes = True


class ApiKeyCreate(BaseModel):
    name: str = ""


# API Routes
@app.post("/api/login", response_model=TokenResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Endpoint de login"""
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/buttons", response_model=List[ButtonResponse])
async def get_buttons(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna todos os botões"""
    buttons = db.query(Button).order_by(Button.position).all()
    return buttons


@app.get("/api/buttons/{position}", response_model=ButtonResponse)
async def get_button(
    position: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna um botão específico por posição"""
    button = db.query(Button).filter(Button.position == position).first()
    if not button:
        raise HTTPException(status_code=404, detail="Botão não encontrado")
    return button


@app.post("/api/buttons/{position}/upload-icon")
async def upload_icon(
    position: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload de imagem para o ícone de um botão"""
    button = db.query(Button).filter(Button.position == position).first()
    if not button:
        raise HTTPException(status_code=404, detail="Botão não encontrado")
    
    # Valida tipo de arquivo
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser uma imagem")
    
    # Gera nome único para o arquivo
    file_extension = Path(file.filename).suffix if file.filename else '.png'
    filename = f"button_{position}_{int(os.urandom(4).hex(), 16)}{file_extension}"
    file_path = UPLOAD_DIR / filename
    
    # Salva arquivo
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Remove imagem antiga se existir e não for emoji
    if button.icon and button.icon.startswith('/uploads/'):
        old_file_path = UPLOAD_DIR / Path(button.icon).name
        if old_file_path.exists():
            try:
                os.remove(old_file_path)
            except:
                pass
    
    # Atualiza botão com caminho da imagem
    button.icon = f"/uploads/{filename}"
    db.commit()
    db.refresh(button)
    
    return {"icon": button.icon}


@app.put("/api/buttons/{position}", response_model=ButtonResponse)
async def update_button(
    position: int,
    button_update: ButtonUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualiza um botão"""
    button = db.query(Button).filter(Button.position == position).first()
    if not button:
        raise HTTPException(status_code=404, detail="Botão não encontrado")
    
    # Valida comando se fornecido
    if button_update.command is not None:
        is_valid, error_msg = validate_command(button_update.command)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
    
    # Atualiza campos
    if button_update.icon is not None:
        button.icon = button_update.icon
    if button_update.background_color is not None:
        button.background_color = button_update.background_color
    if button_update.command is not None:
        button.command = button_update.command
    if button_update.label is not None:
        button.label = button_update.label
    
    db.commit()
    db.refresh(button)
    return button


def execute_button_command(position: int, db: Session):
    """Função auxiliar para executar comando de um botão"""
    button = db.query(Button).filter(Button.position == position).first()
    if not button:
        raise HTTPException(status_code=404, detail="Botão não encontrado")
    
    # Valida comando antes de executar
    is_valid, error_msg = validate_command(button.command)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Comando inválido: {error_msg}")
    
    try:
        # Executa o comando no shell do macOS
        result = subprocess.run(
            button.command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,  # Timeout de 30 segundos
            cwd=os.path.expanduser("~")  # Executa no diretório home do usuário
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Comando excedeu o tempo limite")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao executar comando: {str(e)}")


@app.post("/api/buttons/{position}/execute")
async def execute_button(
    position: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Executa o comando de um botão (requer autenticação JWT)"""
    return execute_button_command(position, db)


@app.get("/api/execute/{position}")
async def execute_button_public(
    position: int,
    api_key: str = Query(..., description="API Key para autenticação"),
    db: Session = Depends(get_db)
):
    """
    Executa o comando de um botão via API Key (público)
    
    Uso em C:
    ```c
    // Exemplo usando libcurl
    curl_easy_setopt(curl, CURLOPT_URL, "http://localhost:8000/api/execute/0?api_key=SUA_API_KEY");
    ```
    
    Ou simplesmente:
    ```
    GET http://localhost:8000/api/execute/0?api_key=SUA_API_KEY
    ```
    """
    # Valida API key
    if not validate_api_key(api_key, db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida ou inativa"
        )
    
    return execute_button_command(position, db)


# API Key Management
@app.post("/api/api-keys", response_model=ApiKeyResponse)
async def create_api_key(
    key_data: ApiKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cria uma nova API Key"""
    # Gera uma API key segura
    api_key = secrets.token_urlsafe(32)
    
    new_key = ApiKey(
        key=api_key,
        name=key_data.name or "API Key",
        created_at=datetime.now().isoformat(),
        is_active=1
    )
    db.add(new_key)
    db.commit()
    db.refresh(new_key)
    
    return new_key


@app.get("/api/api-keys", response_model=List[ApiKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista todas as API Keys"""
    keys = db.query(ApiKey).order_by(ApiKey.created_at.desc()).all()
    return keys


@app.delete("/api/api-keys/{key_id}")
async def delete_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Desativa uma API Key"""
    key_obj = db.query(ApiKey).filter(ApiKey.id == key_id).first()
    if not key_obj:
        raise HTTPException(status_code=404, detail="API Key não encontrada")
    
    key_obj.is_active = 0
    db.commit()
    
    return {"message": "API Key desativada com sucesso"}


# Frontend
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Página principal"""
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

