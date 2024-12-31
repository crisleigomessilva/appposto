from sqlalchemy import Column, Integer, Float, String
from app.models.base import Base

class DensidadeGasolina(Base):
    __tablename__ = "densidade_gasolina"

    id = Column(Integer, primary_key=True, index=True)
    temperatura_observada = Column(Float, nullable=False)  # Temperatura observada
    densidade_observada = Column(Float, nullable=False)  # Tipo de densidade, e.g., "0.700", "0.701", etc.
    densidade_corrigida = Column(Float, nullable=False)  # Valor da densidade para o tipo específico