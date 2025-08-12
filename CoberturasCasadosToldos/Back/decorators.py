from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User

def role_required(*allowed_roles):
    """Decorator para verificar se o usuário tem o role necessário"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user:
                return jsonify({'error': 'Usuário não encontrado'}), 404
            
            if user.role not in allowed_roles:
                return jsonify({'error': 'Acesso negado. Permissões insuficientes.'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def verified_required(f):
    """Decorator para verificar se o usuário tem email verificado"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        if not user.is_verified:
            return jsonify({'error': 'Email não verificado. Verifique sua caixa de entrada.'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Utilitário para obter o usuário atual"""
    current_user_id = get_jwt_identity()
    return User.query.get(current_user_id) if current_user_id else None

def validate_json(*required_fields):
    """Decorator para validar campos obrigatórios no JSON"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Content-Type deve ser application/json'}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Dados JSON são obrigatórios'}), 400
            
            missing_fields = [field for field in required_fields if field not in data or not data[field]]
            if missing_fields:
                return jsonify({
                    'error': f'Campos obrigatórios ausentes: {", ".join(missing_fields)}'
                }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

