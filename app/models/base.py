from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy import Column, DateTime
from datetime import datetime


@as_declarative()
class Base:
    id: int
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    # Campos padrão para todas as tabelas
    data_inclusao = Column(DateTime, default=datetime.utcnow, nullable=False)
    data_alteracao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
