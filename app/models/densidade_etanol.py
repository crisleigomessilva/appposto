from sqlalchemy import Column, Integer, Float, String
from app.models.base import Base

class DensidadeEtanol(Base):
    __tablename__ = "densidade_etanol"
    
    id = Column(Integer, primary_key=True, index=True)
    temperatura_observada = Column(Float, nullable=False)  # Temperatura observada
    densidade_observada = Column(Float, nullable=False)  # Massa específica lida, em g/mL
    densidade_corrigida_20c = Column(Float, nullable=False)  # Massa específica a 20 ºC, em g/mL
    teor_alcoolico = Column(Float, nullable=True)  # Grau alcoólico, em %m/m ou ºINPM
    # Removendo o fator de correção, pois não está presente na planilha
