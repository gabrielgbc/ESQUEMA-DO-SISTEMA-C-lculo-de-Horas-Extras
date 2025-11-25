"""
models/registro_jornada.py
Modelo de dados para Registro de Jornada
"""
from sqlalchemy import Column, Integer, Float, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from models.database import Base

class RegistroJornada(Base):
    __tablename__ = "registros_jornada"
    
    id = Column(Integer, primary_key=True, index=True)
    funcionario_id = Column(Integer, ForeignKey('funcionarios.id', ondelete="CASCADE"))
    data = Column(Date, nullable=False)
    hora_entrada = Column(Time, nullable=False)
    hora_saida = Column(Time, nullable=False)
    intervalo = Column(Float, default=0.0)
    horas_trabalhadas = Column(Float, nullable=False)
    horas_extras = Column(Float, default=0.0)
    horas_faltantes = Column(Float, default=0.0)
    
    # Relacionamento
    funcionario = relationship("Funcionario", backref="registros")
    
    def __repr__(self):
        return f"<RegistroJornada(funcionario_id={self.funcionario_id}, data={self.data})>"