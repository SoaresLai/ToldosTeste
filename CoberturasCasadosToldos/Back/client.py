from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, db
from src.models.client import Client
from src.utils.decorators import role_required, verified_required, get_current_user
from src.utils.validators import Validators

client_bp = Blueprint('client', __name__)

@client_bp.route('/clients', methods=['GET'])
@verified_required
@role_required('admin', 'seller')
def get_clients():
    """Lista todos os clientes (apenas admin e vendedores)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        
        query = Client.query.join(User)
        
        if search:
            query = query.filter(
                db.or_(
                    User.name.contains(search),
                    User.email.contains(search),
                    Client.company_name.contains(search)
                )
            )
        
        clients = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'clients': [client.to_dict() for client in clients.items],
            'total': clients.total,
            'pages': clients.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao listar clientes: {str(e)}'}), 500

@client_bp.route('/clients/<int:client_id>', methods=['GET'])
@verified_required
@role_required('admin', 'seller', 'client')
def get_client(client_id):
    """Obtém um cliente específico"""
    try:
        current_user = get_current_user()
        client = Client.query.get_or_404(client_id)
        
        # Clientes só podem ver seus próprios dados
        if current_user.role == 'client' and client.user_id != current_user.id:
            return jsonify({'error': 'Acesso negado'}), 403
        
        return jsonify(client.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao obter cliente: {str(e)}'}), 500

@client_bp.route('/clients', methods=['POST'])
@verified_required
@role_required('admin')
def create_client():
    """Cria um novo cliente (apenas admin)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados JSON são obrigatórios'}), 400
        
        # Campos obrigatórios
        required_fields = ['email', 'password', 'name']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return jsonify({
                'error': f'Campos obrigatórios ausentes: {", ".join(missing_fields)}'
            }), 400
        
        # Validações
        email_valid, email_error = Validators.validate_email_format(data['email'])
        if not email_valid:
            return jsonify({'error': f'Email inválido: {email_error}'}), 400
        
        password_valid, password_error = Validators.validate_password_strength(data['password'])
        if not password_valid:
            return jsonify({'error': password_error}), 400
        
        if data.get('phone'):
            phone_valid, phone_error = Validators.validate_phone(data['phone'])
            if not phone_valid:
                return jsonify({'error': phone_error}), 400
        
        if data.get('zip_code'):
            cep_valid, cep_error = Validators.validate_cep(data['zip_code'])
            if not cep_valid:
                return jsonify({'error': cep_error}), 400
        
        # Verificar se o email já existe
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email já está em uso'}), 400
        
        # Criar usuário
        user = User(
            email=data['email'],
            name=data['name'],
            role='client',
            is_verified=True  # Admin pode criar usuários já verificados
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.flush()  # Para obter o ID do usuário
        
        # Criar cliente
        client = Client(
            user_id=user.id,
            company_name=data.get('company_name'),
            phone=data.get('phone'),
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state'),
            zip_code=data.get('zip_code')
        )
        
        db.session.add(client)
        db.session.commit()
        
        return jsonify({
            'message': 'Cliente criado com sucesso',
            'client': client.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao criar cliente: {str(e)}'}), 500

@client_bp.route('/clients/<int:client_id>', methods=['PUT'])
@verified_required
@role_required('admin', 'client')
def update_client(client_id):
    """Atualiza um cliente"""
    try:
        current_user = get_current_user()
        client = Client.query.get_or_404(client_id)
        
        # Clientes só podem atualizar seus próprios dados
        if current_user.role == 'client' and client.user_id != current_user.id:
            return jsonify({'error': 'Acesso negado'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados JSON são obrigatórios'}), 400
        
        # Validações
        if 'phone' in data and data['phone']:
            phone_valid, phone_error = Validators.validate_phone(data['phone'])
            if not phone_valid:
                return jsonify({'error': phone_error}), 400
        
        if 'zip_code' in data and data['zip_code']:
            cep_valid, cep_error = Validators.validate_cep(data['zip_code'])
            if not cep_valid:
                return jsonify({'error': cep_error}), 400
        
        # Atualizar dados do usuário
        user = client.user
        if 'name' in data:
            user.name = data['name']
        
        # Atualizar dados do cliente
        if 'company_name' in data:
            client.company_name = data['company_name']
        if 'phone' in data:
            client.phone = data['phone']
        if 'address' in data:
            client.address = data['address']
        if 'city' in data:
            client.city = data['city']
        if 'state' in data:
            client.state = data['state']
        if 'zip_code' in data:
            client.zip_code = data['zip_code']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Cliente atualizado com sucesso',
            'client': client.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao atualizar cliente: {str(e)}'}), 500

@client_bp.route('/clients/<int:client_id>', methods=['DELETE'])
@verified_required
@role_required('admin')
def delete_client(client_id):
    """Deleta um cliente (apenas admin)"""
    try:
        client = Client.query.get_or_404(client_id)
        user = client.user
        
        # Verificar se o cliente tem orçamentos
        if client.quotes:
            return jsonify({
                'error': 'Não é possível deletar cliente com orçamentos associados'
            }), 400
        
        db.session.delete(client)
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'Cliente deletado com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao deletar cliente: {str(e)}'}), 500

@client_bp.route('/clients/profile', methods=['GET'])
@verified_required
@role_required('client')
def get_my_profile():
    """Obtém o perfil do cliente atual"""
    try:
        current_user = get_current_user()
        client = Client.query.filter_by(user_id=current_user.id).first()
        
        if not client:
            return jsonify({'error': 'Perfil de cliente não encontrado'}), 404
        
        return jsonify(client.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao obter perfil: {str(e)}'}), 500

@client_bp.route('/clients/profile', methods=['PUT'])
@verified_required
@role_required('client')
def update_my_profile():
    """Atualiza o perfil do cliente atual"""
    try:
        current_user = get_current_user()
        client = Client.query.filter_by(user_id=current_user.id).first()
        
        if not client:
            return jsonify({'error': 'Perfil de cliente não encontrado'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados JSON são obrigatórios'}), 400
        
        # Validações
        if 'phone' in data and data['phone']:
            phone_valid, phone_error = Validators.validate_phone(data['phone'])
            if not phone_valid:
                return jsonify({'error': phone_error}), 400
        
        if 'zip_code' in data and data['zip_code']:
            cep_valid, cep_error = Validators.validate_cep(data['zip_code'])
            if not cep_valid:
                return jsonify({'error': cep_error}), 400
        
        # Atualizar dados do usuário
        if 'name' in data:
            current_user.name = data['name']
        
        # Atualizar dados do cliente
        if 'company_name' in data:
            client.company_name = data['company_name']
        if 'phone' in data:
            client.phone = data['phone']
        if 'address' in data:
            client.address = data['address']
        if 'city' in data:
            client.city = data['city']
        if 'state' in data:
            client.state = data['state']
        if 'zip_code' in data:
            client.zip_code = data['zip_code']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Perfil atualizado com sucesso',
            'client': client.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao atualizar perfil: {str(e)}'}), 500

