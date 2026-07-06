from django.contrib.auth import get_user_model

from .emails import send_verification_email
from .tokens import build_verification_url

User = get_user_model()

def send_verification_email_task(user_id, domain, scheme):
    user = User.objects.get(pk=user_id)

    verification_url = build_verification_url(
        user,
        domain=domain,
        scheme=scheme,
    )
    send_verification_email(user, verification_url)