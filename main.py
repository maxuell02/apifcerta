from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
import os

# Configurações do banco Firebird
HOST = "25.90.252.41"
USERNAME = "SYSDBA"
PASSWORD = "masterkey"
DATABASE_PATH = "D:\\sistemas\\fcerta\\DB\\ALTERDB.ib"

DATABASE_URL = f"firebird+fdb://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE_PATH}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI(title="API Firebird - FCerta")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- Modelos para filtros lógicos -----
class FilterItem(BaseModel):
    column: str
    op: str  # '=', '!=', '>', '<', '>=', '<=', 'LIKE', 'IN'
    value: any  # valor ou lista de valores (para IN)

class FilterGroup(BaseModel):
    logic: str = "AND"  # "AND" ou "OR"
    filters: list[FilterItem] | list["FilterGroup"]  # pode ter subgrupos

FilterGroup.update_forward_refs()

class TableQuery(BaseModel):
    filter_group: FilterGroup | None = None
    limit: int = 100
    offset: int = 0

# ----- Rotas -----
@app.get("/")
def root():
    return {"status": "API rodando com sucesso!"}

@app.get("/tables")
def list_tables():
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        return {"tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Função para construir WHERE recursivamente
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
                    raise HTTPException(status_code=400, detail="IN deve receber uma lista")
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

@app.post("/table/{table_name}")
def fetch_table_data(table_name: str, query: TableQuery):
    try:
        with engine.connect() as conn:
            params = {}
            where_sql = ""
            if query.filter_group:
                where_sql = "WHERE " + build_where(query.filter_group, params, [0])
            
            query_sql = f"SELECT * FROM {table_name} {where_sql} ROWS {query.offset + 1} TO {query.offset + query.limit}"

            result = conn.execute(text(query_sql), params)
            dados = [dict(row) for row in result.fetchall()]

        return {"table": table_name, "data": dados, "count": len(dados)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
