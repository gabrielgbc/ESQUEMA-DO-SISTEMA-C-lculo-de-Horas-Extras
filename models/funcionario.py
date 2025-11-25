"""
models/funcionario.py
Modelo de dados para Funcionário - CORRIGIDO
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from models.database import Base

class Funcionario(Base):
    __tablename__ = "funcionarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    cargo = Column(String(100), nullable=False)
    carga_horaria_diaria = Column(Float, nullable=False)  # Em horas (ex: 8.0)
    valor_hora = Column(Float, nullable=False)  # Valor em reais
    empresa_id = Column(Integer, ForeignKey('empresas.id', ondelete="SET NULL"))
    
    # Relacionamento com Empresa
    empresa = relationship("Empresa", backref="funcionarios")
    
    def __repr__(self):
        return f"<Funcionario(nome={self.nome}, cargo={self.cargo})>"
    
    def to_dict(self):
        """Converte o objeto em dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'cargo': self.cargo,
            'carga_horaria_diaria': self.carga_horaria_diaria,
            'valor_hora': self.valor_hora,
            'empresa_id': self.empresa_id,
            'empresa_nome': self.empresa.nome if self.empresa else None
        }