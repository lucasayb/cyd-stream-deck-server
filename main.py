from fastapi import FastAPI, Depends, HTTPException, status, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import subprocess
import os
from dotenv import load_dotenv

from database import get_db, Button, User, init_db
from security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from datetime import timedelta
from command_validator import validate_command

load_dotenv()

app = FastAPI(title="Stream Deck API", version="1.0.0")

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


@app.post("/api/buttons/{position}/execute")
async def execute_button(
    position: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Executa o comando de um botão"""
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


# Frontend
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Página principal"""
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

