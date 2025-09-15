from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

# Configurações do banco Firebird
HOST = "25.90.252.41"
USERNAME = "SYSDBA"
PASSWORD = "masterkey"
DATABASE_PATH = "C:/caminho/para/seu/banco.FDB"  # Ajuste para o caminho correto

# String de conexão SQLAlchemy com Firebird
# OBS: Para usar no Render, é recomendável trocar para sqlalchemy-firebird
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


# Função genérica para buscar NRRQU em qualquer tabela
def fetch_nrrqu(table_name: str, nrrqu: int | None = None):
    try:
        with engine.connect() as conn:
            if nrrqu is not None:
                query = text(f"SELECT NRRQU FROM {table_name} WHERE NRRQU = :nrrqu")
                result = conn.execute(query, {"nrrqu": nrrqu})
            else:
                query = text(f"SELECT NRRQU FROM {table_name}")
                result = conn.execute(query)

            dados = [row[0] for row in result.fetchall()]
        return dados
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoints das tabelas solicitadas
@app.get("/fc12000")
def get_fc12000(nrrqu: int | None = Query(None)):
    return {"FC12000": fetch_nrrqu("FC12000", nrrqu)}

@app.get("/fc12001")
def get_fc12001(nrrqu: int | None = Query(None)):
    return {"FC12001": fetch_nrrqu("FC12001", nrrqu)}

@app.get("/fc12110")
def get_fc12110(nrrqu: int | None = Query(None)):
    return {"FC12110": fetch_nrrqu("FC12110", nrrqu)}

@app.get("/fc12111")
def get_fc12111(nrrqu: int | None = Query(None)):
    return {"FC12111": fetch_nrrqu("FC12111", nrrqu)}

@app.get("/fc12300")
def get_fc12300(nrrqu: int | None = Query(None)):
    return {"FC12300": fetch_nrrqu("FC12300", nrrqu)}


# Rodar no Render (porta dinâmica)
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
