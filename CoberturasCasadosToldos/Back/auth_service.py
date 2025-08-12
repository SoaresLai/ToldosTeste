from flask_jwt_extended import create_access_token, create_refresh_token
from src.models.user import User, db
from src.models.client import Client
from src.models.seller import Seller
from src.services.email_service import EmailService
from datetime import datetime
import secrets

class AuthService:
    
    @staticmethod
    def register_user(email, password, name, role='client'):
        """Registra um novo usuário"""
        # Verificar se o email já existe
        if User.query.filter_by(email=email).first():
            return {'error': 'Email já está em uso'}, 400
        
        # Criar novo usuário
        user = User(email=email, name=name, role=role)
        user.set_password(password)
        user.generate_verification_token()
        
        try:
            db.session.add(user)
            db.session.commit()
            
            # Criar perfil específico baseado no role
            if role == 'client':
                client = Client(user_id=user.id)
                db.session.add(client)
            elif role == 'seller':
                seller = Seller(user_id=user.id)
                db.session.add(seller)
            
            db.session.commit()
            
            # Enviar email de verificação
            EmailService.send_verification_email(user)
            
            return {
                'message': 'Usuário registrado com sucesso. Verifique seu email.',
                'user': user.to_dict()
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {'error': f'Erro ao registrar usuário: {str(e)}'}, 500
    
    @staticmethod
    def login_user(email, password):
        """Autentica um usuário"""
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return {'error': 'Email ou senha inválidos'}, 401
        
        if not user.is_verified:
            return {'error': 'Email não verificado. Verifique sua caixa de entrada.'}, 401
        
        # Criar tokens JWT
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return {
            'message': 'Login realizado com sucesso',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }, 200
    
    @staticmethod
    def verify_email(token):
        """Verifica o email do usuário"""
        user = User.query.filter_by(verification_token=token).first()
        
        if not user:
            return {'error': 'Token de verificação inválido'}, 400
        
        user.verify_email()
        
        try:
            db.session.commit()
            return {'message': 'Email verificado com sucesso'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': f'Erro ao verificar email: {str(e)}'}, 500
    
    @staticmethod
    def forgot_password(email):
        """Inicia o processo de recuperação de senha"""
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # Por segurança, não revelar se o email existe
            return {'message': 'Se o email existir, você receberá instruções de recuperação'}, 200
        
        user.generate_reset_token()
        
        try:
            db.session.commit()
            EmailService.send_password_reset_email(user)
            return {'message': 'Se o email existir, você receberá instruções de recuperação'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': 'Erro ao processar solicitação'}, 500
    
    @staticmethod
    def reset_password(token, new_password):
        """Redefine a senha do usuário"""
        user = User.query.filter_by(reset_token=token).first()
        
        if not user or not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
            return {'error': 'Token de reset inválido ou expirado'}, 400
        
        user.set_password(new_password)
        user.reset_token = None
        user.reset_token_expires = None
        
        try:
            db.session.commit()
            return {'message': 'Senha redefinida com sucesso'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': f'Erro ao redefinir senha: {str(e)}'}, 500
    
    @staticmethod
    def get_user_profile(user_id):
        """Obtém o perfil completo do usuário"""
        user = User.query.get(user_id)
        
        if not user:
            return {'error': 'Usuário não encontrado'}, 404
        
        profile = user.to_dict()
        
        # Adicionar dados específicos do role
        if user.role == 'client' and user.client:
            profile['client_data'] = user.client.to_dict()
        elif user.role == 'seller' and user.seller:
            profile['seller_data'] = user.seller.to_dict()
        
        return profile, 200

