from django.shortcuts import render, redirect
from django.views import generic
from datetime import timedelta
import secrets

from .forms import EmailChangeRequestForm, SignupForm
from .models import EmailChangeRequest, User
from .services import verify_email
from django.urls import reverse_lazy
from django_q.tasks import async_task
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.utils.translation import gettext as _


class SignupView(generic.CreateView):
    template_name = "registration/signup.html"
    form_class = SignupForm
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        domain = self.request.get_host()
        scheme = "https" if self.request.is_secure() else "http"
        transaction.on_commit(lambda: async_task(
            "accounts.tasks.send_verification_email_task",
            user.pk,
            domain,
            scheme,
        ))

        return render(
            self.request,
            "accounts/email_verification_sent.html",
            {
                "eyebrow": _("Verification Email Sent"),
                "headline": _("Check your inbox to activate your account."),
                "description": _("We sent a verification email to your address. Open the link in that message to activate your Job Tracker account and sign in."),
                "primary_label": _("Back to login"),
                "primary_url": reverse_lazy("accounts:login"),
                "secondary_label": _("Go to homepage"),
                "secondary_url": reverse_lazy("landing"),
            },
        )


class VerifyEmailView(generic.View):
    def get(self, request, uidb64, token):
        success, _ = verify_email(uidb64, token)

        template = (
            "accounts/email_verified.html"
            if success
            else "accounts/email_verification_failed.html"
        )

        return render(request, template)


class SendVerificationEmailView(generic.View):
    def post(self, request):
        email = request.POST.get("email", "").strip()
        user = User._default_manager.filter(email__iexact=email).first()

        if user and not user.is_email_verified:
            domain = request.get_host()
            scheme = "https" if request.is_secure() else "http"
            transaction.on_commit(lambda: async_task(
                "accounts.tasks.send_verification_email_task",
                user.pk,
                domain,
                scheme,
            ))

        return render(
            request,
            "accounts/email_verification_sent.html",
            {
                "eyebrow": _("Verification Email Sent"),
                "headline": _("A fresh verification link is on its way."),
                "description": _("If that email address matches an unverified account, we have sent a new verification email. Open it to finish confirming your account."),
                "primary_label": _("Back to login"),
                "primary_url": reverse_lazy("accounts:login"),
                "secondary_label": _("Create a new account"),
                "secondary_url": reverse_lazy("accounts:signup"),
            },
        )


class ReactivateAccountView(generic.View):
    def post(self, request):
        email = request.POST.get("email", "").strip()
        user = User._default_manager.filter(email__iexact=email).first()

        if user and not user.is_active:
            domain = request.get_host()
            scheme = "https" if request.is_secure() else "http"
            transaction.on_commit(lambda: async_task(
                "accounts.tasks.send_verification_email_task",
                user.pk,
                domain,
                scheme,
            ))

        return render(
            request,
            "accounts/email_verification_sent.html",
            {
                "eyebrow": _("Reactivation Email Sent"),
                "headline": _("Check your inbox to reactivate your account."),
                "description": _("If that email address matches an inactive account, we have sent a reactivation email. Open the link in that message to reactivate your access."),
                "primary_label": _("Back to login"),
                "primary_url": reverse_lazy("accounts:login"),
                "secondary_label": _("Go to homepage"),
                "secondary_url": reverse_lazy("landing"),
            },
        )
    
class MeView(LoginRequiredMixin, generic.UpdateView):
    model = User
    template_name = "accounts/me.html"
    fields = [
        "first_name",
        "last_name",
        "locale",
        "reminder_email_notifier",
        "reminder_lead_time",
        "timezone",
        "export_format",
        "auto_delete_exports",
        "retain_export_days",
    ]

    success_url = reverse_lazy("accounts:me")

    def get_object(self):
        return self.request.user
    
class EmailChangeView(LoginRequiredMixin, generic.CreateView):
    model = EmailChangeRequest
    form_class = EmailChangeRequestForm
    template_name = "accounts/email_change.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        EmailChangeRequest.objects.filter(
            user=self.request.user,
            used_at__isnull=True,
        ).delete()

        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.token = secrets.token_urlsafe(32)
        self.object.expires_at = timezone.localtime(timezone.now()) + timedelta(hours=24)
        self.object.save()

        domain = self.request.get_host()
        scheme = "https" if self.request.is_secure() else "http"
        transaction.on_commit(lambda: async_task(
            "accounts.tasks.send_email_change_request_email_task",
            self.object.pk,
            domain,
            scheme,
        ))

        return render(
            self.request,
            "accounts/email_verification_sent.html",
            {
                "eyebrow": _("Email Change Requested"),
                "headline": _("Check your new inbox to confirm the change."),
                "description": _("We sent a confirmation message to %(email)s. Open the link in that email to continue updating your account email.") % {"email": self.object.new_email},
                "primary_label": _("Back to account"),
                "primary_url": reverse_lazy("accounts:me"),
                "secondary_label": _("Request another email change"),
                "secondary_url": reverse_lazy("accounts:email-change"),
            },
        )


class EmailChangeConfirmView(generic.View):
    def get(self, request, token):
        email_change_request = (
            EmailChangeRequest.objects
            .select_related("user")
            .filter(token=token)
            .first()
        )

        if email_change_request is None:
            return render(
                request,
                "accounts/email_change_failed.html",
                {"reason": "missing"},
            )

        if email_change_request.used_at is not None:
            return render(
                request,
                "accounts/email_change_failed.html",
                {"reason": "used"},
            )

        if email_change_request.expires_at <= timezone.localtime(timezone.now()):
            return render(
                request,
                "accounts/email_change_failed.html",
                {"reason": "expired"},
            )

        email_in_use = User._default_manager.filter(
            email__iexact=email_change_request.new_email
        ).exclude(pk=email_change_request.user_id).exists()
        if email_in_use:
            return render(
                request,
                "accounts/email_change_failed.html",
                {"reason": "taken"},
            )

        with transaction.atomic():
            user = email_change_request.user
            user.email = email_change_request.new_email
            user.is_email_verified = True
            user.save(update_fields=["email", "is_email_verified"])

            email_change_request.used_at = timezone.localtime(timezone.now())
            email_change_request.save(update_fields=["used_at"])

        return render(
            request,
            "accounts/email_change_confirmed.html",
            {"new_email": user.email},
        )
