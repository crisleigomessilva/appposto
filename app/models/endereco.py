from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.models.base import Base
import enum


class TipoEndereco(enum.Enum):
    PRINCIPAL = "Principal"
    CORRESPONDENCIA = "Correspondência"
    COBRANCA = "Cobrança"


class Endereco(Base):
    __tablename__ = "endereco"

    id = Column(Integer, primary_key=True, index=True)
    logradouro = Column(String, nullable=False)  # Nome da rua/avenida
    numero = Column(String, nullable=True)  # Número do endereço
    complemento = Column(String, nullable=True)  # Complemento
    cep = Column(String(8), nullable=False)  # CEP
    tipo = Column(Enum(TipoEndereco), nullable=False)  # Tipo do endereço
    principal = Column(Boolean, default=False, nullable=False)  # Indica se é o endereço principal
    municipio_id = Column(Integer, ForeignKey("municipio.id_ibge"), nullable=False)  # Chave estrangeira para município

    # Relacionamento com Município
    municipio = relationship("Municipio", back_populates="enderecos")
