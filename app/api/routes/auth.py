from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.core.security import verify_password, create_access_token
from app.core.database import get_session
from app.models.usuario import Usuario
from datetime import timedelta

router = APIRouter()

# Schemas para entrada e saída
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_name: str
    user_email: EmailStr


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_session)):
    """
    Realiza o login no sistema verificando email e senha e retorna um token JWT.
    Args:
        request (LoginRequest): Dados de login do usuário.
        db (Session): Sessão do banco de dados.
    Returns:
        LoginResponse: Token JWT gerado, informações adicionais e detalhes do usuário.
    """
    # Busca o usuário pelo email
    usuario = db.query(Usuario).filter(Usuario.email == request.email).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verifica a senha
    if not verify_password(request.password, usuario.senha):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Gera o token de acesso
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": usuario.email}, expires_delta=access_token_expires
    )

    # Retorna o token com informações adicionais
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 30 * 60,  # Tempo de expiração em segundos
        "user_name": usuario.nome,
        "user_email": usuario.email,
    }
