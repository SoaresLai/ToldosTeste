from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from src.models.quote import Quote
from src.models.client import Client
from src.models.seller import Seller
from src.services.pdf_service import PDFService
from src.utils.decorators import verified_required, get_current_user, role_required
import io
import secrets

pdf_bp = Blueprint('pdf', __name__)

@pdf_bp.route('/pdf/quote/<int:quote_id>', methods=['GET'])
@verified_required
def generate_quote_pdf(quote_id):
    """Gera PDF do orçamento"""
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
        
        # Verificar se deve usar senha
        use_password = request.args.get('protected', 'true').lower() == 'true'
        password = quote.pdf_password if use_password else None
        
        # Gerar PDF
        quote_data = quote.to_dict()
        pdf_bytes = PDFService.generate_quote_pdf(quote_data, password)
        
        # Criar arquivo em memória
        pdf_file = io.BytesIO(pdf_bytes)
        pdf_file.seek(0)
        
        # Nome do arquivo
        filename = f"orcamento_{quote.id}_{quote.created_at.strftime('%Y%m%d')}.pdf"
        
        return send_file(
            pdf_file,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar PDF: {str(e)}'}), 500

@pdf_bp.route('/pdf/quote/<int:quote_id>/password', methods=['POST'])
@verified_required
def get_quote_pdf_password(quote_id):
    """Obtém a senha do PDF do orçamento (apenas para usuários autorizados)"""
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
        
        return jsonify({
            'success': True,
            'pdf_password': quote.pdf_password,
            'quote_id': quote.id
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao obter senha do PDF: {str(e)}'}), 500

@pdf_bp.route('/pdf/quote/<int:quote_id>/regenerate-password', methods=['POST'])
@verified_required
@role_required('admin', 'seller')
def regenerate_quote_pdf_password(quote_id):
    """Regenera a senha do PDF do orçamento"""
    try:
        current_user = get_current_user()
        quote = Quote.query.get_or_404(quote_id)
        
        # Verificar permissões para vendedores
        if current_user.role == 'seller':
            seller = Seller.query.filter_by(user_id=current_user.id).first()
            if not seller or quote.seller_id != seller.id:
                return jsonify({'error': 'Acesso negado'}), 403
        
        # Gerar nova senha
        new_password = secrets.token_urlsafe(8)
        quote.pdf_password = new_password
        
        from src.models.user import db
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Nova senha gerada com sucesso',
            'pdf_password': new_password,
            'quote_id': quote.id
        }), 200
        
    except Exception as e:
        from src.models.user import db
        db.session.rollback()
        return jsonify({'error': f'Erro ao regenerar senha: {str(e)}'}), 500

@pdf_bp.route('/pdf/report/sellers', methods=['GET'])
@verified_required
@role_required('admin')
def generate_sellers_report_pdf():
    """Gera PDF do relatório de vendedores"""
    try:
        # Importar aqui para evitar importação circular
        from src.routes.dashboard import get_sellers_report
        
        # Obter dados do relatório
        with current_app.test_request_context():
            response = get_sellers_report()
            if response[1] != 200:
                return response
            
            report_data = response[0].get_json()
        
        # Gerar PDF
        pdf_bytes = PDFService.generate_report_pdf(report_data, 'sellers')
        
        # Criar arquivo em memória
        pdf_file = io.BytesIO(pdf_bytes)
        pdf_file.seek(0)
        
        filename = f"relatorio_vendedores_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        
        return send_file(
            pdf_file,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar relatório PDF: {str(e)}'}), 500

@pdf_bp.route('/pdf/report/clients', methods=['GET'])
@verified_required
@role_required('admin', 'seller')
def generate_clients_report_pdf():
    """Gera PDF do relatório de clientes"""
    try:
        from flask import current_app
        from datetime import datetime
        from src.routes.dashboard import get_clients_report
        
        # Obter dados do relatório
        with current_app.test_request_context():
            response = get_clients_report()
            if response[1] != 200:
                return response
            
            report_data = response[0].get_json()
        
        # Gerar PDF
        pdf_bytes = PDFService.generate_report_pdf(report_data, 'clients')
        
        # Criar arquivo em memória
        pdf_file = io.BytesIO(pdf_bytes)
        pdf_file.seek(0)
        
        filename = f"relatorio_clientes_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        
        return send_file(
            pdf_file,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar relatório PDF: {str(e)}'}), 500

@pdf_bp.route('/pdf/report/financial', methods=['GET'])
@verified_required
@role_required('admin')
def generate_financial_report_pdf():
    """Gera PDF do relatório financeiro"""
    try:
        from flask import current_app
        from datetime import datetime
        from src.routes.dashboard import get_financial_report
        
        # Obter parâmetros
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Obter dados do relatório
        with current_app.test_request_context(query_string=request.query_string):
            response = get_financial_report()
            if response[1] != 200:
                return response
            
            report_data = response[0].get_json()
        
        # Gerar PDF
        pdf_bytes = PDFService.generate_report_pdf(report_data, 'financial')
        
        # Criar arquivo em memória
        pdf_file = io.BytesIO(pdf_bytes)
        pdf_file.seek(0)
        
        filename = f"relatorio_financeiro_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        
        return send_file(
            pdf_file,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar relatório financeiro PDF: {str(e)}'}), 500

@pdf_bp.route('/pdf/unlock', methods=['POST'])
def unlock_pdf():
    """Endpoint para validar senha de PDF (para uso no frontend)"""
    try:
        data = request.get_json()
        
        if not data or 'quote_id' not in data or 'password' not in data:
            return jsonify({'error': 'quote_id e password são obrigatórios'}), 400
        
        quote = Quote.query.get_or_404(data['quote_id'])
        
        # Verificar senha
        if quote.pdf_password == data['password']:
            return jsonify({
                'success': True,
                'message': 'Senha correta',
                'quote_id': quote.id
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Senha incorreta'
            }), 401
        
    except Exception as e:
        return jsonify({'error': f'Erro ao validar senha: {str(e)}'}), 500

@pdf_bp.route('/pdf/preview/<int:quote_id>', methods=['GET'])
@verified_required
def preview_quote_pdf(quote_id):
    """Gera preview do PDF sem proteção por senha"""
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
        
        # Gerar PDF sem senha para preview
        quote_data = quote.to_dict()
        pdf_bytes = PDFService.generate_quote_pdf(quote_data, password=None)
        
        # Criar arquivo em memória
        pdf_file = io.BytesIO(pdf_bytes)
        pdf_file.seek(0)
        
        return send_file(
            pdf_file,
            mimetype='application/pdf',
            as_attachment=False  # Para visualizar no navegador
        )
        
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar preview: {str(e)}'}), 500

