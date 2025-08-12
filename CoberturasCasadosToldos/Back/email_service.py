from flask_mail import Mail, Message
from flask import current_app, url_for
import os

class EmailService:
    mail = None
    
    @classmethod
    def init_app(cls, app):
        """Inicializa o serviço de email com a aplicação Flask"""
        cls.mail = Mail(app)
    
    @classmethod
    def send_verification_email(cls, user):
        """Envia email de verificação para o usuário"""
        if not cls.mail:
            print(f"Email service not initialized. Verification token for {user.email}: {user.verification_token}")
            return
        
        try:
            msg = Message(
                'Verificação de Email - Sistema de Toldos',
                sender=current_app.config.get('MAIL_DEFAULT_SENDER'),
                recipients=[user.email]
            )
            
            verification_url = url_for('auth.verify_email', token=user.verification_token, _external=True)
            
            msg.body = f"""
            Olá {user.name},
            
            Obrigado por se registrar no Sistema de Toldos!
            
            Para verificar seu email, clique no link abaixo:
            {verification_url}
            
            Se você não se registrou em nosso sistema, ignore este email.
            
            Atenciosamente,
            Equipe Sistema de Toldos
            """
            
            msg.html = f"""
            <h2>Verificação de Email</h2>
            <p>Olá <strong>{user.name}</strong>,</p>
            <p>Obrigado por se registrar no Sistema de Toldos!</p>
            <p>Para verificar seu email, clique no botão abaixo:</p>
            <p><a href="{verification_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Verificar Email</a></p>
            <p>Ou copie e cole este link em seu navegador:</p>
            <p>{verification_url}</p>
            <p>Se você não se registrou em nosso sistema, ignore este email.</p>
            <p>Atenciosamente,<br>Equipe Sistema de Toldos</p>
            """
            
            cls.mail.send(msg)
            print(f"Verification email sent to {user.email}")
            
        except Exception as e:
            print(f"Error sending verification email to {user.email}: {str(e)}")
            # Em desenvolvimento, imprimir o token no console
            print(f"Verification token for {user.email}: {user.verification_token}")
    
    @classmethod
    def send_password_reset_email(cls, user):
        """Envia email de recuperação de senha"""
        if not cls.mail:
            print(f"Email service not initialized. Reset token for {user.email}: {user.reset_token}")
            return
        
        try:
            msg = Message(
                'Recuperação de Senha - Sistema de Toldos',
                sender=current_app.config.get('MAIL_DEFAULT_SENDER'),
                recipients=[user.email]
            )
            
            reset_url = url_for('auth.reset_password_form', token=user.reset_token, _external=True)
            
            msg.body = f"""
            Olá {user.name},
            
            Você solicitou a recuperação de sua senha no Sistema de Toldos.
            
            Para redefinir sua senha, clique no link abaixo:
            {reset_url}
            
            Este link expira em 1 hora.
            
            Se você não solicitou esta recuperação, ignore este email.
            
            Atenciosamente,
            Equipe Sistema de Toldos
            """
            
            msg.html = f"""
            <h2>Recuperação de Senha</h2>
            <p>Olá <strong>{user.name}</strong>,</p>
            <p>Você solicitou a recuperação de sua senha no Sistema de Toldos.</p>
            <p>Para redefinir sua senha, clique no botão abaixo:</p>
            <p><a href="{reset_url}" style="background-color: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Redefinir Senha</a></p>
            <p>Ou copie e cole este link em seu navegador:</p>
            <p>{reset_url}</p>
            <p><strong>Este link expira em 1 hora.</strong></p>
            <p>Se você não solicitou esta recuperação, ignore este email.</p>
            <p>Atenciosamente,<br>Equipe Sistema de Toldos</p>
            """
            
            cls.mail.send(msg)
            print(f"Password reset email sent to {user.email}")
            
        except Exception as e:
            print(f"Error sending password reset email to {user.email}: {str(e)}")
            # Em desenvolvimento, imprimir o token no console
            print(f"Reset token for {user.email}: {user.reset_token}")
    
    @classmethod
    def send_quote_notification(cls, quote, recipient_email, recipient_name):
        """Envia notificação de novo orçamento"""
        if not cls.mail:
            print(f"Email service not initialized. Quote notification for {recipient_email}")
            return
        
        try:
            msg = Message(
                f'Novo Orçamento #{quote.id} - Sistema de Toldos',
                sender=current_app.config.get('MAIL_DEFAULT_SENDER'),
                recipients=[recipient_email]
            )
            
            msg.body = f"""
            Olá {recipient_name},
            
            Um novo orçamento foi criado no Sistema de Toldos.
            
            Detalhes do Orçamento:
            - ID: #{quote.id}
            - Produto: {quote.product_type}
            - Valor: R$ {quote.total_price:.2f}
            - Status: {quote.status}
            
            Acesse o sistema para mais detalhes.
            
            Atenciosamente,
            Equipe Sistema de Toldos
            """
            
            cls.mail.send(msg)
            print(f"Quote notification sent to {recipient_email}")
            
        except Exception as e:
            print(f"Error sending quote notification to {recipient_email}: {str(e)}")

