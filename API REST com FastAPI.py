# ===============================
# MEU PROJETO COMPLETO - DESAFIOS DIO
# ===============================

# Importações necessárias
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from fastapi_pagination import Page, add_pagination, paginate
from pydantic import BaseModel

# ------------------------------
# CONFIGURAÇÃO DO BANCO DE DADOS
# ------------------------------
DATABASE_URL = "sqlite:///./workout.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------------------
# DESAFIO 1 - CLASSE MENSAGEM
# ------------------------------
class Mensagem:
    def __init__(self, remetente: str, conteudo: str):
        self.remetente = remetente
        self.conteudo = conteudo

    def exibir(self) -> str:
        return f"{self.remetente}: {self.conteudo}"

# ------------------------------
# DESAFIO 2 - CLASSE ROBO
# ------------------------------
class Robo:
    def __init__(self, modelo1: str, modelo2: str):
        self.modelo1 = modelo1
        self.modelo2 = modelo2

    def nome_completo(self) -> str:
        return f"{self.modelo1}-{self.modelo2}"

# ------------------------------
# DESAFIO 3 - IDENTIFICAR CATEGORIA DE GADGET
# ------------------------------
def identificar_categoria(codigo: str) -> str:
    if codigo.startswith("T"):
        return "tablet"
    elif codigo.startswith("P"):
        return "phone"
    elif codigo.startswith("N"):
        return "notebook"
    else:
        return "unknown"

# ------------------------------
# DESAFIO 4 - WORKOUT API COM FASTAPI
# ------------------------------

# Modelos SQLAlchemy
class Atleta(Base):
    __tablename__ = "atletas"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    cpf = Column(String, unique=True, nullable=False)
    centro_treinamento = Column(String, nullable=False)
    categoria = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)

# Schemas Pydantic
class AtletaCreate(BaseModel):
    nome: str
    cpf: str
    centro_treinamento: str
    categoria: str

class AtletaResponse(BaseModel):
    nome: str
    centro_treinamento: str
    categoria: str

# CRUD
def criar_atleta(db: Session, atleta: AtletaCreate):
    novo = Atleta(**atleta.dict())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

def listar_atletas(db: Session, nome: str = None, cpf: str = None):
    query = db.query(Atleta)
    if nome:
        query = query.filter(Atleta.nome.contains(nome))
    if cpf:
        query = query.filter(Atleta.cpf == cpf)
    return query.all()

# FastAPI
app = FastAPI(title="Projeto Completo DIO")

@app.post("/atletas", status_code=201)
def endpoint_criar_atleta(atleta: AtletaCreate, db: Session = Depends(get_db)):
    try:
        return criar_atleta(db, atleta)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=303,
            detail=f"Já existe um atleta cadastrado com o cpf: {atleta.cpf}"
        )

@app.get("/atletas", response_model=Page[AtletaResponse])
def endpoint_listar_atletas(
    nome: str | None = Query(default=None),
    cpf: str | None = Query(default=None),
    db: Session = Depends(get_db)
):
    atletas = listar_atletas(db, nome, cpf)
    resposta = [
        {
            "nome": a.nome,
            "centro_treinamento": a.centro_treinamento,
            "categoria": a.categoria
        } for a in atletas
    ]
    return paginate(resposta)

add_pagination(app)

# ------------------------------
# EXEMPLOS DE TESTE DE CLASSES
# ------------------------------
if __name__ == "__main__":
    # Testando Mensagem
    msg = Mensagem("Maria", "Bom dia equipe")
    print(msg.exibir())  # Maria: Bom dia equipe

    # Testando Robo
    robo = Robo("nano", "chip")
    print(robo.nome_completo())  # nano-chip

    # Testando Identificar Gadget
    print(identificar_categoria("T12345"))  # tablet
    print(identificar_categoria("P987"))    # phone
    print(identificar_categoria("X999"))    # unknown

    # Para testar a API: uvicorn main:app --reload
