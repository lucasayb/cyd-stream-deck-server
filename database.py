from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
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


class Config(Base):
    __tablename__ = "config"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)


class SetupStatus(Base):
    __tablename__ = "setup_status"
    
    id = Column(Integer, primary_key=True, index=True)
    is_completed = Column(Integer, default=0)  # 0 = não completado, 1 = completado
    completed_at = Column(String, default="")


def init_db():
    """Inicializa o banco de dados criando as tabelas"""
    Base.metadata.create_all(bind=engine)
    
    # Inicializa configurações padrão
    db = SessionLocal()
    try:
        # Verifica se já existe configuração de setup
        setup = db.query(SetupStatus).first()
        if not setup:
            setup = SetupStatus(is_completed=0)
            db.add(setup)
            db.commit()
        
        # Configurações padrão
        default_configs = {
            "button_count": "6"
        }
        
        for key, value in default_configs.items():
            config = db.query(Config).filter(Config.key == key).first()
            if not config:
                config = Config(key=key, value=value)
                db.add(config)
        
        db.commit()
    finally:
        db.close()


def get_config_value(key: str, default: str = "") -> str:
    """Obtém valor de configuração"""
    db = SessionLocal()
    try:
        config = db.query(Config).filter(Config.key == key).first()
        return config.value if config else default
    finally:
        db.close()


def set_config_value(key: str, value: str):
    """Define valor de configuração"""
    db = SessionLocal()
    try:
        config = db.query(Config).filter(Config.key == key).first()
        if config:
            config.value = value
        else:
            config = Config(key=key, value=value)
            db.add(config)
        db.commit()
    finally:
        db.close()


def is_setup_completed() -> bool:
    """Verifica se o setup foi completado"""
    db = SessionLocal()
    try:
        setup = db.query(SetupStatus).first()
        return setup.is_completed == 1 if setup else False
    finally:
        db.close()


def complete_setup():
    """Marca o setup como completado"""
    db = SessionLocal()
    try:
        setup = db.query(SetupStatus).first()
        if setup:
            setup.is_completed = 1
            setup.completed_at = datetime.now().isoformat()
        else:
            setup = SetupStatus(is_completed=1, completed_at=datetime.now().isoformat())
            db.add(setup)
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

