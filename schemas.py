

from marshmallow import Schema, fields, validate

class MicrodadoSchema(Schema):
    """
    Schema para validação de dados (POST) e serialização (GET) do Microdado.
    """
    id = fields.Int(dump_only=True)
    
    co_entidade = fields.String(validate=validate.Length(min=1, max=10), required=True, 
                                error_messages={"required": "O Código da Entidade é obrigatório."})
    no_entidade = fields.String(validate=validate.Length(min=3, max=255), required=True,
                                error_messages={"required": "O Nome da Entidade é obrigatório."})
    nu_ano_censo = fields.Int(validate=validate.Range(min=2000), required=True,
                              error_messages={"required": "O Ano do Censo é obrigatório."})
    
    qt_mat_total = fields.Int(validate=validate.Range(min=0), required=True,
                              error_messages={"required": "O total de matrículas é obrigatório."})
    
    co_regiao = fields.Int(allow_none=True)
    no_regiao = fields.String(allow_none=True)
    co_uf = fields.Int(allow_none=True)
    sg_uf = fields.String(allow_none=True)
    no_uf = fields.String(allow_none=True)
    co_municipio = fields.Int(allow_none=True)
    no_municipio = fields.String(allow_none=True)
    co_mesorregiao = fields.Int(allow_none=True)
    no_mesorregiao = fields.String(allow_none=True)
    co_microrregiao = fields.Int(allow_none=True)
    no_microrregiao = fields.String(allow_none=True)
    
    qt_mat_bas = fields.Int(validate=validate.Range(min=0), allow_none=True)
    qt_mat_prof = fields.Int(validate=validate.Range(min=0), allow_none=True)
    qt_mat_eja = fields.Int(validate=validate.Range(min=0), allow_none=True)
    qt_mat_esp = fields.Int(validate=validate.Range(min=0), allow_none=True)
    qt_mat_fund = fields.Int(validate=validate.Range(min=0), allow_none=True)
    qt_mat_inf = fields.Int(validate=validate.Range(min=0), allow_none=True)
    qt_mat_med = fields.Int(validate=validate.Range(min=0), allow_none=True)
    qt_mat_zr_na = fields.Int(validate=validate.Range(min=0), allow_none=True)
    qt_mat_zr_rur = fields.Int(validate=validate.Range(min=0), allow_none=True)
    qt_mat_zr_urb = fields.Int(validate=validate.Range(min=0), allow_none=True)