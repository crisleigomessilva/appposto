from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.base import Base

class ClasseAcesso(Base):
    __tablename__ = "classeacesso"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False, unique=True)
    descricao = Column(String, nullable=True)

    usuarios = relationship("Usuario", back_populates="classe_acesso")
