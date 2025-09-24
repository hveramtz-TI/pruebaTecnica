from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.decorators import authentication_classes, permission_classes
from django.views.decorators.http import require_http_methods
from .models import CustomUser, Contest, Participant, EmailVerification
from .serializers import ContestRegistrationSerializer, PasswordCreationSerializer, AdminCreateSerializer, AdminLoginSerializer
from .tasks import send_verification_email
from .jwt_utils import JWTService, TokenBlacklistService

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

# ========== VISTAS DE ADMINISTRADOR ==========

@api_view(['POST'])
@permission_classes([AllowAny])
def admin_create(request):
    """
    Endpoint para crear administradores del hotel.
    """
    serializer = AdminCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            admin_user = serializer.save()
            return Response({
                'success': True,
                'message': 'Administrador creado exitosamente.',
                'admin': {
                    'id': admin_user.id,
                    'email': admin_user.email,
                    'name': admin_user.get_full_name(),
                    'is_staff': admin_user.is_staff
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Error creando administrador'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    else:
        return Response({
            'success': False,
            'message': 'Error en los datos proporcionados',
            'field_errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def admin_login(request):
    """
    Endpoint para login de administradores.
    Devuelve token JWT con expiración de 20 minutos.
    """
    serializer = AdminLoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        try:
            # Generar token JWT con expiración de 20 minutos
            token = JWTService.generate_token(user, expires_in_minutes=20)
            
            return Response({
                'success': True,
                'message': 'Login exitoso',
                'token': token,
                'expires_in': 20 * 60,  # 20 minutos en segundos
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.get_full_name(),
                    'is_staff': user.is_staff
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Error generando token de acceso'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    else:
        return Response({
            'success': False,
            'message': 'Credenciales inválidas',
            'field_errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def admin_logout(request):
    """
    Endpoint para logout de administradores.
    Invalida el token JWT actual.
    """
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return Response({
            'success': False,
            'message': 'Token de autorización requerido'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    token = auth_header.split(' ')[1]
    
    try:
        # Agregar token a lista negra
        if TokenBlacklistService.blacklist_token(token):
            return Response({
                'success': True,
                'message': 'Logout exitoso'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Token inválido'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': 'Error cerrando sesión'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def admin_verify_token(request):
    """
    Endpoint para verificar validez del token actual.
    Requiere autenticación.
    """
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return Response({
            'valid': False,
            'message': 'Token de autorización requerido'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    token = auth_header.split(' ')[1]
    
    try:
        # Verificar si el token está en lista negra
        if TokenBlacklistService.is_token_blacklisted(token):
            return Response({
                'valid': False,
                'message': 'Token invalidado'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Verificar validez del token
        user, error = JWTService.get_user_from_token(token)
        
        if error:
            return Response({
                'valid': False,
                'message': error
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response({
            'valid': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.get_full_name(),
                'is_staff': user.is_staff
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'valid': False,
            'message': 'Error verificando token'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)# ========== ADMIN AUTHENTICATION VIEWS ==========

@api_view(['GET'])
def admin_participants_list(request):
    """
    Endpoint protegido para obtener la lista de participantes del concurso.
    Requiere token JWT de administrador válido.
    """
    from .decorators import jwt_required
    
    # Aplicar manualmente la validación JWT
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    
    print(f"DEBUG - Authorization header recibido: {auth_header}")
    print(f"DEBUG - Headers completos: {dict(request.META)}")
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return Response({
            'success': False,
            'message': 'Token de autorización requerido. Formato: Bearer <token>'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    token = auth_header.split(' ')[1]
    
    print(f"DEBUG - Token extraído: {token}")
    
    try:
        # Decodificar el token
        payload, error = JWTService.decode_token(token)
        
        print(f"DEBUG - Payload decodificado: {payload}")
        print(f"DEBUG - Error de decodificación: {error}")
        
        if error or not payload:
            return Response({
                'success': False,
                'message': f'Token inválido: {error or "Token no válido"}'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Verificar que el usuario existe y es staff
        try:
            user = CustomUser.objects.get(
                id=payload['user_id'], 
                is_staff=True,
                is_active=True
            )
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
    
    # Si llegamos aquí, el token es válido
    try:
        # Obtener todos los participantes con información completa
        participants = []
        
        for participant in Participant.objects.all().order_by('-registered_at'):
            # Obtener información del usuario relacionado
            user = participant.user
            
            # Verificar si el email está verificado
            is_email_verified = user.is_email_verified
            
            # Obtener información adicional
            participant_data = {
                'id': participant.id,
                'name': f"{user.first_name} {user.last_name}".strip() or 'Sin nombre',
                'email': user.email,
                'phone': user.phone or 'No especificado',
                'is_eligible': participant.is_eligible,
                'is_email_verified': is_email_verified,
                'has_password': bool(user.password),  # Indica si completó el registro
                'registration_date': participant.registered_at.isoformat(),
                'verification_status': _get_verification_status(user, participant)
            }
            
            participants.append(participant_data)
        
        return Response({
            'success': True,
            'participants': participants,
            'total_count': len(participants),
            'verified_count': len([p for p in participants if p['is_email_verified']]),
            'eligible_count': len([p for p in participants if p['is_eligible']])
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al obtener la lista de participantes: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def admin_select_winner(request):
    """
    Endpoint protegido para seleccionar un ganador aleatorio del concurso.
    Requiere token JWT de administrador válido.
    """
    import random
    
    # Validar token JWT
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return Response({
            'success': False,
            'message': 'Token de autorización requerido. Formato: Bearer <token>'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    token = auth_header.split(' ')[1]
    
    try:
        # Decodificar el token
        payload, error = JWTService.decode_token(token)
        
        if error or not payload:
            return Response({
                'success': False,
                'message': f'Token inválido: {error or "Token no válido"}'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Verificar que el usuario existe y es staff
        try:
            admin_user = CustomUser.objects.get(
                id=payload['user_id'], 
                is_staff=True,
                is_active=True
            )
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
    
    # Si llegamos aquí, el token es válido
    try:
        # Obtener el concurso activo
        contest = Contest.objects.filter(is_active=True).first()
        if not contest:
            return Response({
                'success': False,
                'message': 'No hay concursos activos disponibles'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar si ya hay un ganador
        if contest.winner:
            return Response({
                'success': False,
                'message': 'Ya se ha seleccionado un ganador para este concurso',
                'winner': {
                    'name': f"{contest.winner.first_name} {contest.winner.last_name}",
                    'email': contest.winner.email,
                    'selected_at': contest.winner.date_joined.isoformat()
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener participantes elegibles (email verificado y contraseña creada)
        eligible_participants = Participant.objects.filter(
            contest=contest,
            is_eligible=True,
            user__is_email_verified=True,
            user__password__isnull=False
        ).exclude(user__password='')
        
        if not eligible_participants.exists():
            return Response({
                'success': False,
                'message': 'No hay participantes elegibles para el sorteo'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Seleccionar ganador aleatorio
        winner_participant = random.choice(list(eligible_participants))
        winner_user = winner_participant.user
        
        # Actualizar el concurso con el ganador
        contest.winner = winner_user
        contest.save()
        
        # Enviar email de notificación al ganador
        try:
            from .tasks import send_winner_notification_email
            send_winner_notification_email.delay(winner_user.id, contest.id)
        except Exception as email_error:
            # Si falla el envío asíncrono, intentar síncrono
            try:
                send_winner_notification_email(winner_user.id, contest.id)
            except Exception as sync_error:
                # Log error but don't fail the winner selection
                print(f"Error enviando email de ganador: {sync_error}")
        
        # Preparar respuesta con información del ganador
        winner_data = {
            'id': winner_user.id,
            'name': f"{winner_user.first_name} {winner_user.last_name}",
            'email': winner_user.email,
            'phone': winner_user.phone or 'No especificado',
            'registration_date': winner_participant.registered_at.isoformat(),
            'selected_at': timezone.now().isoformat(),
            'contest_name': contest.name
        }
        
        # Estadísticas del sorteo
        total_participants = eligible_participants.count()
        
        return Response({
            'success': True,
            'message': '¡Ganador seleccionado exitosamente!',
            'winner': winner_data,
            'contest': {
                'id': contest.id,
                'name': contest.name,
                'total_eligible': total_participants
            },
            'selected_by': {
                'admin_email': admin_user.email,
                'admin_name': f"{admin_user.first_name} {admin_user.last_name}"
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al seleccionar ganador: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def _get_verification_status(user, participant):
    """
    Función auxiliar para determinar el estado de verificación del participante
    """
    if not user.is_email_verified:
        return 'Email pendiente'
    elif not user.password:
        return 'Contraseña pendiente'
    elif not participant.is_eligible:
        return 'No elegible'
    else:
        return 'Completamente verificado'