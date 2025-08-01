from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import logging
from django.core.cache import cache

def send_reservation_email(user, subject, template_name, context):
    """
    Send an HTML email to the user's verified email address using a template.
    Only sends if user.profile.is_verified and email is present.
    """
    email = user.email
    profile = getattr(user, 'profile', None)
    if not (profile and profile.is_verified and email):
        return False
    try:
        html_content = render_to_string(template_name, context)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return True
    except Exception as e:
        error_message = str(e)
        if (
            'quota' in error_message.lower() or
            '454' in error_message or
            '421' in error_message or
            'exceeded' in error_message.lower()
        ):
            logging.error(f"Gmail SMTP daily limit reached. No more emails will be sent today. Error: {error_message}")
            cache.set('gmail_smtp_limit_reached', True, timeout=60*60*12)
        else:
            logging.error(f"Failed to send reservation email to {email}: {error_message}")
        return False
