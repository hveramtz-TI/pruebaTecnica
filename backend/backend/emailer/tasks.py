from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import CustomUser, EmailVerification, Contest
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_verification_email(user_email, verification_token):
    """Envía email de verificación al usuario"""
    try:
        user = CustomUser.objects.get(email=user_email)
        verification_url = f"http://localhost:5173/verify-email/{verification_token}"
        
        subject = "🌹 Verifica tu email - Sorteo San Valentín 2025 💕"
        
        # Template HTML más atractivo
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #ff6b6b, #ff8e9b, #ffd93d);
                    padding: 20px;
                    margin: 0;
                }}
                .email-container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 20px;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #e91e63, #ad1457);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .content {{
                    padding: 30px;
                }}
                .button {{
                    display: inline-block;
                    background: linear-gradient(135deg, #4CAF50, #45a049);
                    color: white !important;
                    padding: 15px 30px;
                    text-decoration: none;
                    border-radius: 10px;
                    font-weight: bold;
                    font-size: 16px;
                    margin: 20px 0;
                }}
                .footer {{
                    background: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>🌹 Sorteo San Valentín 2025 💕</h1>
                    <p>¡Gana una estadía romántica de 2 noches!</p>
                </div>
                <div class="content">
                    <h2>¡Hola {user.first_name}!</h2>
                    
                    <p>Gracias por registrarte en nuestro <strong>Sorteo de San Valentín 2025</strong>.</p>
                    
                    <p>Para completar tu registro y participar en el sorteo, necesitas verificar tu email y crear tu contraseña.</p>
                    
                    <div style="text-align: center;">
                        <a href="{verification_url}" class="button">
                            ✅ Terminar Registro
                        </a>
                    </div>
                    
                    <p><small>Este enlace expirará en 24 horas.</small></p>
                    
                    <p>Si no te registraste en nuestro sorteo, puedes ignorar este email.</p>
                    
                    <p>¡Buena suerte! 🍀</p>
                </div>
                <div class="footer">
                    <p>Equipo del Sorteo San Valentín 💌</p>
                    <p>Este es un email automático, por favor no respondas a este mensaje.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # También crear versión texto plano como fallback
        plain_message = f"""
        ¡Hola {user.first_name}!
        
        Gracias por registrarte en nuestro Sorteo de San Valentín 2025.
        
        Para completar tu registro y participar en el sorteo, visita este enlace:
        {verification_url}
        
        Este enlace expirará en 24 horas.
        
        Si no te registraste en nuestro sorteo, puedes ignorar este email.
        
        ¡Buena suerte!
        Equipo del Sorteo San Valentín
        """
        
        from django.core.mail import EmailMultiAlternatives
        
        # Crear el email con versión HTML
        email = EmailMultiAlternatives(
            subject,
            plain_message,  # Versión texto
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        )
        email.attach_alternative(html_message, "text/html")  # Versión HTML
        email.send()
        
        logger.info(f"Email de verificación enviado a {user.email}")
        return f"Email enviado exitosamente a {user.email}"
        
    except CustomUser.DoesNotExist:
        logger.error(f"Usuario con email {user_email} no encontrado")
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