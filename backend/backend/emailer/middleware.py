from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from .jwt_auth import JWTAuthentication

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
        
        # Verificar si la ruta requiere autenticación
        if not any(request.path.startswith(path) for path in protected_paths):
            return None
        
        # Obtener token del header Authorization
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({
                'error': 'Token de autenticación requerido',
                'code': 'TOKEN_REQUIRED'
            }, status=401)
        
        token = auth_header.split(' ')[1]
        
        # Verificar token
        result = JWTAuthentication.verify_token(token)
        if not result:
            return JsonResponse({
                'error': 'Token inválido o expirado',
                'code': 'INVALID_TOKEN'
            }, status=401)
        
        user, payload = result
        
        # Verificar que sea administrador
        if not (user.is_staff or user.is_superuser):
            return JsonResponse({
                'error': 'Acceso denegado. Se requieren permisos de administrador',
                'code': 'ACCESS_DENIED'
            }, status=403)
        
        # Agregar usuario al request
        request.user = user
        request.jwt_payload = payload
        
        return None