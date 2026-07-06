from django.urls import path
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
)
from .forms import LoginForm
from .views import (
    SignupView,
    VerifyEmailView,
    SendVerificationEmailView,
    ReactivateAccountView,
)

app_name = "accounts"

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path(
        "login/",
        LoginView.as_view(authentication_form=LoginForm),
        name="login",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("login/send-verification-email/", SendVerificationEmailView.as_view(), name="send-verification-email"),
    path("login/reactivate-account/", ReactivateAccountView.as_view(), name="reactivate-account"),
    path("verify-email/<uidb64>/<token>/", VerifyEmailView.as_view(), name="verify-email"),
]
