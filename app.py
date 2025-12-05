# app.py

import os
from flask import Flask, jsonify, request
from sqlalchemy import desc
from models import db, Microdado 
from utils.log import setup_logger 
from marshmallow import ValidationError
from marshmallow import Schema as MarshmallowSchema 

from schemas import MicrodadoSchema 

logger = setup_logger('app_api')
ma = MarshmallowSchema() 

def create_app():
    app = Flask(__name__)
    
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'censo_escolar.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app) 
    
    return app

app = create_app()


@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "API Censo Escolar operacional."})


@app.route('/instituicoesensino/ranking/<int:ano>', methods=['GET'])
def ranking_instituicoes(ano):
   
    try:
        
        if ano not in [2022, 2023, 2024]:
            logger.warning(f"Tentativa de acesso com ano inválido: {ano}")
            return jsonify({
                "erro": "Ano inválido", 
                "mensagem": "O ano deve ser 2022, 2023 ou 2024."
            }), 400

        logger.info(f"Requisitando ranking para o ano: {ano}")

        ranking_data = db.session.execute(
            db.select(Microdado)
            .filter_by(nu_ano_censo=ano)
            .order_by(desc(Microdado.qt_mat_total))
            .limit(10)
        ).scalars().all()

        
        if not ranking_data:
            logger.info(f"Nenhum dado de ranking encontrado para o ano {ano}.")
            return jsonify([]), 200

        ranking_list = []
        for i, ie in enumerate(ranking_data):
            
            ie_dict = ie.to_dict() 
            
            ie_dict['nu_ranking'] = i + 1
            ranking_list.append(ie_dict)
        
        logger.info(f"Ranking para o ano {ano} retornado com sucesso.")
        return jsonify(ranking_list)

    except Exception as e:
        logger.error(f"Erro crítico ao processar ranking para o ano {ano}: {e}", exc_info=True)
        return jsonify({
            "erro": "Erro interno do servidor", 
            "mensagem": "Não foi possível gerar o ranking devido a um erro no servidor."
        }), 500

@app.route('/microdados', methods=['POST'])
def criar_microdado():
    schema = MicrodadoSchema()
    try:
        dados_validados = schema.load(request.json)
    except ValidationError as err:
        logger.warning(f"Tentativa de inserção com dados inválidos: {err.messages}")
        
        return jsonify({"erro": "Dados inválidos", "detalhes": err.messages}), 400

    try:
        novo_microdado = Microdado(**dados_validados)
        db.session.add(novo_microdado)
        db.session.commit()
        
        logger.info(f"Novo microdado criado: {novo_microdado.co_entidade}")
        return jsonify(schema.dump(novo_microdado)), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao salvar novo microdado: {e}", exc_info=True)
        return jsonify({"erro": "Erro ao salvar no banco", "mensagem": str(e)}), 500


@app.route('/microdados', methods=['GET'])
def listar_microdados_paginados():
    try:
        page = request.args.get('pagina', 1, type=int)
        per_page = request.args.get('limite', 10, type=int)

        logger.info(f"Listando microdados - Página: {page}, Limite: {per_page}")
        
        pagination_object = db.paginate(
            db.select(Microdado).order_by(Microdado.id), 
            page=page, 
            per_page=per_page, 
            error_out=False
        )

        schema = MicrodadoSchema(many=True) 
        itens_serializados = schema.dump(pagination_object.items)

        response = {
            "items": itens_serializados,
            "pagination": {
                "total_items": pagination_object.total,
                "total_pages": pagination_object.pages,
                "current_page": pagination_object.page,
                "per_page": pagination_object.per_page,
            }
        }
        return jsonify(response)

    except Exception as e:
        logger.error(f"Erro crítico na paginação: {e}", exc_info=True)
        return jsonify({"erro": "Erro interno do servidor", "mensagem": "Não foi possível listar os dados."}), 500



if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    
    app.run(debug=True)