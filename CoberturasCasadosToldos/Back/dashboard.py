from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func, extract, and_
from datetime import datetime, timedelta
from src.models.user import User, db
from src.models.client import Client
from src.models.seller import Seller
from src.models.quote import Quote
from src.utils.decorators import role_required, verified_required, get_current_user

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard/stats', methods=['GET'])
@verified_required
@role_required('admin', 'seller')
def get_dashboard_stats():
    """Obtém estatísticas gerais do dashboard"""
    try:
        current_user = get_current_user()
        
        # Filtros baseados no role
        if current_user.role == 'seller':
            seller = Seller.query.filter_by(user_id=current_user.id).first()
            if not seller:
                return jsonify({'error': 'Perfil de vendedor não encontrado'}), 404
            quote_filter = Quote.seller_id == seller.id
        else:  # admin
            quote_filter = True
        
        # Estatísticas básicas
        total_clients = Client.query.count()
        total_sellers = Seller.query.count()
        total_quotes = Quote.query.filter(quote_filter).count()
        
        # Estatísticas de orçamentos por status
        quote_stats = db.session.query(
            Quote.status,
            func.count(Quote.id).label('count'),
            func.sum(Quote.total_price).label('total_value')
        ).filter(quote_filter).group_by(Quote.status).all()
        
        status_breakdown = {}
        total_value = 0
        
        for stat in quote_stats:
            status_breakdown[stat.status] = {
                'count': stat.count,
                'total_value': float(stat.total_value or 0)
            }
            if stat.status == 'approved':
                total_value += float(stat.total_value or 0)
        
        # Estatísticas do mês atual
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        monthly_quotes = Quote.query.filter(
            and_(
                quote_filter,
                extract('month', Quote.created_at) == current_month,
                extract('year', Quote.created_at) == current_year
            )
        ).count()
        
        monthly_revenue = db.session.query(
            func.sum(Quote.total_price)
        ).filter(
            and_(
                quote_filter,
                Quote.status == 'approved',
                extract('month', Quote.created_at) == current_month,
                extract('year', Quote.created_at) == current_year
            )
        ).scalar() or 0
        
        # Taxa de conversão
        conversion_rate = 0
        if total_quotes > 0:
            approved_quotes = status_breakdown.get('approved', {}).get('count', 0)
            conversion_rate = (approved_quotes / total_quotes) * 100
        
        # Ticket médio
        average_ticket = 0
        if status_breakdown.get('approved', {}).get('count', 0) > 0:
            average_ticket = total_value / status_breakdown.get('approved', {}).get('count', 1)
        
        stats = {
            'overview': {
                'total_clients': total_clients,
                'total_sellers': total_sellers,
                'total_quotes': total_quotes,
                'total_revenue': float(total_value),
                'conversion_rate': round(conversion_rate, 2),
                'average_ticket': round(average_ticket, 2)
            },
            'monthly': {
                'quotes': monthly_quotes,
                'revenue': float(monthly_revenue)
            },
            'status_breakdown': status_breakdown
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao obter estatísticas: {str(e)}'}), 500

@dashboard_bp.route('/dashboard/charts/revenue', methods=['GET'])
@verified_required
@role_required('admin', 'seller')
def get_revenue_chart_data():
    """Obtém dados para gráfico de receita"""
    try:
        current_user = get_current_user()
        period = request.args.get('period', 'monthly')  # monthly, weekly, yearly
        
        # Filtros baseados no role
        if current_user.role == 'seller':
            seller = Seller.query.filter_by(user_id=current_user.id).first()
            if not seller:
                return jsonify({'error': 'Perfil de vendedor não encontrado'}), 404
            quote_filter = Quote.seller_id == seller.id
        else:  # admin
            quote_filter = True
        
        # Definir período de análise
        if period == 'yearly':
            # Últimos 5 anos
            start_date = datetime.now() - timedelta(days=5*365)
            group_by = [extract('year', Quote.created_at)]
            date_format = 'year'
        elif period == 'weekly':
            # Últimas 12 semanas
            start_date = datetime.now() - timedelta(weeks=12)
            group_by = [extract('year', Quote.created_at), extract('week', Quote.created_at)]
            date_format = 'week'
        else:  # monthly (padrão)
            # Últimos 12 meses
            start_date = datetime.now() - timedelta(days=365)
            group_by = [extract('year', Quote.created_at), extract('month', Quote.created_at)]
            date_format = 'month'
        
        # Consulta de receita por período
        revenue_data = db.session.query(
            extract('year', Quote.created_at).label('year'),
            extract('month', Quote.created_at).label('month'),
            extract('week', Quote.created_at).label('week'),
            func.sum(Quote.total_price).label('revenue'),
            func.count(Quote.id).label('count')
        ).filter(
            and_(
                quote_filter,
                Quote.status == 'approved',
                Quote.created_at >= start_date
            )
        ).group_by(*group_by).order_by(*group_by).all()
        
        # Formatar dados para o gráfico
        chart_data = []
        for data in revenue_data:
            if date_format == 'year':
                label = str(int(data.year))
            elif date_format == 'week':
                label = f"{int(data.year)}-W{int(data.week)}"
            else:  # month
                label = f"{int(data.year)}-{int(data.month):02d}"
            
            chart_data.append({
                'period': label,
                'revenue': float(data.revenue or 0),
                'count': data.count
            })
        
        return jsonify({
            'success': True,
            'chart_data': chart_data,
            'period': period
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao obter dados do gráfico: {str(e)}'}), 500

@dashboard_bp.route('/dashboard/charts/products', methods=['GET'])
@verified_required
@role_required('admin', 'seller')
def get_products_chart_data():
    """Obtém dados para gráfico de produtos mais vendidos"""
    try:
        current_user = get_current_user()
        
        # Filtros baseados no role
        if current_user.role == 'seller':
            seller = Seller.query.filter_by(user_id=current_user.id).first()
            if not seller:
                return jsonify({'error': 'Perfil de vendedor não encontrado'}), 404
            quote_filter = Quote.seller_id == seller.id
        else:  # admin
            quote_filter = True
        
        # Consulta de produtos por quantidade e receita
        product_data = db.session.query(
            Quote.product_type,
            func.count(Quote.id).label('quantity'),
            func.sum(Quote.total_price).label('revenue')
        ).filter(
            and_(
                quote_filter,
                Quote.status == 'approved'
            )
        ).group_by(Quote.product_type).order_by(func.count(Quote.id).desc()).all()
        
        # Formatar dados para o gráfico
        chart_data = []
        for data in product_data:
            chart_data.append({
                'product_type': data.product_type,
                'quantity': data.quantity,
                'revenue': float(data.revenue or 0),
                'average_price': float(data.revenue or 0) / data.quantity if data.quantity > 0 else 0
            })
        
        return jsonify({
            'success': True,
            'chart_data': chart_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao obter dados de produtos: {str(e)}'}), 500

@dashboard_bp.route('/dashboard/reports/sellers', methods=['GET'])
@verified_required
@role_required('admin')
def get_sellers_report():
    """Relatório de performance dos vendedores (apenas admin)"""
    try:
        # Consulta de performance por vendedor
        seller_performance = db.session.query(
            Seller.id,
            User.name,
            User.email,
            Seller.commission_rate,
            func.count(Quote.id).label('total_quotes'),
            func.sum(
                func.case([(Quote.status == 'approved', 1)], else_=0)
            ).label('approved_quotes'),
            func.sum(
                func.case([(Quote.status == 'approved', Quote.total_price)], else_=0)
            ).label('total_sales'),
            func.sum(
                func.case([(Quote.status == 'pending', 1)], else_=0)
            ).label('pending_quotes')
        ).join(User).outerjoin(Quote).group_by(
            Seller.id, User.name, User.email, Seller.commission_rate
        ).all()
        
        # Formatar dados do relatório
        report_data = []
        for seller in seller_performance:
            total_sales = float(seller.total_sales or 0)
            commission_earned = total_sales * seller.commission_rate
            conversion_rate = (seller.approved_quotes / seller.total_quotes * 100) if seller.total_quotes > 0 else 0
            
            report_data.append({
                'seller_id': seller.id,
                'name': seller.name,
                'email': seller.email,
                'commission_rate': seller.commission_rate,
                'total_quotes': seller.total_quotes,
                'approved_quotes': seller.approved_quotes,
                'pending_quotes': seller.pending_quotes,
                'total_sales': total_sales,
                'commission_earned': round(commission_earned, 2),
                'conversion_rate': round(conversion_rate, 2),
                'average_ticket': round(total_sales / seller.approved_quotes, 2) if seller.approved_quotes > 0 else 0
            })
        
        # Ordenar por total de vendas
        report_data.sort(key=lambda x: x['total_sales'], reverse=True)
        
        return jsonify({
            'success': True,
            'report_data': report_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar relatório de vendedores: {str(e)}'}), 500

@dashboard_bp.route('/dashboard/reports/clients', methods=['GET'])
@verified_required
@role_required('admin', 'seller')
def get_clients_report():
    """Relatório de clientes"""
    try:
        current_user = get_current_user()
        
        # Filtros baseados no role
        if current_user.role == 'seller':
            seller = Seller.query.filter_by(user_id=current_user.id).first()
            if not seller:
                return jsonify({'error': 'Perfil de vendedor não encontrado'}), 404
            quote_filter = Quote.seller_id == seller.id
        else:  # admin
            quote_filter = True
        
        # Consulta de dados dos clientes
        client_data = db.session.query(
            Client.id,
            User.name,
            User.email,
            Client.company_name,
            Client.city,
            Client.state,
            func.count(Quote.id).label('total_quotes'),
            func.sum(
                func.case([(Quote.status == 'approved', Quote.total_price)], else_=0)
            ).label('total_spent'),
            func.max(Quote.created_at).label('last_quote_date')
        ).join(User).outerjoin(Quote).filter(quote_filter).group_by(
            Client.id, User.name, User.email, Client.company_name, Client.city, Client.state
        ).all()
        
        # Formatar dados do relatório
        report_data = []
        for client in client_data:
            report_data.append({
                'client_id': client.id,
                'name': client.name,
                'email': client.email,
                'company_name': client.company_name,
                'city': client.city,
                'state': client.state,
                'total_quotes': client.total_quotes,
                'total_spent': float(client.total_spent or 0),
                'last_quote_date': client.last_quote_date.isoformat() if client.last_quote_date else None,
                'average_order': round(float(client.total_spent or 0) / client.total_quotes, 2) if client.total_quotes > 0 else 0
            })
        
        # Ordenar por total gasto
        report_data.sort(key=lambda x: x['total_spent'], reverse=True)
        
        return jsonify({
            'success': True,
            'report_data': report_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar relatório de clientes: {str(e)}'}), 500

@dashboard_bp.route('/dashboard/reports/financial', methods=['GET'])
@verified_required
@role_required('admin')
def get_financial_report():
    """Relatório financeiro detalhado (apenas admin)"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Definir período padrão (último mês)
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        # Converter strings para datetime
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        
        # Receita total por status
        revenue_by_status = db.session.query(
            Quote.status,
            func.count(Quote.id).label('count'),
            func.sum(Quote.total_price).label('total')
        ).filter(
            and_(
                Quote.created_at >= start_dt,
                Quote.created_at < end_dt
            )
        ).group_by(Quote.status).all()
        
        # Receita por tipo de produto
        revenue_by_product = db.session.query(
            Quote.product_type,
            func.count(Quote.id).label('count'),
            func.sum(Quote.total_price).label('total')
        ).filter(
            and_(
                Quote.created_at >= start_dt,
                Quote.created_at < end_dt,
                Quote.status == 'approved'
            )
        ).group_by(Quote.product_type).all()
        
        # Comissões dos vendedores
        seller_commissions = db.session.query(
            User.name,
            Seller.commission_rate,
            func.sum(Quote.total_price).label('sales'),
            func.sum(Quote.total_price * Seller.commission_rate).label('commission')
        ).join(Seller).join(Quote).filter(
            and_(
                Quote.created_at >= start_dt,
                Quote.created_at < end_dt,
                Quote.status == 'approved'
            )
        ).group_by(User.name, Seller.commission_rate).all()
        
        # Formatar dados
        status_data = [
            {
                'status': item.status,
                'count': item.count,
                'total': float(item.total or 0)
            }
            for item in revenue_by_status
        ]
        
        product_data = [
            {
                'product_type': item.product_type,
                'count': item.count,
                'total': float(item.total or 0)
            }
            for item in revenue_by_product
        ]
        
        commission_data = [
            {
                'seller_name': item.name,
                'commission_rate': item.commission_rate,
                'sales': float(item.sales or 0),
                'commission': float(item.commission or 0)
            }
            for item in seller_commissions
        ]
        
        # Calcular totais
        total_revenue = sum(item['total'] for item in status_data if item['status'] == 'approved')
        total_commissions = sum(item['commission'] for item in commission_data)
        net_revenue = total_revenue - total_commissions
        
        financial_report = {
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'summary': {
                'total_revenue': total_revenue,
                'total_commissions': total_commissions,
                'net_revenue': net_revenue,
                'commission_percentage': (total_commissions / total_revenue * 100) if total_revenue > 0 else 0
            },
            'revenue_by_status': status_data,
            'revenue_by_product': product_data,
            'seller_commissions': commission_data
        }
        
        return jsonify({
            'success': True,
            'financial_report': financial_report
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar relatório financeiro: {str(e)}'}), 500

@dashboard_bp.route('/dashboard/recent-activity', methods=['GET'])
@verified_required
@role_required('admin', 'seller')
def get_recent_activity():
    """Obtém atividades recentes"""
    try:
        current_user = get_current_user()
        limit = request.args.get('limit', 10, type=int)
        
        # Filtros baseados no role
        if current_user.role == 'seller':
            seller = Seller.query.filter_by(user_id=current_user.id).first()
            if not seller:
                return jsonify({'error': 'Perfil de vendedor não encontrado'}), 404
            quote_filter = Quote.seller_id == seller.id
        else:  # admin
            quote_filter = True
        
        # Buscar orçamentos recentes
        recent_quotes = Quote.query.filter(quote_filter).order_by(
            Quote.updated_at.desc()
        ).limit(limit).all()
        
        activities = []
        for quote in recent_quotes:
            activities.append({
                'type': 'quote',
                'id': quote.id,
                'description': f'Orçamento #{quote.id} - {quote.product_type}',
                'status': quote.status,
                'value': quote.total_price,
                'client_name': quote.client.user.name if quote.client else 'N/A',
                'seller_name': quote.seller.user.name if quote.seller else 'N/A',
                'created_at': quote.created_at.isoformat() if quote.created_at else None,
                'updated_at': quote.updated_at.isoformat() if quote.updated_at else None
            })
        
        return jsonify({
            'success': True,
            'activities': activities
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao obter atividades recentes: {str(e)}'}), 500

