from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.base import Base


class Municipio(Base):
    __tablename__ = "municipio"

    id_ibge = Column(Integer, primary_key=True, index=True)  # ID fornecido pelo IBGE
    nome = Column(String, nullable=False)  # Nome do município
    uf = Column(String(2), nullable=False)  # Sigla do estado
    estado = Column(String, nullable=False)  # Nome completo do estado
    regiao = Column(String, nullable=False)  # Código da região
    nome_regiao = Column(String, nullable=False)  # Nome da região

    # Relacionamento com Endereço
    enderecos = relationship("Endereco", back_populates="municipio")
