from decimal import Decimal
import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import check_password_hash
from app.models import Aluno, AvisoDestinatario, Carteira, PagamentoPendente, Responsavel, Transacao, User  # ajuste conforme seu model
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





@api.route('/responsavel/find', methods=['GET'])
@jwt_required()
def busca_responsavel():
    user_id = get_jwt_identity()
    responsavel = Responsavel.query.filter_by(user_id=user_id).first()
    alunos = [a.nome for a in responsavel.alunos]


    if not responsavel:
        return jsonify({'erro': 'Responsável não encontrado'}), 404

    user = responsavel.user
    logradouro = responsavel.logradouro

    return jsonify({
        # dados do User
        'nome': user.nome,
        'sobrenome': user.sobrenome,
        'email': user.email,
        'tipo_usuario': user.tipo_usuario.value if user.tipo_usuario else None,

        # dados do Responsavel
        'telefone': responsavel.telefone,
        'nascimento': responsavel.nascimento.strftime('%Y-%m-%d') if responsavel.nascimento else None,
        'alunos': alunos,

        # dados do Logradouro
        'logradouro': {
            'rua': logradouro.rua,
            'numero': logradouro.numero,
            'bairro': logradouro.bairro,
            'cidade': logradouro.cidade,
            'estado': logradouro.estado,
            'cep': logradouro.cep,
        } if logradouro else None,
    }), 200






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



@api.route('/aluno/find/<int:aluno_id>', methods=['GET'])
@jwt_required()
def buscar_aluno(aluno_id):
    user_id = get_jwt_identity()
    responsavel = Responsavel.query.filter_by(user_id=user_id).first()

    if not responsavel:
        return jsonify({'erro': 'Responsável não encontrado'}), 404

    aluno = next((a for a in responsavel.alunos if a.id == aluno_id), None)
    if not aluno:
        return jsonify({'erro': 'Acesso negado'}), 403

    return jsonify({
        'id': aluno.id,
        'nome': aluno.nome,
        'sobrenome': aluno.sobrenome,
        'cpf': aluno.cpf,
        'nascimento': aluno.nascimento.strftime('%Y-%m-%d') if aluno.nascimento else None,
        'status': aluno.status,
        'created_at': aluno.created_at.strftime('%Y-%m-%d %H:%M:%S') if aluno.created_at else None,
        'matricula': aluno.matricula,
        'data_matricula': aluno.data_matricula.strftime('%Y-%m-%d') if aluno.data_matricula else None,
        'tipo_sanguineo': aluno.tipo_sanguineo.value if aluno.tipo_sanguineo else None,
    }), 200





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


@api.route('/carteiras/find/<int:aluno_id>', methods=['GET'])
@jwt_required()
def buscar_carteira(aluno_id):
    carteira = Carteira.query.filter_by(aluno_id=aluno_id).first()

    if not carteira:
        return jsonify({'erro': 'Carteira não encontrada'}), 404

    return jsonify({
        'id': carteira.id,
        'aluno_id': carteira.aluno_id,
        'saldo': carteira.saldo
    })


@api.route('/pagamento/gerar', methods=['POST'])
@jwt_required()
def gerar_pagamento():
    responsavel_id = get_jwt_identity()
    data = request.get_json()
    valor = data.get('valor')

    if not valor or float(valor) <= 0:
        return jsonify({'erro': 'Valor inválido'}), 400

    pedido_id = str(uuid.uuid4())

    pedido = PagamentoPendente(
        id=pedido_id,
        responsavel_id=responsavel_id,
        aluno_id=data.get('aluno_id'),
        valor=valor,
        qr_code=f"https://fake-qr.com/{pedido_id}",   # fake por enquanto
        copia_cola=f"PIX-{pedido_id[:8].upper()}-{int(valor*100)}"
    )

    db.session.add(pedido)
    db.session.commit()

    return jsonify({
        'pedido_id': pedido_id,
        'qr_code': pedido.qr_code,
        'copia_cola': pedido.copia_cola,
        'valor': float(pedido.valor)
    }), 201



@api.route('/pagamento/confirmar', methods=['POST'])
@jwt_required()
def confirmar_pagamento():
    responsavel_id = get_jwt_identity()
    data = request.get_json()
    pedido_id = data.get('pedido_id')

    pedido = PagamentoPendente.query.filter_by(
        id=pedido_id,
        responsavel_id=responsavel_id   # garante que é do responsável logado
    ).first()

    if not pedido:
        return jsonify({'erro': 'Pedido não encontrado'}), 404

    if pedido.status == 'confirmado':
        return jsonify({'erro': 'Pagamento já confirmado'}), 400

    # adiciona saldo na carteira
    carteira = Carteira.query.filter_by(aluno_id=pedido.aluno_id).first()
    carteira.saldo = Decimal(str(carteira.saldo)) + Decimal(str(pedido.valor))
    pedido.status = 'confirmado'

        # registra a transação
    transacao = Transacao(
        tipo='entrada',
        valor=float(pedido.valor),
        descricao=f'Crédito via PIX - pedido {pedido.id[:8].upper()}',
        carteira_id=carteira.id
    )
    db.session.add(transacao)

    db.session.commit()

    return jsonify({
        'mensagem': 'Crédito adicionado com sucesso',
        'saldo_novo': float(carteira.saldo)
    }), 200





@api.route('/carteira/historico/<int:aluno_id>', methods=['GET'])
@jwt_required()
def historico_transacoes(aluno_id):
    user_id = get_jwt_identity()
    


    responsavel = Responsavel.query.filter_by(user_id=user_id).first()
    print(responsavel)

    # valida se o aluno pertence ao responsável logado
    aluno = next((a for a in responsavel.alunos if a.id == aluno_id), None)
    if not aluno:
        return jsonify({'erro': 'Acesso negado'}), 403

    carteira = Carteira.query.filter_by(aluno_id=aluno_id).first()
    if not carteira:
        return jsonify({'erro': 'Carteira não encontrada'}), 404

    transacoes = Transacao.query.filter_by(
        carteira_id=carteira.id
    ).order_by(Transacao.data.desc()).all()

    # agrupa por dia
    historico = {}
    for t in transacoes:
        dia = t.data.strftime('%Y-%m-%d')
        if dia not in historico:
            historico[dia] = []
        historico[dia].append({
            'id': t.id,
            'tipo': t.tipo,
            'valor': t.valor,
            'descricao': t.descricao,
            'hora': t.data.strftime('%H:%M')
        })

    # formata como lista ordenada
    resultado = [
        {'data': dia, 'transacoes': transacoes}
        for dia, transacoes in historico.items()
    ]

    return jsonify({
        'aluno_id': aluno_id,
        'saldo_atual': float(carteira.saldo),
        'historico': resultado
    }), 200




@api.route('/carteiras/update/<int:id>', methods=['GET'])
@jwt_required()
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



@api.route('/lista/avisos/<int:id>', methods=['GET'])
@jwt_required()
def lista_avisos(id):
    current_user_id = get_jwt_identity()

    avisos = AvisoDestinatario.query.filter_by(
        destinatario_id=current_user_id
    ).all()

    if not avisos:
        return jsonify({'error': 'Nenhum aviso encontrado!'}), 404

    return jsonify([
        {
            'lido': aviso.lido,
            'aviso': {
                'id': aviso.aviso.id,
                'titulo': aviso.aviso.titulo,
                'mensagem': aviso.aviso.mensagem,
                'tipo': aviso.aviso.tipo.name if aviso.aviso.tipo else None,
                'prioridade': aviso.aviso.prioridade.value if aviso.aviso.prioridade else None,
                'data_envio': aviso.aviso.data_envio.isoformat() if aviso.aviso.data_envio else None,
                'enviado': aviso.aviso.enviado
            }
        }
        for aviso in avisos
    ]), 200


