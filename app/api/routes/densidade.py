from typing import Union
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, Field
from app.core.database import get_session
from app.api.routes.auth import get_current_user # Dependência para validar token
from app.models.densidade_gasolina import DensidadeGasolina
from app.models.densidade_etanol import DensidadeEtanol
from app.models.densidade_diesel import DensidadeDiesel

router = APIRouter()

# Faixas de densidade aceitáveis para cada tipo de combustível
DENSIDADE_GASOLINA_MIN = 0.715
DENSIDADE_GASOLINA_MAX = 0.775

DENSIDADE_DIESEL_S10_MIN = 0.820
DENSIDADE_DIESEL_S10_MAX = 0.850

DENSIDADE_DIESEL_S500_MIN = 0.830
DENSIDADE_DIESEL_S500_MAX = 0.880

DENSIDADE_ETANOL_MIN = 0.790
DENSIDADE_ETANOL_MAX = 0.806

# Faixa aceitável de teor alcoólico para o Etanol
TEOR_ALCOOLICO_MIN = 92.5
TEOR_ALCOOLICO_MAX = 95.4

class DensidadeRequest(BaseModel):
    temperatura_observada: float
    densidade_observada: float
    tipo_combustivel: str

class DensidadeResponse(BaseModel):
    temperatura_lida: float
    densidade_lida: float
    densidade_corrigida: float
    teor_alcoolico: Union[bool, float] = Field(default=False)  # Use Union para aceitar booleano ou float
    status: str  # Usando uma string para o status (Dentro ou Fora da especificação)

@router.post("/buscar_densidade_corrigida", response_model=DensidadeResponse)
async def buscar_densidade_corrigida(
    dados: DensidadeRequest,
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),  # Validação do token
):
    """
    Busca a densidade corrigida com base nos dados fornecidos.
    Requer autenticação por token JWT.
    """
    # Mapeamento dos tipos de combustível para seus respectivos modelos de banco de dados
    model_map = {
        "Gasolina Comum": DensidadeGasolina,
        "Gasolina Aditivada": DensidadeGasolina,
        "Gasolina Podium": DensidadeGasolina,
        "Etanol": DensidadeEtanol,
        "Etanol Premium": DensidadeEtanol,
        "Diesel S10": DensidadeDiesel,
        "Diesel S10 Aditivado": DensidadeDiesel,
        "Diesel S500": DensidadeDiesel,
        "Diesel S500 Aditivado": DensidadeDiesel,
    }

    model = model_map.get(dados.tipo_combustivel)
    if not model:
        raise HTTPException(status_code=400, detail="Tipo de combustível inválido.")

    # Escolher a coluna de densidade corrigida dependendo do tipo de combustível
    if model == DensidadeEtanol:
        coluna_corrigida = model.densidade_corrigida_20c
    else:
        coluna_corrigida = model.densidade_corrigida

    # Permitindo variação de até 1°C e 0.01 g/mL na densidade para maior flexibilidade
    resultado = db.query(
        model.temperatura_observada,
        model.densidade_observada,
        coluna_corrigida,
        model.teor_alcoolico if model == DensidadeEtanol else False
    ).filter(
        func.abs(model.temperatura_observada - dados.temperatura_observada) < 1.0,
        func.abs(model.densidade_observada - dados.densidade_observada) < 0.01
    ).order_by(
        func.abs(model.temperatura_observada - dados.temperatura_observada),
        func.abs(model.densidade_observada - dados.densidade_observada)
    ).first()

    if resultado is None:
        raise HTTPException(status_code=404, detail="Densidade correspondente não encontrada.")

    # Verificação da densidade corrigida dentro das faixas permitidas
    densidade_corrigida = resultado[2]
    teor_alcoolico = resultado[3] if model == DensidadeEtanol else None
    status = "Fora da especificação"

    if dados.tipo_combustivel in ["Gasolina Comum", "Gasolina Aditivada", "Gasolina Podium"]:
        if DENSIDADE_GASOLINA_MIN <= densidade_corrigida <= DENSIDADE_GASOLINA_MAX:
            status = "Dentro da especificação"
    elif dados.tipo_combustivel in ["Diesel S10", "Diesel S10 Aditivado"]:
        if DENSIDADE_DIESEL_S10_MIN <= densidade_corrigida <= DENSIDADE_DIESEL_S10_MAX:
            status = "Dentro da especificação"
    elif dados.tipo_combustivel in ["Diesel S500", "Diesel S500 Aditivado"]:
        if DENSIDADE_DIESEL_S500_MIN <= densidade_corrigida <= DENSIDADE_DIESEL_S500_MAX:
            status = "Dentro da especificação"
    elif dados.tipo_combustivel in ["Etanol", "Etanol Premium"]:
        if 0.8029 <= densidade_corrigida <= 0.8112 and TEOR_ALCOOLICO_MIN <= teor_alcoolico <= TEOR_ALCOOLICO_MAX:
            status = "Dentro da especificação (Etanol Hidratado Comum)"
        elif 0.7962 <= densidade_corrigida <= 0.8029 and 95.5 <= teor_alcoolico <= 97.7:
            status = "Dentro da especificação (Etanol Hidratado Premium)"
        else:
            status = "Fora da especificação (Densidade ou Teor alcoólico fora da faixa permitida)"

    if "Fora da especificação" in status:
        raise HTTPException(status_code=400, detail="A densidade corrigida está fora da faixa permitida ou o teor alcoólico está fora da faixa permitida.")

    # Retornar os dados encontrados com a verificação de status
    return DensidadeResponse(
        temperatura_lida=resultado[0],
        densidade_lida=resultado[1],
        densidade_corrigida=densidade_corrigida,
        teor_alcoolico=teor_alcoolico if model == DensidadeEtanol else False,
        status=status
    )
