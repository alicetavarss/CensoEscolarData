from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Microdado(db.Model):
    __tablename__ = 'microdados_censo'
    
    id = db.Column(db.Integer, primary_key=True)
    
    co_entidade = db.Column(db.String(10), nullable=False, index=True)
    no_entidade = db.Column(db.String(255), nullable=False)
    nu_ano_censo = db.Column(db.Integer, nullable=False, index=True)
    
    co_regiao = db.Column(db.Integer)
    no_regiao = db.Column(db.String(50))
    co_uf = db.Column(db.Integer)
    sg_uf = db.Column(db.String(2))
    no_uf = db.Column(db.String(50))
    co_municipio = db.Column(db.Integer)
    no_municipio = db.Column(db.String(255))
    co_mesorregiao = db.Column(db.Integer)
    no_mesorregiao = db.Column(db.String(255))
    co_microrregiao = db.Column(db.Integer)
    no_microrregiao = db.Column(db.String(255))
    
    # Colunas de Matrículas (Contagem Agrupada)
    qt_mat_bas = db.Column(db.Integer)
    qt_mat_prof = db.Column(db.Integer)
    qt_mat_eja = db.Column(db.Integer)
    qt_mat_esp = db.Column(db.Integer)
    qt_mat_fund = db.Column(db.Integer)
    qt_mat_inf = db.Column(db.Integer)
    qt_mat_med = db.Column(db.Integer)
    qt_mat_zr_na = db.Column(db.Integer)
    qt_mat_zr_rur = db.Column(db.Integer)
    qt_mat_zr_urb = db.Column(db.Integer)
    
    qt_mat_total = db.Column(db.Integer, index=True)

    def to_dict(self):
        return {
            'no_entidade': self.no_entidade,
            'co_entidade': self.co_entidade,
            'no_uf': self.no_uf,
            'sg_uf': self.sg_uf,
            'co_uf': self.co_uf,
            'no_municipio': self.no_municipio,
            'co_municipio': self.co_municipio,
            'no_mesorregiao': self.no_mesorregiao,
            'co_mesorregiao': self.co_mesorregiao,
            'no_microrregiao': self.no_microrregiao,
            'co_microrregiao': self.co_microrregiao,
            'nu_ano_censo': self.nu_ano_censo,
            'no_regiao': self.no_regiao,
            'co_regiao': self.co_regiao,
            'qt_mat_bas': self.qt_mat_bas,
            'qt_mat_prof': self.qt_mat_prof,
            'qt_mat_eja': self.qt_mat_eja,
            'qt_mat_esp': self.qt_mat_esp,
            'qt_mat_fund': self.qt_mat_fund,
            'qt_mat_inf': self.qt_mat_inf,
            'qt_mat_med': self.qt_mat_med,
            'qt_mat_zr_na': self.qt_mat_zr_na,
            'qt_mat_zr_rur': self.qt_mat_zr_rur,
            'qt_mat_zr_urb': self.qt_mat_zr_urb,
            'qt_mat_total': self.qt_mat_total,
          
        }