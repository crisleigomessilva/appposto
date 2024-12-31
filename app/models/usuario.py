import hashlib
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base
from datetime import datetime

class Usuario(Base):
    __tablename__ = "usuario"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    senha = Column(String, nullable=False)
    id_md5 = Column(String, unique=True)  # Campo único

    classe_acesso_id = Column(Integer, ForeignKey("classeacesso.id"))
    classe_acesso = relationship("ClasseAcesso", back_populates="usuarios")

    empresas = relationship(
        "Empresa", secondary="usuario_empresa", back_populates="usuarios"
    )

    @staticmethod
    def gerar_id_md5(id: int, email: str, senha: str) -> str:
        """
        Gera o ID MD5 único com base no ID, email e senha.
        Args:
            id (int): ID único do usuário.
            email (str): Email do usuário.
            senha (str): Senha criptografada do usuário.
        Returns:
            str: Hash MD5 gerado.
        """
        data = f"{id}-{email}-{senha}".encode("utf-8")
        return hashlib.md5(data).hexdigest()