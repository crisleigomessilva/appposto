from sqlalchemy import Column, Integer, ForeignKey, Table
from app.models.base import Base

# Tabela de associação muitos-para-muitos
usuario_empresa = Table(
    "usuario_empresa",
    Base.metadata,
    Column("usuario_id", Integer, ForeignKey("usuario.id"), primary_key=True),
    Column("empresa_id", Integer, ForeignKey("empresa.id"), primary_key=True),
)
