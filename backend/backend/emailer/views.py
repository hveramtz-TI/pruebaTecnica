from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import transaction
from .models import CustomUser, Contest, Participant, EmailVerification
from .serializers import ContestRegistrationSerializer, PasswordCreationSerializer
from .tasks import send_verification_email

@api_view(['POST'])
@permission_classes([AllowAny])
def contest_register(request):
    """
    Endpoint público para registrarse en el concurso.
    Valida que el email no esté duplicado y crea el usuario + participante.
    """
    serializer = ContestRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            with transaction.atomic():
                # Crear el usuario
                user = serializer.save()
                
                # Obtener o crear el concurso activo
                contest, created = Contest.objects.get_or_create(
                    is_active=True,
                    defaults={
                        'name': 'Sorteo San Valentín 2025',
                        'description': 'Gana una estadía romántica de 2 noches para una pareja',
                        'start_date': '2025-01-01T00:00:00Z',
                        'end_date': '2025-02-14T23:59:59Z'
                    }
                )
                
                # Crear participante
                participant = Participant.objects.create(
                    user=user,
                    contest=contest,
                    is_eligible=False  # Solo elegible después de verificar email
                )
                
                # Crear token de verificación de email
                verification = EmailVerification.objects.create(user=user)
                
                # Enviar email de verificación (tarea asíncrona)
                try:
                    send_verification_email.delay(user.email, str(verification.token))
                except Exception as e:
                    # Si Celery no está disponible, enviar de forma síncrona
                    print(f"Celery no disponible, enviando email síncronamente: {e}")
                    send_verification_email(user.email, str(verification.token))
                
                return Response({
                    'success': True,
                    'message': '¡Gracias por registrarte! Revisa tu correo para verificar tu cuenta.',
                    'user_id': user.id
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Error interno del servidor'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    else:
        # Extraer el mensaje de error específico para email duplicado
        if 'email' in serializer.errors:
            error_message = serializer.errors['email'][0]
            if 'ya está registrado' in str(error_message):
                return Response({
                    'success': False,
                    'message': 'El correo electrónico ya está registrado.',
                    'field_errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': False,
            'message': 'Error en los datos proporcionados',
            'field_errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email_and_create_password(request):
    """
    Endpoint para verificar el email y crear contraseña.
    Recibe token de verificación y nueva contraseña.
    """
    serializer = PasswordCreationSerializer(data=request.data)
    
    if serializer.is_valid():
        token = serializer.validated_data['token']
        password = serializer.validated_data['password']
        
        try:
            with transaction.atomic():
                # Buscar el token de verificación
                verification = EmailVerification.objects.get(
                    token=token,
                    is_used=False
                )
                
                # Verificar que no haya expirado
                if verification.is_expired():
                    return Response({
                        'success': False,
                        'message': 'El enlace de verificación ha expirado.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Obtener el usuario
                user = verification.user
                
                # Establecer la contraseña y marcar como verificado
                user.set_password(password)
                user.is_email_verified = True
                user.save()
                
                # Marcar el token como usado
                verification.is_used = True
                verification.save()
                
                # Marcar al participante como elegible
                try:
                    participant = Participant.objects.get(user=user)
                    participant.is_eligible = True
                    participant.save()
                except Participant.DoesNotExist:
                    pass  # No debería pasar, pero por si acaso
                
                return Response({
                    'success': True,
                    'message': 'Tu cuenta ha sido activada. Ya estás participando en el sorteo.'
                }, status=status.HTTP_200_OK)
                
        except EmailVerification.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Token de verificación inválido o ya utilizado.'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Error interno del servidor'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    else:
        return Response({
            'success': False,
            'message': 'Error en los datos proporcionados',
            'field_errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def verify_token_validity(request, token):
    """
    Endpoint para verificar si un token es válido antes de mostrar el formulario.
    """
    try:
        verification = EmailVerification.objects.get(
            token=token,
            is_used=False
        )
        
        if verification.is_expired():
            return Response({
                'valid': False,
                'message': 'El enlace de verificación ha expirado.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'valid': True,
            'user_email': verification.user.email,
            'user_name': verification.user.get_full_name()
        }, status=status.HTTP_200_OK)
        
    except EmailVerification.DoesNotExist:
        return Response({
            'valid': False,
            'message': 'Token de verificación inválido.'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_database_for_testing(request):
    """
    Endpoint temporal para limpiar datos de prueba.
    ⚠️ SOLO PARA DESARROLLO - ELIMINAR EN PRODUCCIÓN
    """
    try:
        with transaction.atomic():
            # Eliminar todos los tokens de verificación
            EmailVerification.objects.all().delete()
            
            # Eliminar todos los participantes
            Participant.objects.all().delete()
            
            # Eliminar todos los usuarios (excepto superusers)
            CustomUser.objects.filter(is_superuser=False).delete()
            
            # Reiniciar los concursos
            Contest.objects.all().delete()
            
            return Response({
                'success': True,
                'message': 'Base de datos limpiada exitosamente para pruebas.'
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
            return Response({
                'success': False,
                'message': f'Error limpiando base de datos: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ============ ADMIN AUTHENTICATION VIEWS ============

@api_view(['POST'])
@permission_classes([AllowAny])
def admin_login(request):
    """
    Endpoint para login de administrador.
    Devuelve token JWT con expiración de 20 minutos.
    """
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({
            'success': False,
            'message': 'Email y contraseña son requeridos'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    from .jwt_auth import authenticate_admin_user, JWTAuthentication
    
    # Autenticar usuario administrador
    user = authenticate_admin_user(email, password)
    
    if not user:
        return Response({
            'success': False,
            'message': 'Credenciales inválidas o usuario sin permisos de administrador'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Generar tokens JWT
    tokens = JWTAuthentication.generate_tokens(user)
    
    return Response({
        'success': True,
        'message': 'Login exitoso',
        'user': {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser
        },
        'tokens': tokens
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def admin_refresh_token(request):
    """
    Endpoint para renovar access token usando refresh token.
    """
    refresh_token = request.data.get('refresh_token')
    
    if not refresh_token:
        return Response({
            'success': False,
            'message': 'Refresh token requerido'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    from .jwt_auth import JWTAuthentication
    
    # Renovar access token
    new_tokens = JWTAuthentication.refresh_access_token(refresh_token)
    
    if not new_tokens:
        return Response({
            'success': False,
            'message': 'Refresh token inválido o expirado'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    return Response({
        'success': True,
        'message': 'Token renovado exitosamente',
        'tokens': new_tokens
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
def admin_logout(request):
    """
    Endpoint para logout de administrador.
    En una implementación más robusta, se mantendría una blacklist de tokens.
    """
    return Response({
        'success': True,
        'message': 'Logout exitoso'
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def admin_profile(request):
    """
    Endpoint protegido para obtener perfil del administrador.
    Requiere token JWT válido.
    """
    user = request.user
    
    return Response({
        'success': True,
        'user': {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'date_joined': user.date_joined
        }
    }, status=status.HTTP_200_OK)