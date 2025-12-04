# carga.py

import os
import pandas as pd
from app import create_app # Importa a função de criação do app
from models import db, Microdado
from sqlalchemy.exc import SQLAlchemyError
from utils.log import setup_logger # Importa o logger

logger = setup_logger('carga_dados')

# Colunas que serão lidas do CSV e carregadas no banco
COLUNAS_INTERESSE = [
    'NU_ANO_CENSO', 'CO_ENTIDADE', 'NO_ENTIDADE', 
    'CO_REGIAO', 'NO_REGIAO', 'CO_UF', 'SG_UF', 'NO_UF', 'CO_MUNICIPIO', 'NO_MUNICIPIO', 
    'CO_MESORREGIAO', 'NO_MESORREGIAO', 'CO_MICRORREGIAO', 'NO_MICRORREGIAO',
    'QT_MAT_BAS', 'QT_MAT_PROF', 'QT_MAT_EJA', 'QT_MAT_ESP', 'QT_MAT_FUND', 
    'QT_MAT_INF', 'QT_MAT_MED', 'QT_MAT_ZR_NA', 'QT_MAT_ZR_RUR', 'QT_MAT_ZR_URB'
]

# Colunas de matrícula para cálculo de QT_MAT_TOTAL
COLUNAS_MATRICULA = [
    'QT_MAT_BAS', 'QT_MAT_PROF', 'QT_MAT_EJA', 'QT_MAT_ESP', 'QT_MAT_FUND', 
    'QT_MAT_INF', 'QT_MAT_MED', 'QT_MAT_ZR_NA', 'QT_MAT_ZR_RUR', 'QT_MAT_ZR_URB'
]

def carregar_dados_censo(ano):
    """Carrega e processa os microdados de um ano específico para todo o Brasil."""
    
    # Define o caminho do arquivo CSV na pasta data/
    caminho_arquivo = os.path.join(
        os.path.dirname(__file__), 
        'data', 
        f'microdados_ed_basica_{ano}.csv'
    )
    
    if not os.path.exists(caminho_arquivo):
        logger.error(f"Arquivo não encontrado: {caminho_arquivo}")
        return
        
    logger.info(f"Iniciando leitura do arquivo: {caminho_arquivo}")

    try:
        # Define os tipos de dados para evitar conversões indesejadas
        custom_dtypes = {
            # CO_ENTIDADE deve ser string para evitar perda de precisão em códigos longos
            'CO_ENTIDADE': 'str',
            # Colunas de Matrícula (Contagens)
            **{col: 'Int64' for col in COLUNAS_MATRICULA},
            # Outros códigos numéricos
            'NU_ANO_CENSO': 'Int64', 'CO_REGIAO': 'Int64', 'CO_UF': 'Int64', 
            'CO_MUNICIPIO': 'Int64', 'CO_MESORREGIAO': 'Int64', 'CO_MICRORREGIAO': 'Int64'
        }

        # Leitura inicial das colunas necessárias
        df = pd.read_csv(
            caminho_arquivo, 
            sep=';', # <--- CORREÇÃO CRÍTICA DO DELIMITADOR
            encoding='latin1', 
            usecols=COLUNAS_INTERESSE, 
            dtype=custom_dtypes, 
            low_memory=False
        )
        
        # 1. Agrupamento por Instituição de Ensino (IE) para somar matrículas
        # O CO_ENTIDADE e o NU_ANO_CENSO formam a chave para a agregação
        df_agrupado = df.groupby(['CO_ENTIDADE', 'NU_ANO_CENSO']).agg({
            col: 'sum' for col in COLUNAS_MATRICULA
        }).reset_index()
        
        # 2. Re-adquirir dados de identificação e geográficos (usando drop_duplicates)
        cols_id_geo = [col for col in COLUNAS_INTERESSE if col not in COLUNAS_MATRICULA]
        df_geo = df.drop_duplicates(subset=['CO_ENTIDADE', 'NU_ANO_CENSO'])[cols_id_geo]
        
        # Merge e tratamento de NaNs
        df_final = pd.merge(
            df_agrupado, 
            df_geo, 
            on=['CO_ENTIDADE', 'NU_ANO_CENSO'], 
            how='left'
        ).fillna(0) 

        # 3. Cálculo do campo qt_mat_total (REQUISITO: computado na carga)
        # Converte as colunas de matrícula para tipo numérico antes da soma, 
        # forçando NaNs a 0 se o fillna(0) acima não foi suficiente.
        for col in COLUNAS_MATRICULA:
            df_final[col] = pd.to_numeric(df_final[col], errors='coerce').fillna(0).astype(int)

        df_final['QT_MAT_TOTAL'] = df_final[COLUNAS_MATRICULA].sum(axis=1)

        # 4. Preparação e inserção no banco de dados
        # Renomeia as colunas do DataFrame para minúsculas (padrão do modelo DB)
        df_final.columns = [c.lower() for c in df_final.columns]
        
        logger.info(f"Iniciando inserção de {len(df_final)} IEs no banco de dados para o ano {ano}...")
        
        objetos_microdado = []
        cols_modelo = [c.key for c in Microdado.__table__.columns if c.key != 'id']

        for _, row in df_final.iterrows():
            data_dict = row.to_dict()
            objeto_data = {col: data_dict.get(col) for col in cols_modelo}
            objetos_microdado.append(Microdado(**objeto_data))

        db.session.bulk_save_objects(objetos_microdado)
        db.session.commit()
        logger.info(f"Dados do ano {ano} inseridos com sucesso!")

    except SQLAlchemyError as e:
        logger.error(f"Erro de banco de dados ao carregar dados do ano {ano}: {e}", exc_info=True)
        db.session.rollback()
    except Exception as e:
        logger.error(f"Erro geral ao carregar dados do ano {ano}: {e}", exc_info=True)
        db.session.rollback()

if __name__ == '__main__':
    app = create_app() 
    with app.app_context():
        # Limpa e recria as tabelas para garantir o novo schema
        db.drop_all()
        db.create_all()
        logger.info("Tabelas recriadas no banco de dados.")

        anos = [2022, 2023, 2024]
        for ano in anos:
            carregar_dados_censo(ano)

        logger.info("Processo de carga de dados finalizado.")