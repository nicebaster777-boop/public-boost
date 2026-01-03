"""Email sending utilities."""

import logging
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_email(
    to_email: str,
    subject: str,
    html_body: str,
    text_body: str | None = None,
) -> bool:
    """
    Send email via SMTP.

    Args:
        to_email: Recipient email address
        subject: Email subject
        html_body: HTML email body
        text_body: Plain text email body (optional)

    Returns:
        True if email was sent successfully, False otherwise
    """
    if not settings.smtp_enabled:
        # In development, just log instead of sending
        logger.info(f"[EMAIL] Would send to {to_email}: {subject}")
        logger.info(f"[EMAIL] Body: {html_body}")
        return True

    if not settings.smtp_user or not settings.smtp_password:
        logger.warning("[EMAIL] SMTP credentials not configured")
        return False

    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
        message["To"] = to_email

        # Add text and HTML parts
        if text_body:
            text_part = MIMEText(text_body, "plain", "utf-8")
            message.attach(text_part)

        html_part = MIMEText(html_body, "html", "utf-8")
        message.attach(html_part)

        # Send email
        await aiosmtplib.send(
            message,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            use_tls=settings.smtp_use_tls,
            username=settings.smtp_user,
            password=settings.smtp_password,
        )

        logger.info(f"[EMAIL] Successfully sent email to {to_email}")
        return True
    except Exception as e:
        logger.error(f"[EMAIL] Error sending email: {e}")
        return False


async def send_password_reset_email(email: str, reset_token: str, reset_url: str) -> bool:
    """
    Send password reset email.

    Args:
        email: User email address
        reset_token: Password reset token
        reset_url: Full URL for password reset page

    Returns:
        True if email was sent successfully
    """
    subject = "Восстановление пароля - Public Boost"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .button {{ display: inline-block; padding: 12px 24px; background-color: #2563eb; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .button:hover {{ background-color: #1d4ed8; }}
            .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Восстановление пароля</h1>
            <p>Вы запросили восстановление пароля для вашего аккаунта в Public Boost.</p>
            <p>Для сброса пароля нажмите на кнопку ниже:</p>
            <a href="{reset_url}" class="button">Восстановить пароль</a>
            <p>Или скопируйте и вставьте эту ссылку в браузер:</p>
            <p style="word-break: break-all; color: #2563eb;">{reset_url}</p>
            <p><strong>Ссылка действительна в течение 1 часа.</strong></p>
            <p>Если вы не запрашивали восстановление пароля, просто проигнорируйте это письмо.</p>
            <div class="footer">
                <p>С уважением,<br>Команда Public Boost</p>
            </div>
        </div>
    </body>
    </html>
    """

    text_body = f"""
Восстановление пароля - Public Boost

Вы запросили восстановление пароля для вашего аккаунта.

Для сброса пароля перейдите по ссылке:
{reset_url}

Ссылка действительна в течение 1 часа.

Если вы не запрашивали восстановление пароля, просто проигнорируйте это письмо.

С уважением,
Команда Public Boost
    """

    return await send_email(email, subject, html_body, text_body)
