from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from src.models.user import db

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    materials = db.Column(db.Text, nullable=False)  # JSON string
    dimensions_config = db.Column(db.Text, nullable=False)  # JSON string
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_materials(self):
        """Retorna os materiais como dicionário Python"""
        try:
            return json.loads(self.materials) if self.materials else {}
        except json.JSONDecodeError:
            return {}
    
    def set_materials(self, materials_dict):
        """Define os materiais a partir de um dicionário Python"""
        self.materials = json.dumps(materials_dict)
    
    def get_dimensions_config(self):
        """Retorna a configuração de dimensões como dicionário Python"""
        try:
            return json.loads(self.dimensions_config) if self.dimensions_config else {}
        except json.JSONDecodeError:
            return {}
    
    def set_dimensions_config(self, config_dict):
        """Define a configuração de dimensões a partir de um dicionário Python"""
        self.dimensions_config = json.dumps(config_dict)
    
    def calculate_price(self, dimensions, selected_materials=None):
        """Calcula o preço baseado nas dimensões e materiais selecionados"""
        base_area = dimensions.get('width', 0) * dimensions.get('length', 0)
        price = self.base_price * base_area
        
        # Adicionar custos de materiais específicos
        if selected_materials:
            materials_config = self.get_materials()
            for material, quantity in selected_materials.items():
                if material in materials_config:
                    price += materials_config[material].get('price_per_unit', 0) * quantity
        
        return round(price, 2)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'base_price': self.base_price,
            'materials': self.get_materials(),
            'dimensions_config': self.get_dimensions_config(),
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Product {self.name}>'

