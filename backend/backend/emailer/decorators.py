from functools import wraps
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from .models import CustomUser
from .jwt_utils import JWTService

def jwt_required(view_func):
    """
    Decorador para proteger vistas que requieren autenticación JWT.
    Valida el token JWT en el header Authorization y agrega el usuario a request.user
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Obtener el header de autorización
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({
                'success': False,
                'message': 'Token de autorización requerido. Formato: Bearer <token>'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Extraer el token
        token = auth_header.split(' ')[1]
        
        try:
            # Decodificar el token
            payload = JWTService.decode_token(token)
            
            # Verificar que el usuario existe y es staff
            try:
                user = CustomUser.objects.get(
                    id=payload['user_id'], 
                    is_staff=True,
                    is_active=True
                )
                
                # Agregar el usuario al request
                request.user = user
                
                # Llamar a la vista original
                return view_func(request, *args, **kwargs)
                
            except CustomUser.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Usuario no encontrado o sin permisos de administrador'
                }, status=status.HTTP_401_UNAUTHORIZED)
                
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Token inválido o expirado: {str(e)}'
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    return wrapper

def admin_required(view_func):
    """
    Decorador adicional para vistas que requieren permisos de superusuario.
    Debe usarse junto con @jwt_required
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Verificar que el usuario tenga permisos de superusuario
        if not hasattr(request, 'user') or not request.user.is_superuser:
            return Response({
                'success': False,
                'message': 'Se requieren permisos de superusuario'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return view_func(request, *args, **kwargs)
    
    return wrapper