import pandas as pd
import sqlite3

def importar_dados():

    csv_path = "data/microdados_ed_basica_2024.csv"

   
    uf_nordeste = [21, 22, 23, 24, 25, 26, 27, 28, 29]

  
    colunas = [
        "CO_ENTIDADE", "NO_ENTIDADE", "CO_UF", "CO_MUNICIPIO",
        "QT_MAT_BAS", "QT_MAT_INF", "QT_MAT_FUND", "QT_MAT_MED",
        "QT_MAT_PROF", "QT_MAT_EJA", "QT_MAT_ESP"
    ]

    chunksize = 1000

    conn = sqlite3.connect("censo.db")

    for i, chunk in enumerate(pd.read_csv(
        csv_path,
        sep=';',
        encoding='latin-1',
        usecols=colunas,
        chunksize=chunksize
    )):
      

        
        chunk_ne = chunk[chunk["CO_UF"].isin(uf_nordeste)]

        if not chunk_ne.empty:
            chunk_ne.to_sql("escolas", conn, if_exists="append", index=False)
            print(f"Chunk {i+1}: {len(chunk_ne)} registros inseridos.")

    conn.close()
    
if __name__ == "__main__":
    importar_dados()
