from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import check_password_hash
from app.models import Aluno, Carteira, Responsavel, User  # ajuste conforme seu model
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




@api.route('/carteiras/create', methods=['POST'])
@jwt_required()
def criar_carteira():
    
    data = request.get_json()

    aluno_id = data.get('aluno_id')

    aluno = Aluno.query.get(aluno_id)

    if not aluno:
        return jsonify({'erro': 'Aluno não encontrado'}), 404

    if aluno.carteira:
        return jsonify({'erro': 'Aluno já possui carteira'}), 400

    carteira = Carteira(aluno_id=aluno_id)

    db.session.add(carteira)
    db.session.commit()

    return jsonify({
        'id': carteira.id,
        'aluno_id': carteira.aluno_id,
        'saldo': carteira.saldo
    }), 201


@api.route('/carteiras/find/<int:id>', methods=['GET'])
@jwt_required()
def buscar_carteira(id):
    carteira = Carteira.query.get(id)

    if not carteira:
        return jsonify({'erro': 'Carteira não encontrada'}), 404

    return jsonify({
        'id': carteira.id,
        'aluno_id': carteira.aluno_id,
        'saldo': carteira.saldo
    })




@api.route('/carteiras/update/<int:id>', methods=['PUT'])
def update_carteira(id):
    carteira = Carteira.query.get(id)

    if not carteira:
        return jsonify({'erro': 'Carteira não encontrada'}), 404

    data = request.get_json()
    novo_saldo = data.get('saldo')

    if novo_saldo is None:
        return jsonify({'erro': 'Saldo é obrigatório'}), 400

    carteira.saldo = novo_saldo

    db.session.commit()

    return jsonify({'mensagem': 'Carteira atualizada'})