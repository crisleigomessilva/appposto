from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from app.models.base import Base

class Densidades(Base):
tablename = "densidade"
id = Column(Integer, primary_key=True, index=True)
temperatura = Column(Float(precision=2), nullable=False)  # Temperatura numérica com 2 casas decimais
densidade_observ = Column(Float(precision=4), nullable=False)  # Densidade observada com 4 casas decimais
densidade_20c = Column(Float(precision=4), nullable=False)  # Densidade a 20°C com 4 casas decimais