from django.urls import path
from .views import (
    SignupView,
    VerifyEmailView,
)

app_name = "accounts"

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("verify-email/<uidb64>/<token>/", VerifyEmailView.as_view(), name="verify-email"),
]
