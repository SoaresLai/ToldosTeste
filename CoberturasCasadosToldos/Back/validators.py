import re
from email_validator import validate_email, EmailNotValidError

class Validators:
    
    @staticmethod
    def validate_email_format(email):
        """Valida o formato do email"""
        try:
            validate_email(email)
            return True, None
        except EmailNotValidError as e:
            return False, str(e)
    
    @staticmethod
    def validate_password_strength(password):
        """Valida a força da senha"""
        if len(password) < 8:
            return False, "A senha deve ter pelo menos 8 caracteres"
        
        if not re.search(r"[A-Z]", password):
            return False, "A senha deve conter pelo menos uma letra maiúscula"
        
        if not re.search(r"[a-z]", password):
            return False, "A senha deve conter pelo menos uma letra minúscula"
        
        if not re.search(r"\d", password):
            return False, "A senha deve conter pelo menos um número"
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False, "A senha deve conter pelo menos um caractere especial"
        
        return True, None
    
    @staticmethod
    def validate_phone(phone):
        """Valida o formato do telefone brasileiro"""
        if not phone:
            return True, None  # Telefone é opcional
        
        # Remove caracteres não numéricos
        phone_clean = re.sub(r'\D', '', phone)
        
        # Verifica se tem 10 ou 11 dígitos (com DDD)
        if len(phone_clean) not in [10, 11]:
            return False, "Telefone deve ter 10 ou 11 dígitos (incluindo DDD)"
        
        # Verifica se o DDD é válido (11-99)
        ddd = phone_clean[:2]
        if not (11 <= int(ddd) <= 99):
            return False, "DDD inválido"
        
        return True, None
    
    @staticmethod
    def validate_cep(cep):
        """Valida o formato do CEP brasileiro"""
        if not cep:
            return True, None  # CEP é opcional
        
        # Remove caracteres não numéricos
        cep_clean = re.sub(r'\D', '', cep)
        
        # Verifica se tem 8 dígitos
        if len(cep_clean) != 8:
            return False, "CEP deve ter 8 dígitos"
        
        return True, None
    
    @staticmethod
    def validate_dimensions(dimensions):
        """Valida as dimensões do produto"""
        required_fields = ['width', 'length']
        
        for field in required_fields:
            if field not in dimensions:
                return False, f"Campo '{field}' é obrigatório nas dimensões"
            
            try:
                value = float(dimensions[field])
                if value <= 0:
                    return False, f"'{field}' deve ser um valor positivo"
            except (ValueError, TypeError):
                return False, f"'{field}' deve ser um número válido"
        
        return True, None
    
    @staticmethod
    def validate_price(price):
        """Valida o preço"""
        try:
            price_float = float(price)
            if price_float < 0:
                return False, "Preço não pode ser negativo"
            return True, None
        except (ValueError, TypeError):
            return False, "Preço deve ser um número válido"
    
    @staticmethod
    def validate_role(role):
        """Valida o role do usuário"""
        valid_roles = ['admin', 'seller', 'client']
        if role not in valid_roles:
            return False, f"Role deve ser um dos seguintes: {', '.join(valid_roles)}"
        return True, None
    
    @staticmethod
    def validate_status(status):
        """Valida o status do orçamento"""
        valid_statuses = ['pending', 'approved', 'rejected', 'completed']
        if status not in valid_statuses:
            return False, f"Status deve ser um dos seguintes: {', '.join(valid_statuses)}"
        return True, None

