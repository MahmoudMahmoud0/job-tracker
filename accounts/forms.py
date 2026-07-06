from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordResetForm,
)
from django.contrib.auth import authenticate
from django.contrib.sites.shortcuts import get_current_site
from .models import User
from django import forms
from django.core.exceptions import ValidationError
from django_q.tasks import async_task
from django.utils.translation import gettext_lazy as _

class SignupForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.existing_account_email = None

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]

    def clean_email(self):
        email = self.cleaned_data["email"]

        if User._default_manager.filter(email__iexact=email).exists():
            self.existing_account_email = email
            raise ValidationError(
                _("An account with this email already exists. Try logging in instead."),
                code="duplicate_email",
            )

        return email

class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "autofocus": True,
                "autocomplete": "email"
            }
        )
    )

    error_messages = {
        "invalid_login": _(
            "Please enter a correct email and password. Note that both "
            "fields may be case-sensitive."
        ),
        "unverified_email": _("This email has not been verified yet."),
        "inactive": _("This account is inactive right now."),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recovery_action = None
        self.recovery_email = None
        if self.request and self.request.method == "GET":
            initial_email = self.request.GET.get("username")
            if initial_email:
                self.fields["username"].initial = initial_email

    def clean(self):
        email = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if email is not None and password:
            self.user_cache = authenticate(
                self.request,
                username=email,
                password=password,
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        if not user.is_email_verified:
            self.recovery_action = "verify"
            self.recovery_email = user.email
            raise ValidationError(
                self.error_messages["unverified_email"],
                code="unverified_email",
            )
        if not user.is_active:
            self.recovery_action = "reactivate"
            self.recovery_email = user.email
            raise ValidationError(
                self.error_messages["inactive"],
                code="inactive",
            )


class BrandedPasswordResetForm(PasswordResetForm):
    def save(
        self,
        subject_template_name,
        email_template_name,
        from_email,
        domain_override=None,
        use_https=False,
        token_generator=None,
        request=None,
        html_email_template_name=None,
        extra_email_context=None,
    ):
        email = self.cleaned_data["email"]
        if not domain_override:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = domain_override

        protocol = "https" if use_https else "http"

        for user in self.get_users(email):
            async_task(
                "accounts.tasks.send_password_reset_email_task",
                user.pk,
                domain=domain,
                site_name=site_name,
                protocol=protocol,
                from_email=from_email,
                subject_template_name=subject_template_name,
                email_template_name=email_template_name,
                html_email_template_name=html_email_template_name,
                extra_email_context=extra_email_context,
            )
