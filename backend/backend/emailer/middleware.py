from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from .jwt_utils import JWTService

class JWTAuthenticationMiddleware(MiddlewareMixin):
    """Middleware para autenticación JWT"""
    
    def process_request(self, request):
        # Rutas que requieren autenticación de admin
        protected_paths = [
            '/api/admin/dashboard/',
            '/api/admin/participants/',
            '/api/admin/select-winner/',
            '/api/admin/contest-stats/',
        ]
        
        print(f"DEBUG Middleware - Ruta solicitada: {request.path}")
        
        # Verificar si la ruta requiere autenticación
        if not any(request.path.startswith(path) for path in protected_paths):
            print(f"DEBUG Middleware - Ruta no protegida, permitiendo acceso")
            return None
        
        print(f"DEBUG Middleware - Ruta protegida, verificando token")
        
        # Obtener token del header Authorization
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        print(f"DEBUG Middleware - Auth header: {auth_header}")
        
        if not auth_header or not auth_header.startswith('Bearer '):
            print(f"DEBUG Middleware - Token no válido o ausente")
            return JsonResponse({
                'error': 'Token de autenticación requerido',
                'code': 'TOKEN_REQUIRED'
            }, status=401)
        
        token = auth_header.split(' ')[1]
        print(f"DEBUG Middleware - Token extraído: {token}")
        
        # Verificar token
        payload, error = JWTService.decode_token(token)
        if error or not payload:
            return JsonResponse({
                'error': 'Token inválido o expirado',
                'code': 'INVALID_TOKEN'
            }, status=401)
        
        # Obtener usuario del payload
        try:
            from .models import CustomUser
            user = CustomUser.objects.get(id=payload['user_id'])
            if not user.is_active:
                return JsonResponse({
                    'error': 'Usuario inactivo',
                    'code': 'USER_INACTIVE'
                }, status=401)
        except CustomUser.DoesNotExist:
            return JsonResponse({
                'error': 'Usuario no encontrado',
                'code': 'USER_NOT_FOUND'
            }, status=401)
        
        # Verificar que sea administrador
        if not (user.is_staff or user.is_superuser):
            print(f"DEBUG Middleware - Usuario sin permisos de admin: {user.email}")
            return JsonResponse({
                'error': 'Acceso denegado. Se requieren permisos de administrador',
                'code': 'ACCESS_DENIED'
            }, status=403)
        
        print(f"DEBUG Middleware - Token válido para usuario admin: {user.email}")
        
        # Agregar usuario al request
        request.user = user
        request.jwt_payload = payload
        
        return None