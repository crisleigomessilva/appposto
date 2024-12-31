from fastapi import FastAPI
from app.api.routes import user, municipio, auth, densidade, import_densidade_combustivel
import app.models  # Certifique-se de carregar os modelos para registrar no metadata
from app.core.database import engine
from app.models.base import Base


Base.metadata.create_all(bind=engine)

app = FastAPI()

# Registrar os routers
app.include_router(user.router, prefix="/usuarios", tags=["Usuários"])
app.include_router(municipio.router, prefix="/municipios", tags=["Municípios"])
app.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
app.include_router(densidade.router, prefix="/densidade", tags=["Densidade"])
app.include_router(import_densidade_combustivel.router, prefix="/import-densidade", tags=["Importação de Densidades"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the AppPosto API"}

@app.get("/test")
def test_endpoint():
    return {"status": "OK"}
