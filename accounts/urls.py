from django.urls import path, reverse_lazy
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
    PasswordChangeView,
    PasswordChangeDoneView,
)
from .forms import BrandedPasswordResetForm, LoginForm
from .views import (
    EmailChangeConfirmView,
    EmailChangeView,
    SignupView,
    VerifyEmailView,
    SendVerificationEmailView,
    ReactivateAccountView,
    MeView,
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
    path(
        "reset-password/",
        PasswordResetView.as_view(
            form_class=BrandedPasswordResetForm,
            template_name="accounts/password_reset_form.html",
            email_template_name="emails/password_reset_email.txt",
            html_email_template_name="emails/password_reset_email.html",
            subject_template_name="emails/password_reset_subject.txt",
            success_url=reverse_lazy("accounts:password_reset_done"),
        ),
        name="reset-password",
    ),
    path(
        "password-reset-done/",
        PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html",
            success_url=reverse_lazy("accounts:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path("password-reset-complete/",
        PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
    path("password-change/",
        PasswordChangeView.as_view(
            template_name="accounts/password_change_form.html",
            success_url=reverse_lazy("accounts:password_change_done"),
        ),
        name="password_change",
    ),
    path("password-change-done/",
        PasswordChangeDoneView.as_view(
            template_name="accounts/password_change_done.html",
        ),
        name="password_change_done",
    ),
    path("email-change/", EmailChangeView.as_view(), name="email-change"),
    path(
        "email-change/confirm/<str:token>/",
        EmailChangeConfirmView.as_view(),
        name="email-change-confirm",
    ),
    path("me/", MeView.as_view(), name="me")

]
