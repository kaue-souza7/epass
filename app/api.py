from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import check_password_hash
from app.models import Responsavel, User  # ajuste conforme seu model
from app import db
from app import bcrypt
from flask_jwt_extended import jwt_required, get_jwt_identity


api = Blueprint('api', __name__)





@api.route('/login', methods=['POST'])
def login():
    
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    # validação básica
    if not email or not senha:
        return jsonify({'error': 'Dados inválidos'}), 400


    # busca usuário no banco
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    # verifica senha (assumindo que está com hash)
    if not bcrypt.check_password_hash(user.senha, senha):
        return jsonify({'error': 'Senha incorreta'}), 401

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    # resposta de sucesso 
    return jsonify({
        'message': 'Login realizado com sucesso',
        'token': access_token,
        'refresh_token': refresh_token,    
        'user': {
            'id': user.id,
            'nome': user.nome,
            'email': user.email,
            'tipo_usuario': user.tipo_usuario.value
        }
    }), 200




@api.route('/refresh', methods=['POST'])
@jwt_required(refresh=True) # Note o parâmetro refresh=True
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token), 200






@api.route('/listar_alunos', methods=['GET'])
@jwt_required()
def get_meus_alunos():
    # 1. Pega o ID do usuário (User) que está no Token
    current_user_id = get_jwt_identity()

    # 2. Busca o registro de Responsavel vinculado a esse User
    responsavel = Responsavel.query.filter_by(user_id=current_user_id).first()

    if not responsavel:
        return jsonify({'error': 'Perfil de responsável não encontrado'}), 404

    # 3. Acessa a lista de alunos (graças ao db.relationship que você já criou)
    alunos_list = []
    for aluno in responsavel.alunos:
        alunos_list.append({
            'id': aluno.id,
            'nome': aluno.nome,
            'sobrenome': aluno.sobrenome,
            'matricula': aluno.matricula,
            'turma_id': aluno.turma_id,
            'status': aluno.status,
            'nascimento': aluno.nascimento.isoformat() if aluno.nascimento else None
        })

    return jsonify(alunos_list), 200