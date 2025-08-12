from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.services.auth_service import AuthService
from src.utils.decorators import validate_json
from src.utils.validators import Validators

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@validate_json('email', 'password', 'name')
def register():
    """Registra um novo usuário"""
    data = request.get_json()
    
    # Validações
    email_valid, email_error = Validators.validate_email_format(data['email'])
    if not email_valid:
        return jsonify({'error': f'Email inválido: {email_error}'}), 400
    
    password_valid, password_error = Validators.validate_password_strength(data['password'])
    if not password_valid:
        return jsonify({'error': password_error}), 400
    
    role = data.get('role', 'client')
    role_valid, role_error = Validators.validate_role(role)
    if not role_valid:
        return jsonify({'error': role_error}), 400
    
    # Registrar usuário
    result, status_code = AuthService.register_user(
        email=data['email'],
        password=data['password'],
        name=data['name'],
        role=role
    )
    
    return jsonify(result), status_code

@auth_bp.route('/login', methods=['POST'])
@validate_json('email', 'password')
def login():
    """Autentica um usuário"""
    data = request.get_json()
    
    result, status_code = AuthService.login_user(
        email=data['email'],
        password=data['password']
    )
    
    return jsonify(result), status_code

@auth_bp.route('/verify-email/<token>', methods=['GET'])
def verify_email(token):
    """Verifica o email do usuário"""
    result, status_code = AuthService.verify_email(token)
    
    if status_code == 200:
        # Retornar uma página HTML simples de sucesso
        return """
        <html>
        <head><title>Email Verificado</title></head>
        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
            <h1 style="color: green;">✓ Email Verificado com Sucesso!</h1>
            <p>Seu email foi verificado. Você já pode fazer login no sistema.</p>
            <p><a href="/" style="color: #007bff;">Voltar ao Sistema</a></p>
        </body>
        </html>
        """
    else:
        return f"""
        <html>
        <head><title>Erro na Verificação</title></head>
        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
            <h1 style="color: red;">✗ Erro na Verificação</h1>
            <p>{result.get('error', 'Token inválido')}</p>
            <p><a href="/" style="color: #007bff;">Voltar ao Sistema</a></p>
        </body>
        </html>
        """, status_code

@auth_bp.route('/forgot-password', methods=['POST'])
@validate_json('email')
def forgot_password():
    """Inicia o processo de recuperação de senha"""
    data = request.get_json()
    
    result, status_code = AuthService.forgot_password(data['email'])
    return jsonify(result), status_code

@auth_bp.route('/reset-password/<token>', methods=['GET'])
def reset_password_form(token):
    """Exibe formulário de reset de senha"""
    return f"""
    <html>
    <head>
        <title>Redefinir Senha</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 400px; margin: 50px auto; padding: 20px; }}
            .form-group {{ margin-bottom: 15px; }}
            label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
            input {{ width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }}
            button {{ background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; width: 100%; }}
            button:hover {{ background-color: #0056b3; }}
            .error {{ color: red; margin-top: 10px; }}
            .success {{ color: green; margin-top: 10px; }}
        </style>
    </head>
    <body>
        <h2>Redefinir Senha</h2>
        <form id="resetForm">
            <div class="form-group">
                <label for="password">Nova Senha:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <div class="form-group">
                <label for="confirmPassword">Confirmar Senha:</label>
                <input type="password" id="confirmPassword" name="confirmPassword" required>
            </div>
            <button type="submit">Redefinir Senha</button>
        </form>
        <div id="message"></div>
        
        <script>
            document.getElementById('resetForm').addEventListener('submit', async function(e) {{
                e.preventDefault();
                
                const password = document.getElementById('password').value;
                const confirmPassword = document.getElementById('confirmPassword').value;
                const messageDiv = document.getElementById('message');
                
                if (password !== confirmPassword) {{
                    messageDiv.innerHTML = '<div class="error">As senhas não coincidem</div>';
                    return;
                }}
                
                try {{
                    const response = await fetch('/api/auth/reset-password', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json'
                        }},
                        body: JSON.stringify({{
                            token: '{token}',
                            password: password
                        }})
                    }});
                    
                    const result = await response.json();
                    
                    if (response.ok) {{
                        messageDiv.innerHTML = '<div class="success">' + result.message + '</div>';
                        document.getElementById('resetForm').style.display = 'none';
                    }} else {{
                        messageDiv.innerHTML = '<div class="error">' + result.error + '</div>';
                    }}
                }} catch (error) {{
                    messageDiv.innerHTML = '<div class="error">Erro ao redefinir senha</div>';
                }}
            }});
        </script>
    </body>
    </html>
    """

@auth_bp.route('/reset-password', methods=['POST'])
@validate_json('token', 'password')
def reset_password():
    """Redefine a senha do usuário"""
    data = request.get_json()
    
    # Validar força da senha
    password_valid, password_error = Validators.validate_password_strength(data['password'])
    if not password_valid:
        return jsonify({'error': password_error}), 400
    
    result, status_code = AuthService.reset_password(
        token=data['token'],
        new_password=data['password']
    )
    
    return jsonify(result), status_code

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Obtém o perfil do usuário atual"""
    current_user_id = get_jwt_identity()
    result, status_code = AuthService.get_user_profile(current_user_id)
    return jsonify(result), status_code

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Atualiza o perfil do usuário atual"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # TODO: Implementar atualização de perfil
    return jsonify({'message': 'Funcionalidade em desenvolvimento'}), 501

