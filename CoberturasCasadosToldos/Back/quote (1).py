from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from src.models.user import db

class Quote(db.Model):
    __tablename__ = 'quotes'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('sellers.id'), nullable=False)
    product_type = db.Column(db.String(100), nullable=False)
    dimensions = db.Column(db.Text, nullable=False)  # JSON string
    materials = db.Column(db.Text, nullable=False)   # JSON string
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    pdf_password = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_dimensions(self):
        """Retorna as dimensões como dicionário Python"""
        try:
            return json.loads(self.dimensions) if self.dimensions else {}
        except json.JSONDecodeError:
            return {}
    
    def set_dimensions(self, dimensions_dict):
        """Define as dimensões a partir de um dicionário Python"""
        self.dimensions = json.dumps(dimensions_dict)
    
    def get_materials(self):
        """Retorna os materiais como dicionário Python"""
        try:
            return json.loads(self.materials) if self.materials else {}
        except json.JSONDecodeError:
            return {}
    
    def set_materials(self, materials_dict):
        """Define os materiais a partir de um dicionário Python"""
        self.materials = json.dumps(materials_dict)
    
    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'seller_id': self.seller_id,
            'product_type': self.product_type,
            'dimensions': self.get_dimensions(),
            'materials': self.get_materials(),
            'total_price': self.total_price,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'client': self.client.to_dict() if self.client else None,
            'seller': self.seller.to_dict() if self.seller else None
        }
    
    def __repr__(self):
        return f'<Quote {self.id} - {self.product_type}>'

