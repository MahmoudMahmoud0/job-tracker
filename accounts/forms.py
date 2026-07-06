from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm
)
from django.contrib.auth import authenticate
from .models import User
from django import forms
from django.core.exceptions import ValidationError
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
