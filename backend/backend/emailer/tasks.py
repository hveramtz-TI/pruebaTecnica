from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import CustomUser, EmailVerification, Contest
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_verification_email(user_id, verification_token):
    """Envía email de verificación al usuario"""
    try:
        user = CustomUser.objects.get(id=user_id)
        verification_url = f"http://localhost:3000/verify-email/{verification_token}"
        
        subject = "Verifica tu email - Sorteo San Valentín 2025"
        
        # Template en texto plano (por ahora)
        message = f"""
        ¡Hola {user.first_name}!
        
        Gracias por registrarte en nuestro Sorteo de San Valentín 2025.
        
        Para completar tu registro y participar en el sorteo, necesitas verificar tu email haciendo clic en el siguiente enlace:
        
        {verification_url}
        
        Este enlace expirará en 24 horas.
        
        Si no te registraste en nuestro sorteo, puedes ignorar este email.
        
        ¡Buena suerte!
        Equipo del Sorteo San Valentín
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        logger.info(f"Email de verificación enviado a {user.email}")
        return f"Email enviado exitosamente a {user.email}"
        
    except CustomUser.DoesNotExist:
        logger.error(f"Usuario con ID {user_id} no encontrado")
        return "Error: Usuario no encontrado"
    except Exception as e:
        logger.error(f"Error enviando email: {str(e)}")
        return f"Error enviando email: {str(e)}"

@shared_task
def send_winner_notification(user_id, contest_id):
    """Envía notificación al ganador del sorteo"""
    try:
        user = CustomUser.objects.get(id=user_id)
        contest = Contest.objects.get(id=contest_id)
        
        subject = f"🎉 ¡FELICIDADES! Eres el ganador de {contest.name}"
        
        message = f"""
        ¡Felicidades {user.first_name}!
        
        ¡Tienes una excelente noticia! Has sido seleccionado como el GANADOR de nuestro {contest.name}.
        
        Tu participación ha sido premiada y te contactaremos pronto con más detalles sobre tu premio.
        
        Gracias por participar y ¡disfruta tu premio!
        
        Equipo del Sorteo San Valentín
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        logger.info(f"Email de ganador enviado a {user.email}")
        return f"Notificación de ganador enviada a {user.email}"
        
    except (CustomUser.DoesNotExist, Contest.DoesNotExist) as e:
        logger.error(f"Error: {str(e)}")
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Error enviando email de ganador: {str(e)}")
        return f"Error enviando email: {str(e)}"