from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .emails import send_verification_email
from .tokens import build_verification_url
from core.email import attach_default_inline_images

User = get_user_model()

def send_verification_email_task(user_id, domain, scheme):
    user = User.objects.get(pk=user_id)

    verification_url = build_verification_url(
        user,
        domain=domain,
        scheme=scheme,
    )
    send_verification_email(user, verification_url)


def send_password_reset_email_task(
    user_id,
    *,
    domain,
    site_name,
    protocol,
    from_email,
    subject_template_name,
    email_template_name,
    html_email_template_name=None,
    extra_email_context=None,
):
    user = User.objects.get(pk=user_id)
    user_email = getattr(user, User.get_email_field_name())
    user_pk_bytes = force_bytes(User._meta.pk.value_to_string(user))

    context = {
        "email": user_email,
        "domain": domain,
        "site_name": site_name,
        "uid": urlsafe_base64_encode(user_pk_bytes),
        "user": user,
        "token": default_token_generator.make_token(user),
        "protocol": protocol,
        **(extra_email_context or {}),
    }

    subject = render_to_string(subject_template_name, context)
    subject = "".join(subject.splitlines())
    body = render_to_string(email_template_name, context)

    email_message = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=from_email or settings.DEFAULT_FROM_EMAIL,
        to=[user_email],
    )

    if html_email_template_name:
        html_email = render_to_string(html_email_template_name, context)
        email_message.attach_alternative(html_email, "text/html")
        attach_default_inline_images(email_message)

    email_message.send()
