

DROP TABLE IF EXISTS microdados_censo;

CREATE TABLE microdados_censo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    co_entidade VARCHAR(10) NOT NULL,
    no_entidade VARCHAR(255) NOT NULL,
    nu_ano_censo INTEGER NOT NULL,
    
    co_regiao INTEGER,
    no_regiao VARCHAR(50),
    co_uf INTEGER,
    sg_uf VARCHAR(2),
    no_uf VARCHAR(50),
    co_municipio INTEGER,
    no_municipio VARCHAR(255),
    co_mesorregiao INTEGER,
    no_mesorregiao VARCHAR(255),
    co_microrregiao INTEGER,
    no_microrregiao VARCHAR(255),
    
    qt_mat_bas INTEGER,
    qt_mat_prof INTEGER,
    qt_mat_eja INTEGER,
    qt_mat_esp INTEGER,
    qt_mat_fund INTEGER,
    qt_mat_inf INTEGER,
    qt_mat_med INTEGER,
    qt_mat_zr_na INTEGER,
    qt_mat_zr_rur INTEGER,
    qt_mat_zr_urb INTEGER,
    
    qt_mat_total INTEGER
);

CREATE INDEX idx_co_entidade ON microdados_censo (co_entidade);
CREATE INDEX idx_nu_ano_censo ON microdados_censo (nu_ano_censo);
CREATE INDEX idx_qt_mat_total ON microdados_censo (qt_mat_total);