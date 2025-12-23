from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = "sqlite:///./stream_deck.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Button(Base):
    __tablename__ = "buttons"
    
    id = Column(Integer, primary_key=True, index=True)
    position = Column(Integer, unique=True, nullable=False)  # 0-5 para 6 botões
    icon = Column(String, default="📱")  # Emoji ou nome do arquivo de ícone
    background_color = Column(String, default="#3B82F6")  # Cor em hex
    command = Column(Text, nullable=False)  # Comando a ser executado
    label = Column(String, default="")  # Label opcional para o botão


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)


class ApiKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, default="")  # Nome descritivo da chave
    created_at = Column(String, default="")  # Timestamp de criação
    is_active = Column(Integer, default=1)  # 1 = ativa, 0 = desativada


def init_db():
    """Inicializa o banco de dados criando as tabelas"""
    Base.metadata.create_all(bind=engine)
    
    # Cria botões padrão se não existirem
    db = SessionLocal()
    try:
        existing_buttons = db.query(Button).count()
        if existing_buttons == 0:
            for i in range(6):
                button = Button(
                    position=i,
                    icon="📱",
                    background_color="#3B82F6",
                    command=f"echo 'Button {i+1}'",
                    label=f"Botão {i+1}"
                )
                db.add(button)
            db.commit()
    finally:
        db.close()


def get_db():
    """Dependency para obter sessão do banco"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

