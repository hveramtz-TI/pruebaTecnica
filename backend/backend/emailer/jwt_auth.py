import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import authenticate
from .models import CustomUser

class JWTAuthentication:
    """Clase para manejar autenticación JWT personalizada"""
    
    @staticmethod
    def generate_tokens(user):
        """Genera access token y refresh token para el usuario"""
        now = datetime.utcnow()
        
        # Access token (20 minutos)
        access_payload = {
            'user_id': user.id,
            'email': user.email,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'exp': now + timedelta(minutes=20),
            'iat': now,
            'type': 'access'
        }
        
        # Refresh token (7 días)
        refresh_payload = {
            'user_id': user.id,
            'exp': now + timedelta(days=7),
            'iat': now,
            'type': 'refresh'
        }
        
        secret_key = getattr(settings, 'JWT_SECRET_KEY', settings.SECRET_KEY)
        
        access_token = jwt.encode(access_payload, secret_key, algorithm='HS256')
        refresh_token = jwt.encode(refresh_payload, secret_key, algorithm='HS256')
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': 1200,  # 20 minutos en segundos
            'token_type': 'Bearer'
        }
    
    @staticmethod
    def verify_token(token, token_type='access'):
        """Verifica y decodifica un token JWT"""
        try:
            secret_key = getattr(settings, 'JWT_SECRET_KEY', settings.SECRET_KEY)
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            
            # Verificar tipo de token
            if payload.get('type') != token_type:
                return None
                
            # Verificar si el usuario existe y está activo
            try:
                user = CustomUser.objects.get(id=payload['user_id'])
                if not user.is_active:
                    return None
                return user, payload
            except CustomUser.DoesNotExist:
                return None
                
        except jwt.ExpiredSignatureError:
            return None  # Token expirado
        except jwt.InvalidTokenError:
            return None  # Token inválido
    
    @staticmethod
    def refresh_access_token(refresh_token):
        """Genera un nuevo access token usando el refresh token"""
        result = JWTAuthentication.verify_token(refresh_token, 'refresh')
        if not result:
            return None
            
        user, payload = result
        
        # Generar nuevo access token
        now = datetime.utcnow()
        access_payload = {
            'user_id': user.id,
            'email': user.email,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'exp': now + timedelta(minutes=20),
            'iat': now,
            'type': 'access'
        }
        
        secret_key = getattr(settings, 'JWT_SECRET_KEY', settings.SECRET_KEY)
        access_token = jwt.encode(access_payload, secret_key, algorithm='HS256')
        
        return {
            'access_token': access_token,
            'expires_in': 1200,  # 20 minutos
            'token_type': 'Bearer'
        }

def authenticate_admin_user(email, password):
    """Autentica un usuario administrador"""
    user = authenticate(username=email, password=password)
    
    if user and user.is_active:
        # Verificar que sea administrador (staff o superuser)
        if user.is_staff or user.is_superuser:
            return user
    return None