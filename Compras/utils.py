
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


def send_email(to, subject, body, html_template=None, context=None):
    """
    Sends an email to the specified recipient.

    Args:
        to (str): Recipient's email address
        subject (str): Email subject
        body (str): Plain text email body
        html_template (str, optional): Path to HTML template for formatted emails
        context (dict, optional): Context data for HTML template rendering

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        from_email = settings.DEFAULT_FROM_EMAIL

        if html_template and context:
            html_message = render_to_string(html_template, context)
            plain_message = strip_tags(html_message)
        else:
            html_message = None
            plain_message = body

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[to],
            html_message=html_message,
            fail_silently=True,
        )
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to}: {str(e)}")
        return False
