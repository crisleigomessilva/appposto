from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from sqlalchemy.orm import Session
from app.core.database import get_session
from app.models.densidade_gasolina import DensidadeGasolina
from app.models.densidade_diesel import DensidadeDiesel
from app.models.densidade_etanol import DensidadeEtanol
import pandas as pd

router = APIRouter()

@router.post("/import_densidade_combustivel")
async def import_densidade_combustivel(
    tabela: str = Form(...),
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_session)
):
    """
    Importa os dados do arquivo Excel e insere na tabela apropriada.
    """
    if tabela not in ["gasolina", "diesel", "etanol"]:
        raise HTTPException(status_code=400, detail="Apenas as tabelas de gasolina, diesel e etanol são suportadas neste endpoint.")

    try:
        df = pd.read_excel(arquivo.file, header=0, index_col=0)
        if tabela == "gasolina":
            await importar_gasolina(df, db)
        elif tabela == "diesel":
            await importar_diesel(df, db)
        elif tabela == "etanol":
            await importar_etanol(df, db)
        return {"message": f"Dados de densidade de {tabela} importados com sucesso."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao processar o arquivo: {str(e)}")

async def importar_gasolina(df, db):
    # Converte os cabeçalhos de coluna para float
    df.columns = [float(col) for col in df.columns]
    for temperatura, row in df.iterrows():
        for densidade_observada, densidade_corrigida in row.items():
            nova_entrada = DensidadeGasolina(
                temperatura_observada=temperatura,
                densidade_observada=densidade_observada,
                densidade_corrigida=densidade_corrigida
            )
            db.add(nova_entrada)
    db.commit()

async def importar_diesel(df, db):
    df.columns = [float(col) for col in df.columns]
    for temperatura, row in df.iterrows():
        for densidade_observada, densidade_corrigida in row.items():
            nova_entrada = DensidadeDiesel(
                temperatura_observada=temperatura,
                densidade_observada=densidade_observada,
                densidade_corrigida=densidade_corrigida
            )
            db.add(nova_entrada)
    db.commit()

async def importar_etanol(df, db):
    for temperatura, row in df.iterrows():
        densidade_observada = row['Massa específica lida, em g/mL']
        densidade_corrigida_20c = row['Massa específica a 20 ºC, em g/mL']
        teor_alcoolico = row.get('Grau alcoólico, em %m/m ou ºINPM', None)
        nova_entrada = DensidadeEtanol(
            temperatura_observada=temperatura,
            densidade_observada=densidade_observada,
            densidade_corrigida_20c=densidade_corrigida_20c,
            teor_alcoolico=teor_alcoolico
        )
        db.add(nova_entrada)
    db.commit()

