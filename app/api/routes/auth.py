from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.core.security import verify_password, create_access_token
from app.core.database import get_session
from app.models.usuario import Usuario
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.core.config import settings



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


def autenticar_usuario(email: str, password: str, db: Session) -> Usuario:
    """
    Verifica as credenciais do usuário e retorna o objeto do usuário autenticado.

    Args:
        email (str): Email do usuário.
        password (str): Senha do usuário.
        db (Session): Sessão do banco de dados.

    Returns:
        Usuario: Objeto do usuário autenticado.
    """
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(password, usuario.senha):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Opcional: Verifique se o usuário está ativo
    if not getattr(usuario, "is_active", True):  # Exemplo: campo 'is_active' no modelo
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo. Entre em contato com o administrador.",
        )

    return usuario


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
    # Autentica o usuário
    usuario = autenticar_usuario(request.email, request.password, db)

    # Gera o token de acesso
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": usuario.email, "id_md5": usuario.id_md5}, expires_delta=access_token_expires
    )

    # Retorna o token com informações adicionais
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 30 * 60,  # Tempo de expiração em segundos
        "user_name": usuario.nome,
        "user_email": usuario.email,
    }


# Configuração do OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)) -> Usuario:
    """
    Valida o token JWT e retorna o usuário autenticado.

    Args:
        token (str): Token JWT fornecido na requisição.
        db (Session): Sessão do banco de dados.

    Returns:
        Usuario: Objeto do usuário autenticado.

    Raises:
        HTTPException: Se o token for inválido ou o usuário não for encontrado.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        usuario = db.query(Usuario).filter(Usuario.email == email).first()
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return usuario
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )