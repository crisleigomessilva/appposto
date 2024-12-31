from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_session
from app.models.usuario import Usuario
from pydantic import BaseModel
from app.core.security import hash_password
from datetime import datetime


router = APIRouter()

# Esquemas para validação de dados
class UsuarioCreate(BaseModel):
    nome: str
    email: str
    senha: str

class UsuarioUpdate(BaseModel):
    nome: str = None
    email: str = None
    senha: str = None

class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: str

    class Config:
        from_attributes = True


# Rotas para gerenciar usuários
@router.post("/", response_model=UsuarioResponse)
def criar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_session)):
    # Verifica se o e-mail já está em uso
    if db.query(Usuario).filter(Usuario.email == usuario.email).first():
        raise HTTPException(status_code=400, detail="Email já está em uso")

    # Gera o hash da senha antes de salvar
    senha_hash = hash_password(usuario.senha)

    # Cria o registro inicial
    novo_usuario = Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha=senha_hash,
        data_inclusao=datetime.utcnow(),
        data_alteracao=datetime.utcnow(),
    )
    db.add(novo_usuario)
    db.commit()  # O ID será gerado pelo banco após este commit
    db.refresh(novo_usuario)  # Atualiza o objeto com o ID gerado pelo banco

    # Calcula o id_md5 com base no ID gerado, email e senha
    novo_usuario.id_md5 = Usuario.gerar_id_md5(
        id=novo_usuario.id,
        email=novo_usuario.email,
        senha=novo_usuario.senha,
    )
    db.add(novo_usuario)  # Atualiza o registro com o id_md5
    db.commit()
    db.refresh(novo_usuario)

    return novo_usuario


@router.get("/{usuario_id}", response_model=UsuarioResponse)
def obter_usuario(usuario_id: int, db: Session = Depends(get_session)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario


@router.get("/", response_model=List[UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_session)):
    return db.query(Usuario).all()


@router.put("/{usuario_id}", response_model=UsuarioResponse)
def atualizar_usuario(
    usuario_id: int, usuario: UsuarioUpdate, db: Session = Depends(get_session)
):
    # Busca o usuário no banco de dados
    usuario_db = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Atualiza os campos fornecidos
    if usuario.nome:
        usuario_db.nome = usuario.nome

    if usuario.email:
        # Verifica se o e-mail já está em uso por outro usuário
        email_existente = db.query(Usuario).filter(
            Usuario.email == usuario.email, Usuario.id != usuario_id
        ).first()
        if email_existente:
            raise HTTPException(status_code=400, detail="Email já está em uso")
        usuario_db.email = usuario.email

    if usuario.senha:
        # Criptografa a nova senha antes de atualizar
        senha_hash = hash_password(usuario.senha)
        usuario_db.senha = senha_hash

    # Recalcula o ID MD5 (caso email ou senha tenham sido alterados)
    usuario_db.id_md5 = Usuario.gerar_id_md5(usuario_db.id, usuario_db.email, usuario_db.senha)

    # Salva as alterações no banco de dados
    db.commit()
    db.refresh(usuario_db)
    return usuario_db
