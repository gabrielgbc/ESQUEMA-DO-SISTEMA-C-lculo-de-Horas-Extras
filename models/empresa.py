"""
models/empresa.py
Modelo de dados para Empresa
"""
from sqlalchemy import Column, Integer, String
from models.database import Base

class Empresa(Base):
    __tablename__ = "empresas"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), nullable=False)
    cnpj = Column(String(18), unique=True, nullable=False)
    endereco = Column(String(300))
    telefone = Column(String(20))
    email = Column(String(100))
    
    def __repr__(self):
        return f"<Empresa(nome={self.nome}, cnpj={self.cnpj})>"
    
    def to_dict(self):
        """Converte o objeto em dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'cnpj': self.cnpj,
            'endereco': self.endereco,
            'telefone': self.telefone,
            'email': self.email
        }