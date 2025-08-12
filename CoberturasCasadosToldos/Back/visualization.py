from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from src.models.quote import Quote
from src.models.product import Product
from src.services.visualization_service import VisualizationService
from src.utils.decorators import verified_required, get_current_user
from src.utils.validators import Validators

visualization_bp = Blueprint('visualization', __name__)

@visualization_bp.route('/visualization/generate', methods=['POST'])
@verified_required
def generate_3d_visualization():
    """Gera visualização 3D baseada em parâmetros"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados JSON são obrigatórios'}), 400
        
        # Campos obrigatórios
        required_fields = ['product_type', 'dimensions']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'error': f'Campos obrigatórios ausentes: {", ".join(missing_fields)}'
            }), 400
        
        # Validar dimensões
        dimensions_valid, dimensions_error = Validators.validate_dimensions(data['dimensions'])
        if not dimensions_valid:
            return jsonify({'error': dimensions_error}), 400
        
        # Gerar geometria 3D
        geometry_data = VisualizationService.generate_3d_geometry(
            product_type=data['product_type'],
            dimensions=data['dimensions'],
            materials=data.get('materials', {})
        )
        
        # Exportar para formato Three.js
        threejs_data = VisualizationService.export_to_threejs_format(geometry_data)
        
        return jsonify({
            'success': True,
            'visualization_data': threejs_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar visualização: {str(e)}'}), 500

@visualization_bp.route('/visualization/quote/<int:quote_id>', methods=['GET'])
@verified_required
def get_quote_visualization(quote_id):
    """Obtém visualização 3D de um orçamento específico"""
    try:
        current_user = get_current_user()
        quote = Quote.query.get_or_404(quote_id)
        
        # Verificar permissões (mesmo código da rota de quote)
        if current_user.role == 'client':
            from src.models.client import Client
            client = Client.query.filter_by(user_id=current_user.id).first()
            if not client or quote.client_id != client.id:
                return jsonify({'error': 'Acesso negado'}), 403
        elif current_user.role == 'seller':
            from src.models.seller import Seller
            seller = Seller.query.filter_by(user_id=current_user.id).first()
            if not seller or quote.seller_id != seller.id:
                return jsonify({'error': 'Acesso negado'}), 403
        
        # Gerar visualização baseada no orçamento
        dimensions = quote.get_dimensions()
        materials = quote.get_materials()
        
        geometry_data = VisualizationService.generate_3d_geometry(
            product_type=quote.product_type,
            dimensions=dimensions,
            materials=materials
        )
        
        # Exportar para formato Three.js
        threejs_data = VisualizationService.export_to_threejs_format(geometry_data)
        
        # Adicionar informações do orçamento
        threejs_data['quote_info'] = {
            'id': quote.id,
            'total_price': quote.total_price,
            'status': quote.status,
            'created_at': quote.created_at.isoformat() if quote.created_at else None
        }
        
        return jsonify({
            'success': True,
            'visualization_data': threejs_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao obter visualização do orçamento: {str(e)}'}), 500

@visualization_bp.route('/visualization/products', methods=['GET'])
@verified_required
def get_product_types():
    """Lista tipos de produtos disponíveis para visualização"""
    try:
        product_types = [
            {
                'id': 'toldo_fixo',
                'name': 'Toldo Fixo',
                'description': 'Toldo fixo com estrutura de alumínio',
                'base_price': 120.0,
                'features': ['Estrutura fixa', 'Resistente ao vento', 'Baixa manutenção']
            },
            {
                'id': 'toldo_retratil',
                'name': 'Toldo Retrátil',
                'description': 'Toldo retrátil com sistema motorizado',
                'base_price': 180.0,
                'features': ['Retrátil', 'Motorizado', 'Controle remoto', 'Sensor de vento']
            },
            {
                'id': 'cobertura_policarbonato',
                'name': 'Cobertura de Policarbonato',
                'description': 'Cobertura transparente de policarbonato',
                'base_price': 95.0,
                'features': ['Transparente', 'Proteção UV', 'Isolamento térmico']
            },
            {
                'id': 'pergolado',
                'name': 'Pergolado',
                'description': 'Estrutura de pergolado em madeira ou alumínio',
                'base_price': 200.0,
                'features': ['Teto aberto', 'Suporte para plantas', 'Sombra parcial']
            },
            {
                'id': 'tenda',
                'name': 'Tenda',
                'description': 'Tenda portátil para eventos',
                'base_price': 85.0,
                'features': ['Portátil', 'Montagem rápida', 'Resistente à chuva']
            }
        ]
        
        return jsonify({
            'success': True,
            'product_types': product_types
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao listar tipos de produtos: {str(e)}'}), 500

@visualization_bp.route('/visualization/materials', methods=['GET'])
def get_available_materials():
    """Lista materiais disponíveis para visualização"""
    try:
        materials = {
            'estrutura': [
                {'id': 'aluminio', 'name': 'Alumínio', 'color': '#C0C0C0', 'price_factor': 1.0},
                {'id': 'aco', 'name': 'Aço', 'color': '#808080', 'price_factor': 1.2},
                {'id': 'madeira', 'name': 'Madeira', 'color': '#8B4513', 'price_factor': 0.8}
            ],
            'cobertura': [
                {'id': 'lona_comum', 'name': 'Lona Comum', 'color': '#FFFFFF', 'price_factor': 1.0},
                {'id': 'lona_premium', 'name': 'Lona Premium', 'color': '#F0F0F0', 'price_factor': 1.5},
                {'id': 'policarbonato', 'name': 'Policarbonato', 'color': '#E6F3FF', 'price_factor': 2.0},
                {'id': 'vidro', 'name': 'Vidro', 'color': '#E0F6FF', 'price_factor': 3.0}
            ],
            'cores': [
                {'id': 'branco', 'name': 'Branco', 'hex': '#FFFFFF'},
                {'id': 'bege', 'name': 'Bege', 'hex': '#F5F5DC'},
                {'id': 'cinza', 'name': 'Cinza', 'hex': '#808080'},
                {'id': 'azul', 'name': 'Azul', 'hex': '#4169E1'},
                {'id': 'verde', 'name': 'Verde', 'hex': '#228B22'},
                {'id': 'vermelho', 'name': 'Vermelho', 'hex': '#DC143C'},
                {'id': 'preto', 'name': 'Preto', 'hex': '#000000'}
            ],
            'acessorios': [
                {'id': 'led_lighting', 'name': 'Iluminação LED', 'price': 150.0},
                {'id': 'wind_sensor', 'name': 'Sensor de Vento', 'price': 200.0},
                {'id': 'remote_control', 'name': 'Controle Remoto', 'price': 100.0},
                {'id': 'rain_sensor', 'name': 'Sensor de Chuva', 'price': 180.0}
            ]
        }
        
        return jsonify({
            'success': True,
            'materials': materials
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao listar materiais: {str(e)}'}), 500

@visualization_bp.route('/visualization/calculate-price', methods=['POST'])
@verified_required
def calculate_visualization_price():
    """Calcula preço baseado na visualização"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados JSON são obrigatórios'}), 400
        
        # Campos obrigatórios
        required_fields = ['product_type', 'dimensions']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'error': f'Campos obrigatórios ausentes: {", ".join(missing_fields)}'
            }), 400
        
        # Validar dimensões
        dimensions_valid, dimensions_error = Validators.validate_dimensions(data['dimensions'])
        if not dimensions_valid:
            return jsonify({'error': dimensions_error}), 400
        
        # Calcular preço
        width = float(data['dimensions']['width'])
        length = float(data['dimensions']['length'])
        area = width * length
        
        # Preços base por tipo
        base_prices = {
            'toldo_fixo': 120.0,
            'toldo_retratil': 180.0,
            'cobertura_policarbonato': 95.0,
            'pergolado': 200.0,
            'tenda': 85.0
        }
        
        base_price = base_prices.get(data['product_type'], 150.0)
        total_price = area * base_price
        
        # Adicionar custos de materiais
        materials = data.get('materials', {})
        material_cost = 0
        
        material_prices = {
            'estrutura_aco': 25.0,
            'estrutura_madeira': -15.0,
            'lona_premium': 20.0,
            'policarbonato': 40.0,
            'vidro': 80.0
        }
        
        for material, selected in materials.items():
            if selected and material in material_prices:
                material_cost += material_prices[material] * area
        
        # Adicionar custos de acessórios
        accessories = data.get('accessories', {})
        accessory_cost = 0
        
        accessory_prices = {
            'led_lighting': 150.0,
            'wind_sensor': 200.0,
            'remote_control': 100.0,
            'rain_sensor': 180.0
        }
        
        for accessory, selected in accessories.items():
            if selected and accessory in accessory_prices:
                accessory_cost += accessory_prices[accessory]
        
        # Calcular preço final
        final_price = total_price + material_cost + accessory_cost
        
        # Aplicar fator de complexidade
        complexity_factor = data.get('complexity_factor', 1.0)
        final_price *= complexity_factor
        
        return jsonify({
            'success': True,
            'price_breakdown': {
                'base_price': round(total_price, 2),
                'material_cost': round(material_cost, 2),
                'accessory_cost': round(accessory_cost, 2),
                'complexity_adjustment': round(final_price - (total_price + material_cost + accessory_cost), 2),
                'total_price': round(final_price, 2)
            },
            'area': round(area, 2),
            'base_price_per_m2': base_price
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao calcular preço: {str(e)}'}), 500

@visualization_bp.route('/visualization/export/<format>', methods=['POST'])
@verified_required
def export_visualization(format):
    """Exporta visualização em diferentes formatos"""
    try:
        if format not in ['obj', 'stl', 'gltf', 'json']:
            return jsonify({'error': 'Formato não suportado'}), 400
        
        data = request.get_json()
        
        if not data or 'visualization_data' not in data:
            return jsonify({'error': 'Dados de visualização são obrigatórios'}), 400
        
        # Por enquanto, retornar apenas o JSON
        # Em uma implementação completa, seria necessário converter para outros formatos
        
        if format == 'json':
            return jsonify({
                'success': True,
                'format': format,
                'data': data['visualization_data']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'Exportação para {format} ainda não implementada'
            }), 501
        
    except Exception as e:
        return jsonify({'error': f'Erro ao exportar visualização: {str(e)}'}), 500

