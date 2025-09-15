from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Union, List
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
import os

# ------------------------------
# Configurações do banco Firebird via variáveis de ambiente
# ------------------------------
HOST = os.getenv("FIREBIRD_HOST", "localhost")
USERNAME = os.getenv("FIREBIRD_USER", "SYSDBA")
PASSWORD = os.getenv("FIREBIRD_PASSWORD", "masterkey")
DATABASE_PATH = os.getenv("FIREBIRD_DB", "/app/ALTERDB.fdb")  # ajuste o caminho real

# ⚠️ Use firebird+fdb:// (precisa de sqlalchemy-firebird + fdb instalados)
DATABASE_URL = f"firebird+fdb://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE_PATH}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ------------------------------
# Inicializa FastAPI
# ------------------------------
app = FastAPI(title="API Firebird - FCerta")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 🔒 ideal restringir no futuro
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------
# Modelos Pydantic
# ------------------------------
class FilterItem(BaseModel):
    column: str
    op: str  # '=', '!=', '>', '<', '>=', '<=', 'LIKE', 'IN'
    value: Union[Any, List[Any]]

class FilterGroup(BaseModel):
    logic: str = "AND"  # "AND" ou "OR"
    filters: List[Union["FilterItem", "FilterGroup"]]

FilterGroup.update_forward_refs()

class TableQuery(BaseModel):
    filter_group: FilterGroup | None = None
    limit: int = 100
    offset: int = 0

# ------------------------------
# Rotas básicas
# ------------------------------
@app.get("/")
def root():
    return {"status": "API rodando com sucesso no Render!"}

@app.get("/tables")
def list_tables():
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        return {"tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar tabelas: {e}")

# ------------------------------
# Função recursiva para montar WHERE dinâmico
# ------------------------------
def build_where(group: FilterGroup, params: dict, param_counter: list):
    clauses = []
    for f in group.filters:
        if isinstance(f, FilterGroup):
            sub_clause = build_where(f, params, param_counter)
            clauses.append(f"({sub_clause})")
        else:
            param_name = f"p{param_counter[0]}"
            op = f.op.upper()
            param_counter[0] += 1

            if op == "IN":
                if not isinstance(f.value, list):
                    raise HTTPException(status_code=400, detail="O operador IN requer uma lista")
                placeholders = ", ".join([f":{param_name}_{i}" for i in range(len(f.value))])
                clauses.append(f"{f.column} IN ({placeholders})")
                for i, v in enumerate(f.value):
                    params[f"{param_name}_{i}"] = v
            elif op == "LIKE":
                clauses.append(f"{f.column} LIKE :{param_name}")
                params[param_name] = f.value
            elif op in ("=", "!=", ">", "<", ">=", "<="):
                clauses.append(f"{f.column} {op} :{param_name}")
                params[param_name] = f.value
            else:
                raise HTTPException(status_code=400, detail=f"Operador inválido: {f.op}")

    return f" {group.logic.upper()} ".join(clauses)

# ------------------------------
# Endpoint genérico para consultar tabelas
# ------------------------------
@app.post("/table/{table_name}")
def fetch_table_data(table_name: str, query: TableQuery):
    try:
        with engine.connect() as conn:
            params = {}
            where_sql = ""
            if query.filter_group:
                where_sql = "WHERE " + build_where(query.filter_group, params, [0])

            # Firebird usa ROWS <start> TO <end> para paginação
            start_row = query.offset + 1
            end_row = query.offset + query.limit
            query_sql = f"SELECT * FROM {table_name} {where_sql} ROWS {start_row} TO {end_row}"

            result = conn.execute(text(query_sql), params)
            dados = [dict(row._mapping) for row in result.fetchall()]  # compatível SQLAlchemy 2.x

        return {"table": table_name, "data": dados, "count": len(dados)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na consulta: {e}")
