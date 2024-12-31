from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.core.config import settings  # Importa as configurações do .env


# Cria o engine principal para o banco
engine = create_engine(settings.DATABASE_URL, future=True, echo=True)


# Função para obter uma sessão do banco de dados
def get_session():
    with Session(engine) as session:
        yield session
