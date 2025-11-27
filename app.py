from flask import Flask, jsonify, request
import sqlite3
from db import get_db_connection, init_db, load_initial_data

app = Flask(__name__)

# --- Inicialização da Aplicação ---
# Garante que as tabelas sejam criadas e os dados sejam carregados ao iniciar
with app.app_context():
    init_db()         # Cria as tabelas lendo schema.sql
    load_initial_data() # Carrega os dados (usando Pandas paginado)

# -----------------------------------------------------
# --- Endpoint: /usuarios (tb_usuario) ---
# -----------------------------------------------------
@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    conn = get_db_connection()
    usuarios = conn.execute('SELECT * FROM tb_usuario').fetchall() 
    conn.close()
    
    usuarios_list = [dict(row) for row in usuarios]
    return jsonify(usuarios_list)

@app.route('/usuarios', methods=['POST'])
def add_usuario():
    novo_usuario = request.get_json()
    
    campos_obrigatorios = ['nome', 'cpf', 'nascimento']
    if not all(campo in novo_usuario for campo in campos_obrigatorios):
        return jsonify({"erro": f"Dados incompletos. Os campos {campos_obrigatorios} são obrigatórios."}), 400
        
    nome = novo_usuario['nome']
    cpf = novo_usuario['cpf']
    nascimento = novo_usuario['nascimento']
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        sql_insert = "INSERT INTO tb_usuario (nome, cpf, nascimento) VALUES (?, ?, ?)"
        cursor.execute(sql_insert, (nome, cpf, nascimento))
        conn.commit()
        novo_id = cursor.lastrowid
        conn.close()
        return jsonify({"id": novo_id, "mensagem": "Usuário adicionado com sucesso"}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"erro": "CPF já cadastrado ou dados inválidos."}), 409
    except Exception as e:
        conn.close()
        return jsonify({"erro": str(e)}), 500


# -----------------------------------------------------
# --- Endpoint: /escolas (Com Paginação Otimizada) ---
# -----------------------------------------------------
@app.route('/escolas', methods=['GET'])
def get_escolas():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    # Limites de paginação
    if page < 1:
        page = 1
    if per_page > 200: 
        per_page = 200 
    
    offset = (page - 1) * per_page
    
    conn = get_db_connection()
    
    try:
        total_count = conn.execute('SELECT COUNT(*) FROM escolas').fetchone()[0]

        # Consulta paginada
        query = "SELECT * FROM escolas LIMIT ? OFFSET ?"
        escolas = conn.execute(query, (per_page, offset)).fetchall()
        
        conn.close()
        
        escolas_list = [dict(row) for row in escolas]
        
        # Cálculo do total de páginas
        total_paginas = (total_count + per_page - 1) // per_page
        
        return jsonify({
            "meta": {
                "total_registros": total_count,
                "total_paginas": total_paginas,
                "pagina_atual": page,
                "limite_por_pagina": per_page,
            },
            "dados": escolas_list
        })
    except Exception as e:
        conn.close()
        return jsonify({"erro": f"Erro ao consultar escolas: {str(e)}"}), 500

@app.route('/usuarios/<int:user_id>', methods=['PUT'])
def update_usuario(user_id):
    dados_atualizados = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Adaptado para incluir 'nascimento'
    nome = dados_atualizados.get('nome')
    cpf = dados_atualizados.get('cpf')
    nascimento = dados_atualizados.get('nascimento')
    
    # 1. Pré-verificação de campos (evita atualização sem dados)
    if not nome and not cpf and not nascimento:
        conn.close()
        return jsonify({"erro": "Nenhum campo de atualização válido fornecido."}), 400

    # Lógica para construir a query dinamicamente
    sets = []
    params = []
    
    if nome is not None:
        sets.append("nome = ?")
        params.append(nome)
    if cpf is not None:
        sets.append("cpf = ?")
        params.append(cpf)
    if nascimento is not None:
        sets.append("nascimento = ?")
        params.append(nascimento)

    # Adiciona o ID para a cláusula WHERE
    params.append(user_id)
    
    try:
        query = f"UPDATE tb_usuario SET {', '.join(sets)} WHERE id = ?"
        cursor.execute(query, tuple(params))
        rows_updated = cursor.rowcount
        conn.commit()
        
        # 2. SE rowcount for zero, faça uma SELEÇÃO para verificar se o usuário existe.
        check_user = conn.execute("SELECT id FROM tb_usuario WHERE id = ?", (user_id,)).fetchone()
        
        conn.close()
        
        if check_user is None:
            # ID não existe, mesmo antes do UPDATE
            return jsonify({"erro": f"Usuário com ID {user_id} não encontrado."}), 404
        
        # Se o usuário existe, mas rowcount foi zero (ou seja, dados não mudaram),
        # retornamos sucesso 200 (OK), pois o estado desejado foi alcançado.
        if rows_updated == 0:
            return jsonify({"mensagem": f"Usuário {user_id} encontrado, mas sem alterações aplicadas."}), 200

        # Se rowcount > 0, a atualização foi bem-sucedida
        return jsonify({"mensagem": f"Usuário {user_id} atualizado com sucesso."}), 200

    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"erro": "CPF já existe no sistema."}), 409
    except Exception as e:
        conn.close()
        return jsonify({"erro": str(e)}), 500
    
    
    
@app.route('/usuarios/<int:user_id>', methods=['DELETE'])
def delete_usuario(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Tenta remover o usuário com o ID fornecido
        cursor.execute("DELETE FROM tb_usuario WHERE id = ?", (user_id,))
        rows_deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        # Verifica se alguma linha foi realmente deletada
        if rows_deleted == 0:
            return jsonify({"erro": f"Usuário com ID {user_id} não encontrado."}), 404
            
        # Sucesso! Status 204 No Content (padrão para DELETE bem-sucedido sem corpo)
        return jsonify({"mensagem": f"Usuário {user_id} removido com sucesso."}), 204

    except Exception as e:
        conn.close()
        return jsonify({"erro": str(e)}), 500
    
    
if __name__ == '__main__':
    app.run(debug=True)
    