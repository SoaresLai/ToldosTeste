from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, db
from src.models.seller import Seller
from src.utils.decorators import role_required, verified_required, get_current_user
from src.utils.validators import Validators

seller_bp = Blueprint('seller', __name__)

@seller_bp.route('/sellers', methods=['GET'])
@verified_required
@role_required('admin')
def get_sellers():
    """Lista todos os vendedores (apenas admin)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        
        query = Seller.query.join(User)
        
        if search:
            query = query.filter(
                db.or_(
                    User.name.contains(search),
                    User.email.contains(search),
                    Seller.territory.contains(search)
                )
            )
        
        sellers = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'sellers': [seller.to_dict() for seller in sellers.items],
            'total': sellers.total,
            'pages': sellers.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao listar vendedores: {str(e)}'}), 500

@seller_bp.route('/sellers/<int:seller_id>', methods=['GET'])
@verified_required
@role_required('admin', 'seller')
def get_seller(seller_id):
    """Obtém um vendedor específico"""
    try:
        current_user = get_current_user()
        seller = Seller.query.get_or_404(seller_id)
        
        # Vendedores só podem ver seus próprios dados
        if current_user.role == 'seller' and seller.user_id != current_user.id:
            return jsonify({'error': 'Acesso negado'}), 403
        
        return jsonify(seller.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao obter vendedor: {str(e)}'}), 500

@seller_bp.route('/sellers', methods=['POST'])
@verified_required
@role_required('admin')
def create_seller():
    """Cria um novo vendedor (apenas admin)"""
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
        
        # Verificar se o email já existe
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email já está em uso'}), 400
        
        # Validar taxa de comissão
        commission_rate = data.get('commission_rate', 0.05)
        try:
            commission_rate = float(commission_rate)
            if commission_rate < 0 or commission_rate > 1:
                return jsonify({'error': 'Taxa de comissão deve estar entre 0 e 1'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Taxa de comissão deve ser um número válido'}), 400
        
        # Criar usuário
        user = User(
            email=data['email'],
            name=data['name'],
            role='seller',
            is_verified=True  # Admin pode criar usuários já verificados
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.flush()  # Para obter o ID do usuário
        
        # Criar vendedor
        seller = Seller(
            user_id=user.id,
            commission_rate=commission_rate,
            territory=data.get('territory')
        )
        
        db.session.add(seller)
        db.session.commit()
        
        return jsonify({
            'message': 'Vendedor criado com sucesso',
            'seller': seller.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao criar vendedor: {str(e)}'}), 500

@seller_bp.route('/sellers/<int:seller_id>', methods=['PUT'])
@verified_required
@role_required('admin', 'seller')
def update_seller(seller_id):
    """Atualiza um vendedor"""
    try:
        current_user = get_current_user()
        seller = Seller.query.get_or_404(seller_id)
        
        # Vendedores só podem atualizar seus próprios dados (exceto comissão)
        if current_user.role == 'seller' and seller.user_id != current_user.id:
            return jsonify({'error': 'Acesso negado'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados JSON são obrigatórios'}), 400
        
        # Atualizar dados do usuário
        user = seller.user
        if 'name' in data:
            user.name = data['name']
        
        # Atualizar dados do vendedor
        if 'territory' in data:
            seller.territory = data['territory']
        
        # Apenas admin pode alterar taxa de comissão
        if 'commission_rate' in data and current_user.role == 'admin':
            try:
                commission_rate = float(data['commission_rate'])
                if commission_rate < 0 or commission_rate > 1:
                    return jsonify({'error': 'Taxa de comissão deve estar entre 0 e 1'}), 400
                seller.commission_rate = commission_rate
            except (ValueError, TypeError):
                return jsonify({'error': 'Taxa de comissão deve ser um número válido'}), 400
        
        db.session.commit()
        
        return jsonify({
            'message': 'Vendedor atualizado com sucesso',
            'seller': seller.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao atualizar vendedor: {str(e)}'}), 500

@seller_bp.route('/sellers/<int:seller_id>', methods=['DELETE'])
@verified_required
@role_required('admin')
def delete_seller(seller_id):
    """Deleta um vendedor (apenas admin)"""
    try:
        seller = Seller.query.get_or_404(seller_id)
        user = seller.user
        
        # Verificar se o vendedor tem orçamentos
        if seller.quotes:
            return jsonify({
                'error': 'Não é possível deletar vendedor com orçamentos associados'
            }), 400
        
        db.session.delete(seller)
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'Vendedor deletado com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao deletar vendedor: {str(e)}'}), 500

@seller_bp.route('/sellers/profile', methods=['GET'])
@verified_required
@role_required('seller')
def get_my_profile():
    """Obtém o perfil do vendedor atual"""
    try:
        current_user = get_current_user()
        seller = Seller.query.filter_by(user_id=current_user.id).first()
        
        if not seller:
            return jsonify({'error': 'Perfil de vendedor não encontrado'}), 404
        
        return jsonify(seller.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao obter perfil: {str(e)}'}), 500

@seller_bp.route('/sellers/profile', methods=['PUT'])
@verified_required
@role_required('seller')
def update_my_profile():
    """Atualiza o perfil do vendedor atual"""
    try:
        current_user = get_current_user()
        seller = Seller.query.filter_by(user_id=current_user.id).first()
        
        if not seller:
            return jsonify({'error': 'Perfil de vendedor não encontrado'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados JSON são obrigatórios'}), 400
        
        # Atualizar dados do usuário
        if 'name' in data:
            current_user.name = data['name']
        
        # Atualizar dados do vendedor
        if 'territory' in data:
            seller.territory = data['territory']
        
        # Vendedores não podem alterar sua própria comissão
        
        db.session.commit()
        
        return jsonify({
            'message': 'Perfil atualizado com sucesso',
            'seller': seller.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao atualizar perfil: {str(e)}'}), 500

@seller_bp.route('/sellers/<int:seller_id>/stats', methods=['GET'])
@verified_required
@role_required('admin', 'seller')
def get_seller_stats(seller_id):
    """Obtém estatísticas de um vendedor"""
    try:
        current_user = get_current_user()
        seller = Seller.query.get_or_404(seller_id)
        
        # Vendedores só podem ver suas próprias estatísticas
        if current_user.role == 'seller' and seller.user_id != current_user.id:
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Calcular estatísticas
        from src.models.quote import Quote
        from sqlalchemy import func
        
        total_quotes = Quote.query.filter_by(seller_id=seller_id).count()
        approved_quotes = Quote.query.filter_by(seller_id=seller_id, status='approved').count()
        total_value = db.session.query(func.sum(Quote.total_price)).filter_by(
            seller_id=seller_id, status='approved'
        ).scalar() or 0
        
        commission_earned = total_value * seller.commission_rate
        
        stats = {
            'total_quotes': total_quotes,
            'approved_quotes': approved_quotes,
            'pending_quotes': Quote.query.filter_by(seller_id=seller_id, status='pending').count(),
            'rejected_quotes': Quote.query.filter_by(seller_id=seller_id, status='rejected').count(),
            'total_sales_value': float(total_value),
            'commission_earned': float(commission_earned),
            'conversion_rate': (approved_quotes / total_quotes * 100) if total_quotes > 0 else 0
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao obter estatísticas: {str(e)}'}), 500

