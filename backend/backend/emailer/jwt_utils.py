import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()

class JWTService:
    """Servicio para manejar tokens JWT"""
    
    @staticmethod
    def generate_token(user, expires_in_minutes=20):
        """
        Genera un token JWT para el usuario con expiración personalizada
        """
        now = timezone.now()
        exp_time = now + timedelta(minutes=expires_in_minutes)
        
        print(f"DEBUG JWT - Generando token para usuario {user.id}")
        print(f"DEBUG JWT - Fecha actual: {now}")
        print(f"DEBUG JWT - Fecha expiración: {exp_time}")
        print(f"DEBUG JWT - Timestamp actual: {now.timestamp()}")
        print(f"DEBUG JWT - Timestamp expiración: {exp_time.timestamp()}")
        
        payload = {
            'user_id': user.id,
            'email': user.email,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'exp': exp_time.timestamp(),  # Convertir a timestamp explícitamente
            'iat': now.timestamp(),      # Convertir a timestamp explícitamente
            'jti': str(uuid.uuid4())     # JWT ID único para poder invalidar tokens
        }
        
        print(f"DEBUG JWT - Payload completo: {payload}")
        
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        print(f"DEBUG JWT - Token generado: {token}")
        return token
    
    @staticmethod
    def decode_token(token):
        """
        Decodifica y valida un token JWT
        """
        try:
            print(f"DEBUG JWT - Intentando decodificar token: {token}")
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            print(f"DEBUG JWT - Token decodificado exitosamente: {payload}")
            return payload, None
        except jwt.ExpiredSignatureError as e:
            print(f"DEBUG JWT - Token expirado: {e}")
            return None, 'Token ha expirado'
        except jwt.InvalidTokenError as e:
            print(f"DEBUG JWT - Token inválido: {e}")
            return None, 'Token inválido'
        except Exception as e:
            print(f"DEBUG JWT - Error inesperado: {e}")
            return None, f'Error inesperado: {str(e)}'
    
    @staticmethod
    def get_user_from_token(token):
        """
        Obtiene el usuario desde un token JWT válido
        """
        payload, error = JWTService.decode_token(token)
        if error:
            return None, error
        
        try:
            user = User.objects.get(id=payload['user_id'])
            return user, None
        except User.DoesNotExist:
            return None, 'Usuario no encontrado'
    
    @staticmethod
    def is_token_expired(token):
        """
        Verifica si un token está expirado
        """
        payload, error = JWTService.decode_token(token)
        if error:
            return True
        
        exp_timestamp = payload.get('exp')
        if not exp_timestamp:
            return True
        
        exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        return timezone.now() > exp_datetime

# Lista en memoria para tokens invalidados (en producción usar Redis o DB)
BLACKLISTED_TOKENS = set()

class TokenBlacklistService:
    """Servicio para manejar tokens invalidados"""
    
    @staticmethod
    def blacklist_token(token):
        """Agrega un token a la lista negra"""
        payload, error = JWTService.decode_token(token)
        if not error and payload:
            jti = payload.get('jti')
            if jti:
                BLACKLISTED_TOKENS.add(jti)
                return True
        return False
    
    @staticmethod
    def is_token_blacklisted(token):
        """Verifica si un token está en la lista negra"""
        payload, error = JWTService.decode_token(token)
        if error or not payload:
            return True
        
        jti = payload.get('jti')
        return jti in BLACKLISTED_TOKENS if jti else True