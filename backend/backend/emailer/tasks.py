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
def send_winner_notification_email(user_id, contest_id):
    """Envía email de notificación HTML al ganador del sorteo"""
    try:
        user = CustomUser.objects.get(id=user_id)
        contest = Contest.objects.get(id=contest_id)
        
        subject = f"🎉 ¡FELICIDADES! Eres el GANADOR de {contest.name} 🏆"
        
        # Template HTML celebratorio para el ganador
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #FFD700, #FFA500, #FF6347);
                    padding: 20px;
                    margin: 0;
                }}
                .email-container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 25px;
                    box-shadow: 0 15px 50px rgba(0, 0, 0, 0.3);
                    overflow: hidden;
                    border: 5px solid #FFD700;
                }}
                .header {{
                    background: linear-gradient(135deg, #FF6B35, #F7931E);
                    color: white;
                    padding: 40px 30px;
                    text-align: center;
                    position: relative;
                }}
                .confetti {{
                    font-size: 30px;
                    position: absolute;
                    animation: bounce 2s infinite;
                }}
                @keyframes bounce {{
                    0%, 20%, 50%, 80%, 100% {{ transform: translateY(0); }}
                    40% {{ transform: translateY(-10px); }}
                    60% {{ transform: translateY(-5px); }}
                }}
                .content {{
                    padding: 40px 30px;
                    background: linear-gradient(135deg, #fff, #fff9e6);
                }}
                .winner-badge {{
                    background: linear-gradient(135deg, #FFD700, #FFA500);
                    color: #8B4513;
                    padding: 15px 30px;
                    border-radius: 50px;
                    font-size: 24px;
                    font-weight: bold;
                    text-align: center;
                    margin: 20px 0;
                    box-shadow: 0 5px 15px rgba(255, 215, 0, 0.4);
                }}
                .prize-info {{
                    background: #f8f9fa;
                    padding: 25px;
                    border-radius: 15px;
                    border-left: 5px solid #28a745;
                    margin: 25px 0;
                }}
                .footer {{
                    background: linear-gradient(135deg, #333, #555);
                    color: white;
                    padding: 25px;
                    text-align: center;
                    font-size: 14px;
                }}
                .celebration {{
                    text-align: center;
                    font-size: 50px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <div class="confetti" style="top: 10px; left: 10%;">🎊</div>
                    <div class="confetti" style="top: 20px; right: 10%; animation-delay: 0.5s;">🎉</div>
                    <div class="confetti" style="top: 30px; left: 80%; animation-delay: 1s;">✨</div>
                    
                    <h1 style="margin: 0; font-size: 28px;">🏆 ¡FELICIDADES! 🏆</h1>
                    <h2 style="margin: 10px 0 0 0; font-size: 20px;">{contest.name}</h2>
                </div>
                
                <div class="content">
                    <div class="celebration">🎊 🎉 🏆 🎊 🎉</div>
                    
                    <h2 style="color: #FF6B35; text-align: center;">¡Hola {user.first_name}!</h2>
                    
                    <div class="winner-badge">
                        🌟 ¡ERES EL GANADOR! 🌟
                    </div>
                    
                    <p style="font-size: 18px; text-align: center; color: #333;">
                        <strong>¡Tienes una noticia INCREÍBLE!</strong>
                    </p>
                    
                    <p style="font-size: 16px; color: #555; line-height: 1.6;">
                        Has sido <strong style="color: #FF6B35;">seleccionado como el GANADOR</strong> de nuestro 
                        <strong>{contest.name}</strong>. Entre todos los participantes elegibles, 
                        ¡el destino te ha sonreído! 🍀
                    </p>
                    
                    <div class="prize-info">
                        <h3 style="color: #28a745; margin-top: 0;">🎁 Tu Premio:</h3>
                        <p style="font-size: 16px; margin: 10px 0;">
                            <strong>🏨 Estadía romántica de 2 noches</strong><br>
                            🌹 Desayuno incluido<br>
                            💕 Experiencia perfecta para San Valentín<br>
                            ✨ Una experiencia inolvidable te espera
                        </p>
                    </div>
                    
                    <p style="color: #666; font-size: 14px;">
                        <strong>📞 Próximos pasos:</strong><br>
                        Nuestro equipo se contactará contigo en las próximas 48 horas para coordinar 
                        los detalles de tu premio. Mantente atento a tu email y teléfono.
                    </p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <p style="font-size: 18px; color: #FF6B35; font-weight: bold;">
                            ¡Disfruta tu premio y feliz San Valentín! 💕
                        </p>
                    </div>
                    
                    <div class="celebration">🌹 💕 🥂 💕 🌹</div>
                </div>
                
                <div class="footer">
                    <p><strong>🎉 Equipo del Sorteo San Valentín 💌</strong></p>
                    <p>Gracias por participar en nuestro sorteo</p>
                    <p style="font-size: 12px; margin-top: 15px;">
                        Este es un email automático, por favor no respondas a este mensaje.<br>
                        Para consultas, contacta a nuestro equipo de soporte.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Versión texto plano como fallback
        plain_message = f"""
        🎉 ¡FELICIDADES {user.first_name}! 🎉
        
        ¡ERES EL GANADOR DE {contest.name}!
        
        Has sido seleccionado entre todos los participantes elegibles.
        
        🎁 TU PREMIO:
        - Estadía romántica de 2 noches
        - Desayuno incluido
        - Experiencia perfecta para San Valentín
        
        📞 PRÓXIMOS PASOS:
        Nuestro equipo se contactará contigo en las próximas 48 horas 
        para coordinar los detalles de tu premio.
        
        ¡Disfruta tu premio y feliz San Valentín! 💕
        
        Equipo del Sorteo San Valentín
        """
        
        from django.core.mail import EmailMultiAlternatives
        
        # Crear el email con versión HTML
        email = EmailMultiAlternatives(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        )
        email.attach_alternative(html_message, "text/html")
        email.send()
        
        logger.info(f"Email de ganador enviado exitosamente a {user.email}")
        return f"Notificación de ganador enviada a {user.email}"
        
    except CustomUser.DoesNotExist:
        logger.error(f"Usuario con ID {user_id} no encontrado")
        return "Error: Usuario no encontrado"
    except Contest.DoesNotExist:
        logger.error(f"Concurso con ID {contest_id} no encontrado")
        return "Error: Concurso no encontrado"
    except Exception as e:
        logger.error(f"Error enviando email de ganador: {str(e)}")
        return f"Error enviando email: {str(e)}"

# Mantener la función anterior por compatibilidad
@shared_task
def send_winner_notification(user_id, contest_id):
    """Función de compatibilidad - redirige a la nueva función"""
    return send_winner_notification_email(user_id, contest_id)