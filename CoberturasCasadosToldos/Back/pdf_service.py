from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PyPDF2 import PdfWriter, PdfReader
import io
import os
from datetime import datetime
from typing import Dict, Any

class PDFService:
    """Serviço para geração de PDFs de orçamentos com proteção por senha"""
    
    @staticmethod
    def generate_quote_pdf(quote_data: Dict[str, Any], password: str = None) -> bytes:
        """Gera PDF do orçamento com proteção opcional por senha"""
        
        # Criar buffer em memória
        buffer = io.BytesIO()
        
        # Configurar documento
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Obter estilos
        styles = getSampleStyleSheet()
        
        # Criar estilos personalizados
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2E86AB')
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#2E86AB')
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=6
        )
        
        # Construir conteúdo do PDF
        story = []
        
        # Cabeçalho da empresa
        story.append(Paragraph("COBERTURAS CASADOS TOLDOS", title_style))
        story.append(Paragraph("Soluções em Toldos e Coberturas", normal_style))
        story.append(Spacer(1, 20))
        
        # Informações do orçamento
        story.append(Paragraph("ORÇAMENTO", heading_style))
        
        quote_info = [
            ['Número do Orçamento:', f"#{quote_data.get('id', 'N/A')}"],
            ['Data:', datetime.now().strftime('%d/%m/%Y')],
            ['Status:', quote_data.get('status', 'N/A').upper()],
            ['Validade:', '30 dias']
        ]
        
        quote_table = Table(quote_info, colWidths=[4*cm, 6*cm])
        quote_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(quote_table)
        story.append(Spacer(1, 20))
        
        # Dados do cliente
        story.append(Paragraph("DADOS DO CLIENTE", heading_style))
        
        client_data = quote_data.get('client', {})
        client_info = [
            ['Nome:', client_data.get('user', {}).get('name', 'N/A')],
            ['Email:', client_data.get('user', {}).get('email', 'N/A')],
            ['Empresa:', client_data.get('company_name', 'N/A')],
            ['Telefone:', client_data.get('phone', 'N/A')],
            ['Endereço:', client_data.get('address', 'N/A')],
            ['Cidade/Estado:', f"{client_data.get('city', 'N/A')} - {client_data.get('state', 'N/A')}"]
        ]
        
        client_table = Table(client_info, colWidths=[3*cm, 7*cm])
        client_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(client_table)
        story.append(Spacer(1, 20))
        
        # Especificações do produto
        story.append(Paragraph("ESPECIFICAÇÕES DO PRODUTO", heading_style))
        
        dimensions = quote_data.get('dimensions', {})
        materials = quote_data.get('materials', {})
        
        product_info = [
            ['Tipo de Produto:', quote_data.get('product_type', 'N/A')],
            ['Largura:', f"{dimensions.get('width', 0):.2f} m"],
            ['Comprimento:', f"{dimensions.get('length', 0):.2f} m"],
            ['Altura:', f"{dimensions.get('height', 2.5):.2f} m"],
            ['Área Total:', f"{dimensions.get('width', 0) * dimensions.get('length', 0):.2f} m²"]
        ]
        
        # Adicionar materiais se disponíveis
        if materials:
            for material, value in materials.items():
                if value:
                    product_info.append([f"{material.replace('_', ' ').title()}:", str(value)])
        
        product_table = Table(product_info, colWidths=[4*cm, 6*cm])
        product_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        story.append(product_table)
        story.append(Spacer(1, 20))
        
        # Valor do orçamento
        story.append(Paragraph("VALOR DO ORÇAMENTO", heading_style))
        
        price_data = [
            ['Descrição', 'Quantidade', 'Valor Unitário', 'Valor Total'],
            [
                quote_data.get('product_type', 'Produto'),
                f"{dimensions.get('width', 0) * dimensions.get('length', 0):.2f} m²",
                f"R$ {quote_data.get('total_price', 0) / (dimensions.get('width', 1) * dimensions.get('length', 1)):.2f}",
                f"R$ {quote_data.get('total_price', 0):.2f}"
            ]
        ]
        
        price_table = Table(price_data, colWidths=[6*cm, 2*cm, 3*cm, 3*cm])
        price_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(price_table)
        story.append(Spacer(1, 20))
        
        # Total
        total_style = ParagraphStyle(
            'Total',
            parent=styles['Normal'],
            fontSize=16,
            alignment=TA_RIGHT,
            textColor=colors.HexColor('#2E86AB'),
            fontName='Helvetica-Bold'
        )
        
        story.append(Paragraph(f"<b>VALOR TOTAL: R$ {quote_data.get('total_price', 0):.2f}</b>", total_style))
        story.append(Spacer(1, 30))
        
        # Observações
        if quote_data.get('notes'):
            story.append(Paragraph("OBSERVAÇÕES", heading_style))
            story.append(Paragraph(quote_data.get('notes'), normal_style))
            story.append(Spacer(1, 20))
        
        # Condições comerciais
        story.append(Paragraph("CONDIÇÕES COMERCIAIS", heading_style))
        
        conditions = [
            "• Prazo de entrega: 15 a 20 dias úteis após aprovação do projeto",
            "• Forma de pagamento: 50% na aprovação e 50% na entrega",
            "• Garantia: 12 meses contra defeitos de fabricação",
            "• Instalação inclusa no valor do orçamento",
            "• Orçamento válido por 30 dias"
        ]
        
        for condition in conditions:
            story.append(Paragraph(condition, normal_style))
        
        story.append(Spacer(1, 30))
        
        # Rodapé
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.grey
        )
        
        story.append(Paragraph("Coberturas Casados Toldos - Telefone: (11) 99999-9999 - Email: contato@casadostoldos.com.br", footer_style))
        
        # Gerar PDF
        doc.build(story)
        
        # Se senha foi fornecida, proteger o PDF
        if password:
            return PDFService._protect_pdf_with_password(buffer.getvalue(), password)
        
        return buffer.getvalue()
    
    @staticmethod
    def _protect_pdf_with_password(pdf_bytes: bytes, password: str) -> bytes:
        """Protege PDF com senha usando PyPDF2"""
        try:
            # Ler PDF original
            pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
            pdf_writer = PdfWriter()
            
            # Copiar todas as páginas
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)
            
            # Adicionar proteção por senha
            pdf_writer.encrypt(password)
            
            # Salvar PDF protegido
            output_buffer = io.BytesIO()
            pdf_writer.write(output_buffer)
            
            return output_buffer.getvalue()
            
        except Exception as e:
            print(f"Erro ao proteger PDF: {str(e)}")
            # Retornar PDF original se houver erro
            return pdf_bytes
    
    @staticmethod
    def generate_report_pdf(report_data: Dict[str, Any], report_type: str) -> bytes:
        """Gera PDF de relatórios"""
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        
        styles = getSampleStyleSheet()
        story = []
        
        # Título do relatório
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2E86AB')
        )
        
        report_titles = {
            'sellers': 'RELATÓRIO DE VENDEDORES',
            'clients': 'RELATÓRIO DE CLIENTES',
            'financial': 'RELATÓRIO FINANCEIRO'
        }
        
        story.append(Paragraph(report_titles.get(report_type, 'RELATÓRIO'), title_style))
        story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 30))
        
        # Conteúdo específico por tipo de relatório
        if report_type == 'sellers':
            PDFService._add_sellers_report_content(story, report_data, styles)
        elif report_type == 'clients':
            PDFService._add_clients_report_content(story, report_data, styles)
        elif report_type == 'financial':
            PDFService._add_financial_report_content(story, report_data, styles)
        
        doc.build(story)
        return buffer.getvalue()
    
    @staticmethod
    def _add_sellers_report_content(story, report_data, styles):
        """Adiciona conteúdo do relatório de vendedores"""
        
        # Cabeçalho da tabela
        table_data = [
            ['Vendedor', 'Total Orçamentos', 'Aprovados', 'Vendas (R$)', 'Comissão (R$)', 'Taxa Conversão']
        ]
        
        # Dados dos vendedores
        for seller in report_data.get('report_data', []):
            table_data.append([
                seller['name'],
                str(seller['total_quotes']),
                str(seller['approved_quotes']),
                f"R$ {seller['total_sales']:.2f}",
                f"R$ {seller['commission_earned']:.2f}",
                f"{seller['conversion_rate']:.1f}%"
            ])
        
        # Criar tabela
        table = Table(table_data, colWidths=[4*cm, 2*cm, 2*cm, 2.5*cm, 2.5*cm, 2*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(table)
    
    @staticmethod
    def _add_clients_report_content(story, report_data, styles):
        """Adiciona conteúdo do relatório de clientes"""
        
        table_data = [
            ['Cliente', 'Empresa', 'Cidade', 'Total Orçamentos', 'Total Gasto (R$)']
        ]
        
        for client in report_data.get('report_data', []):
            table_data.append([
                client['name'],
                client['company_name'] or 'N/A',
                client['city'] or 'N/A',
                str(client['total_quotes']),
                f"R$ {client['total_spent']:.2f}"
            ])
        
        table = Table(table_data, colWidths=[4*cm, 3*cm, 3*cm, 2*cm, 3*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(table)
    
    @staticmethod
    def _add_financial_report_content(story, report_data, styles):
        """Adiciona conteúdo do relatório financeiro"""
        
        financial_data = report_data.get('financial_report', {})
        summary = financial_data.get('summary', {})
        
        # Resumo financeiro
        summary_data = [
            ['Receita Total', f"R$ {summary.get('total_revenue', 0):.2f}"],
            ['Total Comissões', f"R$ {summary.get('total_commissions', 0):.2f}"],
            ['Receita Líquida', f"R$ {summary.get('net_revenue', 0):.2f}"],
            ['% Comissões', f"{summary.get('commission_percentage', 0):.1f}%"]
        ]
        
        summary_table = Table(summary_data, colWidths=[6*cm, 4*cm])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F0F0F0')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Receita por produto
        story.append(Paragraph("Receita por Produto", styles['Heading2']))
        
        product_data = [['Produto', 'Quantidade', 'Total (R$)']]
        for item in financial_data.get('revenue_by_product', []):
            product_data.append([
                item['product_type'],
                str(item['count']),
                f"R$ {item['total']:.2f}"
            ])
        
        product_table = Table(product_data, colWidths=[6*cm, 3*cm, 3*cm])
        product_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(product_table)

