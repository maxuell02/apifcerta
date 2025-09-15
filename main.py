from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configurações do banco Firebird
DATABASE_PATH = "D:\\sistemas\\fcerta\\DB\\ALTERDB.ib"
HOST = "25.90.252.41"
USERNAME = "SYSDBA"
PASSWORD = "masterkey"

# String de conexão SQLAlchemy com Firebird
DATABASE_URL = f"firebird+fdb://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE_PATH}"

# Criando conexão
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Inicializa FastAPI
app = FastAPI(title="API Firebird - FCerta")

# Habilitar CORS (para frontend na Lovable)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ideal restringir para o domínio do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependência para pegar sessão
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Rota teste
@app.get("/")
def root():
    return {"status": "API rodando com sucesso!"}


# Exemplo: Listar registros de uma tabela
@app.get("/clientes")
def get_clientes():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT ID, NOME, EMAIL FROM CLIENTES"))
            clientes = [dict(row._mapping) for row in result.fetchall()]
        return {"clientes": clientes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Exemplo: Inserir cliente
@app.post("/clientes")
def add_cliente(nome: str, email: str):
    try:
        with engine.begin() as conn:
            conn.execute(
                text("INSERT INTO CLIENTES (NOME, EMAIL) VALUES (:nome, :email)"),
                {"nome": nome, "email": email},
            )
        return {"message": "Cliente adicionado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

import os

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # Render vai injetar a porta
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
