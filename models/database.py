"""
models/database.py
Configuração do banco de dados SQLAlchemy - ATUALIZADO
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuração do banco de dados SQLite
DATABASE_URL = "sqlite:///horas_extras.db"

# Criação do engine
engine = create_engine(DATABASE_URL, echo=False)

# Criação da sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()

def get_db():
    """Retorna uma sessão do banco de dados"""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e

def init_db():
    """Inicializa o banco de dados criando todas as tabelas"""
    from models.empresa import Empresa
    from models.funcionario import Funcionario
    from models.registro_jornada import RegistroJornada
    Base.metadata.create_all(bind=engine)