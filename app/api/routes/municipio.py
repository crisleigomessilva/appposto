from fastapi import APIRouter, Depends, HTTPException
import requests
from sqlalchemy.orm import Session
from app.models.municipio import Municipio
from app.core.database import get_session
from app.api.routes.auth import get_current_user   # Dependência para validação do token

router = APIRouter()

IBGE_API_URL = "https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios"


@router.post("/municipios/{uf}")
def buscar_e_salvar_municipios(
    uf: str,
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),  # Validação do token
):
    """
    Busca os municípios da API do IBGE e salva na tabela 'municipio'.
    Requer autenticação por token JWT.

    Args:
        uf (str): Sigla do estado para buscar os municípios (ex.: SP, RJ).
        db (Session): Sessão do banco de dados.

    Returns:
        dict: Resumo da operação.
    """
    # Validação da sigla do estado
    if len(uf) != 2 or not uf.isalpha():
        raise HTTPException(status_code=400, detail="UF inválido. Deve conter 2 letras.")

    # Busca os municípios na API do IBGE
    response = requests.get(IBGE_API_URL.format(uf=uf.upper()))
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Erro ao acessar a API do IBGE.")
    
    municipios = response.json()

    # Processa os municípios
    for municipio_data in municipios:
        id_ibge = municipio_data["id"]
        nome = municipio_data["nome"]
        regiao = municipio_data["microrregiao"]["mesorregiao"]["UF"]["regiao"]["id"]
        nome_regiao = municipio_data["microrregiao"]["mesorregiao"]["UF"]["regiao"]["nome"]
        estado = municipio_data["microrregiao"]["mesorregiao"]["UF"]["nome"]

        # Verifica se o município já existe
        municipio_existente = db.query(Municipio).filter(Municipio.id_ibge == id_ibge).first()
        if municipio_existente:
            # Atualiza os dados se necessário
            municipio_existente.nome = nome
            municipio_existente.uf = uf.upper()
            municipio_existente.regiao = regiao
            municipio_existente.nome_regiao = nome_regiao
            municipio_existente.estado = estado
        else:
            # Insere um novo registro
            novo_municipio = Municipio(
                id_ibge=id_ibge,
                nome=nome,
                uf=uf.upper(),
                regiao=regiao,
                nome_regiao=nome_regiao,
                estado=estado,
            )
            db.add(novo_municipio)

    # Confirma as alterações no banco de dados
    db.commit()

    return {"message": "Municípios atualizados com sucesso.", "uf": uf.upper(), "total": len(municipios)}
