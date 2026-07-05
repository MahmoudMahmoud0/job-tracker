# accounts/services.py

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode


User = get_user_model()


def verify_email(uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return False, None

    if not default_token_generator.check_token(user, token):
        return False, user

    user.is_active = True
    user.is_email_verified = True
    user.save(update_fields=["is_active", "is_email_verified"])

    return True, user