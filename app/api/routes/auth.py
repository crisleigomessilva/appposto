from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import verify_password, create_access_token
from app.core.database import get_session
from app.models.usuario import Usuario
from datetime import timedelta



router = APIRouter()

@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_session)):
    """
    Realiza o login no sistema verificando email e senha e retorna um token JWT.
    Args:
        email (str): Email do usuário.
        password (str): Senha do usuário.
        db (Session): Sessão do banco de dados.
    Returns:
        dict: Token JWT gerado.
    """
    # Busca o usuário pelo email
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verifica a senha
    if not verify_password(password, usuario.senha):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Gera o token de acesso
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": usuario.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
