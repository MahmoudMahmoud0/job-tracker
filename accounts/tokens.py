from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def build_verification_url(user, request):
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    token = default_token_generator.make_token(user)

    return request.build_absolute_uri(
        reverse(
            "accounts:verify-email",
            kwargs={
                "uidb64": uid,
                "token": token,
            },
        )
    )