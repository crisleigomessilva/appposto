from sqlalchemy import Column, Integer, Float, String
from app.models.base import Base

class DensidadeDiesel(Base):
    __tablename__ = "densidade_diesel"

    id = Column(Integer, primary_key=True, index=True)
    temperatura_observada = Column(Float, nullable=False)  # Temperatura observada
    densidade_observada = Column(Float, nullable=False)  # Tipo de densidade observada, e.g., "0.820", "0.821", etc.
    densidade_corrigida = Column(Float, nullable=False)  # Valor da densidade corrigida
 