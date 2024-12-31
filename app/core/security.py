from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.core.config import settings

# Configura o contexto de hashing para usar bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configurações do JWT
SECRET_KEY = "sua_chave_secreta_super_segura"  # Substitua por uma chave segura
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password: str) -> str:
    """
    Gera o hash de uma senha em texto puro.
    Args:
        password (str): Senha em texto plano.
    Returns:
        str: Hash da senha.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se uma senha em texto puro corresponde ao hash armazenado.
    Args:
        plain_password (str): Senha em texto plano.
        hashed_password (str): Hash da senha armazenado.
    Returns:
        bool: True se a senha corresponder, False caso contrário.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Gera um token JWT para acesso.
    Args:
        data (dict): Dados a serem incluídos no token.
        expires_delta (timedelta, optional): Tempo de expiração do token. Default: None.
    Returns:
        str: Token JWT gerado.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
