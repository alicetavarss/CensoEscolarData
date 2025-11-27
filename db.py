import sqlite3
import pandas as pd
import os

# --- Configurações de Arquivos ---
DATABASE = 'censo.db'
CSV_FILE_PATH = 'data/microdados_ed_basica_2024.csv'
SCHEMA_FILE_PATH = 'schema.sql' # NOVO: Caminho para o seu arquivo SQL

# Parâmetros de Leitura do CSV (conforme a sua atividade anterior)
CSV_DELIMITER = ';' 
CSV_ENCODING = 'latin-1' 
CHUNK_SIZE = 50000 
# --------------------------------

def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados SQLite."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Cria as tabelas lendo o schema.sql."""
    if not os.path.exists(SCHEMA_FILE_PATH):
        print(f"❌ Erro: Arquivo de schema '{SCHEMA_FILE_PATH}' não encontrado. Certifique-se de que ele está na raiz do projeto.")
        return
        
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Lendo e executando o seu arquivo schema.sql
        with open(SCHEMA_FILE_PATH, "r", encoding="utf-8") as f:
            cursor.executescript(f.read())
        conn.commit()
        print("✅ Tabelas criadas a partir do schema.sql.")
    except Exception as e:
        print(f"❌ Erro ao executar schema.sql: {e}")
    finally:
        conn.close()

def load_initial_data():
    """Carrega dados do CSV usando Pandas, filtrando a região Nordeste."""

    if not os.path.exists(CSV_FILE_PATH):
        print(f"❌ Erro: Arquivo CSV '{CSV_FILE_PATH}' não encontrado. Pulando carregamento.")
        return

    print("Carregando dados do Nordeste para o SQLite usando Pandas Chunking...")
    
    # Parâmetros de Filtragem e Colunas (conforme a sua atividade anterior)
    uf_nordeste = [21, 22, 23, 24, 25, 26, 27, 28, 29]
    colunas = [
        "CO_ENTIDADE", "NO_ENTIDADE", "CO_UF", "CO_MUNICIPIO",
        "QT_MAT_BAS", "QT_MAT_INF", "QT_MAT_FUND", "QT_MAT_MED",
        "QT_MAT_PROF", "QT_MAT_EJA", "QT_MAT_ESP"
    ]

    try:
        conn = get_db_connection()
        total_rows_inserted = 0

        # Leitura paginada (chunking)
        chunk_iterator = pd.read_csv(
            CSV_FILE_PATH,
            sep=CSV_DELIMITER,
            encoding=CSV_ENCODING,
            usecols=colunas,
            chunksize=CHUNK_SIZE,
            low_memory=False
        )
        
        for i, chunk in enumerate(chunk_iterator):
            # 1. Filtragem da Região Nordeste
            chunk_ne = chunk[chunk["CO_UF"].isin(uf_nordeste)]

            if not chunk_ne.empty:
                # 2. Inserção no SQLite (append)
                chunk_ne.to_sql("escolas", conn, if_exists="append", index=False)
                total_rows_inserted += len(chunk_ne)
                
        conn.close()
        print(f"✅ Carregamento concluído. Total de {total_rows_inserted} registros do Nordeste inseridos.")

    except Exception as e:
        print(f"❌ Erro fatal ao carregar dados do CSV com Pandas: {e}")