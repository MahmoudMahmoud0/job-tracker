from django.shortcuts import render, redirect
from django.views import generic

from .forms import SignupForm
from .models import User
from .services import verify_email
from django.urls import reverse_lazy
from django_q.tasks import async_task
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin


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
                "eyebrow": "Verification Email Sent",
                "headline": "Check your inbox to activate your account.",
                "description": "We sent a verification email to your address. Open the link in that message to activate your Job Tracker account and sign in.",
                "primary_label": "Back to login",
                "primary_url": reverse_lazy("accounts:login"),
                "secondary_label": "Go to homepage",
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
                "eyebrow": "Verification Email Sent",
                "headline": "A fresh verification link is on its way.",
                "description": "If that email address matches an unverified account, we have sent a new verification email. Open it to finish confirming your account.",
                "primary_label": "Back to login",
                "primary_url": reverse_lazy("accounts:login"),
                "secondary_label": "Create a new account",
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
                "eyebrow": "Reactivation Email Sent",
                "headline": "Check your inbox to reactivate your account.",
                "description": "If that email address matches an inactive account, we have sent a reactivation email. Open the link in that message to reactivate your access.",
                "primary_label": "Back to login",
                "primary_url": reverse_lazy("accounts:login"),
                "secondary_label": "Go to homepage",
                "secondary_url": reverse_lazy("landing"),
            },
        )
    
class MeView(LoginRequiredMixin, generic.UpdateView):
    model = User
    template_name = "accounts/me.html"
    fields = [
        "first_name",
        "last_name",
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