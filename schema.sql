-- Garante que as tabelas antigas sejam removidas antes de criar as novas
DROP TABLE IF EXISTS tb_usuario;
DROP TABLE IF EXISTS escolas;

-- 1. Criação da Tabela de Usuários (tb_usuario)
CREATE TABLE tb_usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cpf TEXT UNIQUE NOT NULL,       -- CPF deve ser único para cada usuário
    nascimento DATE NOT NULL
);

-- 2. Criação da Tabela de Escolas (mantida como solicitado)
CREATE TABLE escolas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    CO_ENTIDADE INTEGER,
    NO_ENTIDADE TEXT,
    CO_UF INTEGER,
    CO_MUNICIPIO INTEGER,
    QT_MAT_BAS INTEGER,
    QT_MAT_INF INTEGER,
    QT_MAT_FUND INTEGER,
    QT_MAT_MED INTEGER,
    QT_MAT_PROF INTEGER,
    QT_MAT_EJA INTEGER,
    QT_MAT_ESP INTEGER
);
