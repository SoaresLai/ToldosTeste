from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, db
from src.models.client import Client
from src.models.seller import Seller
from src.models.quote import Quote
from src.models.product import Product
from src.utils.decorators import role_required, verified_required, get_current_user
from src.utils.validators import Validators
from src.services.email_service import EmailService
import secrets

quote_bp = Blueprint('quote', __name__)

@quote_bp.route('/quotes', methods=['GET'])
@verified_required
def get_quotes():
    """Lista orçamentos baseado no role do usuário"""
    try:
        current_user = get_current_user()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status', '')
        
        # Filtrar baseado no role
        if current_user.role == 'admin':
            query = Quote.query
        elif current_user.role == 'seller':
            seller = Seller.query.filter_by(user_id=current_user.id).first()
            if not seller:
                return jsonify({'error': 'Perfil de vendedor não encontrado'}), 404
            query = Quote.query.filter_by(seller_id=seller.id)
        elif current_user.role == 'client':
            client = Client.query.filter_by(user_id=current_user.id).first()
            if not client:
                return jsonify({'error': 'Perfil de cliente não encontrado'}), 404
            query = Quote.query.filter_by(client_id=client.id)
        else:
            return jsonify({'error': 'Role inválido'}), 403
        
        # Filtrar por status se especificado
        if status:
            status_valid, status_error = Validators.validate_status(status)
            if not status_valid:
                return jsonify({'error': status_error}), 400
            query = query.filter_by(status=status)
        
        quotes = query.order_by(Quote.created_at.desc()).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'quotes': [quote.to_dict() for quote in quotes.items],
            'total': quotes.total,
            'pages': quotes.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao listar orçamentos: {str(e)}'}), 500

@quote_bp.route('/quotes/<int:quote_id>', methods=['GET'])
@verified_required
def get_quote(quote_id):
    """Obtém um orçamento específico"""
    try:
        current_user = get_current_user()
        quote = Quote.query.get_or_404(quote_id)
        
        # Verificar permissões
        if current_user.role == 'client':
            client = Client.query.filter_by(user_id=current_user.id).first()
            if not client or quote.client_id != client.id:
                return jsonify({'error': 'Acesso negado'}), 403
        elif current_user.role == 'seller':
            seller = Seller.query.filter_by(user_id=current_user.id).first()
            if not seller or quote.seller_id != seller.id:
                return jsonify({'error': 'Acesso negado'}), 403
        # Admin pode ver todos
        
        return jsonify(quote.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao obter orçamento: {str(e)}'}), 500

@quote_bp.route('/quotes', methods=['POST'])
@verified_required
@role_required('admin', 'seller')
def create_quote():
    """Cria um novo orçamento"""
    try:
        current_user = get_current_user()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados JSON são obrigatórios'}), 400
        
        # Campos obrigatórios
        required_fields = ['client_id', 'product_type', 'dimensions', 'materials']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'error': f'Campos obrigatórios ausentes: {", ".join(missing_fields)}'
            }), 400
        
        # Validações
        client = Client.query.get(data['client_id'])
        if not client:
            return jsonify({'error': 'Cliente não encontrado'}), 404
        
        # Validar dimensões
        dimensions_valid, dimensions_error = Validators.validate_dimensions(data['dimensions'])
        if not dimensions_valid:
            return jsonify({'error': dimensions_error}), 400
        
        # Determinar vendedor
        if current_user.role == 'seller':
            seller = Seller.query.filter_by(user_id=current_user.id).first()
            if not seller:
                return jsonify({'error': 'Perfil de vendedor não encontrado'}), 404
            seller_id = seller.id
        else:  # admin
            seller_id = data.get('seller_id')
            if not seller_id:
                return jsonify({'error': 'seller_id é obrigatório para admin'}), 400
            seller = Seller.query.get(seller_id)
            if not seller:
                return jsonify({'error': 'Vendedor não encontrado'}), 404
        
        # Calcular preço (implementação básica)
        total_price = data.get('total_price')
        if not total_price:
            # Cálculo automático baseado em dimensões e materiais
            width = data['dimensions'].get('width', 0)
            length = data['dimensions'].get('length', 0)
            area = width * length
            base_price_per_m2 = 150.0  # Preço base por m²
            total_price = area * base_price_per_m2
        
        price_valid, price_error = Validators.validate_price(total_price)
        if not price_valid:
            return jsonify({'error': price_error}), 400
        
        # Gerar senha para PDF
        pdf_password = secrets.token_urlsafe(8)
        
        # Criar orçamento
        quote = Quote(
            client_id=data['client_id'],
            seller_id=seller_id,
            product_type=data['product_type'],
            total_price=float(total_price),
            pdf_password=pdf_password,
            notes=data.get('notes')
        )
        
        quote.set_dimensions(data['dimensions'])
        quote.set_materials(data['materials'])
        
        db.session.add(quote)
        db.session.commit()
        
        # Enviar notificação por email
        try:
            EmailService.send_quote_notification(
                quote, 
                client.user.email, 
                client.user.name
            )
        except Exception as e:
            print(f"Erro ao enviar notificação: {str(e)}")
        
        return jsonify({
            'message': 'Orçamento criado com sucesso',
            'quote': quote.to_dict(),
            'pdf_password': pdf_password
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao criar orçamento: {str(e)}'}), 500

@quote_bp.route('/quotes/<int:quote_id>', methods=['PUT'])
@verified_required
@role_required('admin', 'seller')
def update_quote(quote_id):
    """Atualiza um orçamento"""
    try:
        current_user = get_current_user()
        quote = Quote.query.get_or_404(quote_id)
        
        # Verificar permissões
        if current_user.role == 'seller':
            seller = Seller.query.filter_by(user_id=current_user.id).first()
            if not seller or quote.seller_id != seller.id:
                return jsonify({'error': 'Acesso negado'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados JSON são obrigatórios'}), 400
        
        # Atualizar campos permitidos
        if 'product_type' in data:
            quote.product_type = data['product_type']
        
        if 'dimensions' in data:
            dimensions_valid, dimensions_error = Validators.validate_dimensions(data['dimensions'])
            if not dimensions_valid:
                return jsonify({'error': dimensions_error}), 400
            quote.set_dimensions(data['dimensions'])
        
        if 'materials' in data:
            quote.set_materials(data['materials'])
        
        if 'total_price' in data:
            price_valid, price_error = Validators.validate_price(data['total_price'])
            if not price_valid:
                return jsonify({'error': price_error}), 400
            quote.total_price = float(data['total_price'])
        
        if 'status' in data:
            status_valid, status_error = Validators.validate_status(data['status'])
            if not status_valid:
                return jsonify({'error': status_error}), 400
            quote.status = data['status']
        
        if 'notes' in data:
            quote.notes = data['notes']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Orçamento atualizado com sucesso',
            'quote': quote.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao atualizar orçamento: {str(e)}'}), 500

@quote_bp.route('/quotes/<int:quote_id>', methods=['DELETE'])
@verified_required
@role_required('admin')
def delete_quote(quote_id):
    """Deleta um orçamento (apenas admin)"""
    try:
        quote = Quote.query.get_or_404(quote_id)
        
        db.session.delete(quote)
        db.session.commit()
        
        return jsonify({'message': 'Orçamento deletado com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao deletar orçamento: {str(e)}'}), 500

@quote_bp.route('/quotes/<int:quote_id>/calculate', methods=['POST'])
@verified_required
@role_required('admin', 'seller')
def calculate_quote_price(quote_id):
    """Recalcula o preço de um orçamento"""
    try:
        quote = Quote.query.get_or_404(quote_id)
        data = request.get_json()
        
        if not data or 'dimensions' not in data:
            return jsonify({'error': 'Dimensões são obrigatórias'}), 400
        
        # Validar dimensões
        dimensions_valid, dimensions_error = Validators.validate_dimensions(data['dimensions'])
        if not dimensions_valid:
            return jsonify({'error': dimensions_error}), 400
        
        # Cálculo de preço
        width = data['dimensions'].get('width', 0)
        length = data['dimensions'].get('length', 0)
        height = data['dimensions'].get('height', 2.5)  # altura padrão
        
        area = width * length
        
        # Preços base por tipo de produto
        price_table = {
            'toldo_fixo': 120.0,
            'toldo_retratil': 180.0,
            'cobertura_policarbonato': 95.0,
            'pergolado': 200.0,
            'tenda': 85.0
        }
        
        base_price = price_table.get(quote.product_type, 150.0)
        
        # Calcular preço base
        calculated_price = area * base_price
        
        # Adicionar custos de materiais
        materials = data.get('materials', {})
        material_costs = {
            'estrutura_aluminio': 25.0,
            'estrutura_aco': 35.0,
            'lona_comum': 15.0,
            'lona_premium': 30.0,
            'policarbonato': 45.0,
            'vidro': 80.0
        }
        
        for material, quantity in materials.items():
            if material in material_costs:
                calculated_price += material_costs[material] * float(quantity)
        
        # Adicionar margem de complexidade
        complexity_factor = data.get('complexity_factor', 1.0)
        calculated_price *= complexity_factor
        
        return jsonify({
            'calculated_price': round(calculated_price, 2),
            'area': area,
            'base_price_per_m2': base_price,
            'breakdown': {
                'base_cost': round(area * base_price, 2),
                'material_cost': round(calculated_price - (area * base_price * complexity_factor), 2),
                'complexity_adjustment': round((calculated_price / complexity_factor) * (complexity_factor - 1), 2)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao calcular preço: {str(e)}'}), 500

@quote_bp.route('/quotes/<int:quote_id>/3d-data', methods=['GET'])
@verified_required
def get_quote_3d_data(quote_id):
    """Obtém dados para visualização 3D do orçamento"""
    try:
        current_user = get_current_user()
        quote = Quote.query.get_or_404(quote_id)
        
        # Verificar permissões
        if current_user.role == 'client':
            client = Client.query.filter_by(user_id=current_user.id).first()
            if not client or quote.client_id != client.id:
                return jsonify({'error': 'Acesso negado'}), 403
        elif current_user.role == 'seller':
            seller = Seller.query.filter_by(user_id=current_user.id).first()
            if not seller or quote.seller_id != seller.id:
                return jsonify({'error': 'Acesso negado'}), 403
        
        dimensions = quote.get_dimensions()
        materials = quote.get_materials()
        
        # Gerar dados para visualização 3D
        visualization_data = {
            'geometry': {
                'width': dimensions.get('width', 0),
                'length': dimensions.get('length', 0),
                'height': dimensions.get('height', 2.5),
                'type': quote.product_type
            },
            'materials': materials,
            'colors': {
                'structure': materials.get('structure_color', '#808080'),
                'cover': materials.get('cover_color', '#ffffff'),
                'frame': materials.get('frame_color', '#404040')
            },
            'features': {
                'retractable': 'retratil' in quote.product_type.lower(),
                'motorized': materials.get('motorized', False),
                'led_lighting': materials.get('led_lighting', False),
                'wind_sensor': materials.get('wind_sensor', False)
            },
            'measurements': {
                'area': dimensions.get('width', 0) * dimensions.get('length', 0),
                'perimeter': 2 * (dimensions.get('width', 0) + dimensions.get('length', 0)),
                'coverage_angle': dimensions.get('angle', 0)
            }
        }
        
        return jsonify(visualization_data), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao obter dados 3D: {str(e)}'}), 500

