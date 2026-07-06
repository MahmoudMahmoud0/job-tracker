from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views import generic

from .tokens import build_verification_url
from .forms import SignupForm
from .services import verify_email
from django.urls import reverse_lazy
from .emails import send_verification_email
from django_q.tasks import async_task
from django.db import transaction


class SignupView(generic.CreateView):
    template_name = "accounts/signup.html"
    form_class = SignupForm
    success_url = reverse_lazy("accounts:signup")

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

        return render(self.request, "accounts/email_verification_sent.html")

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)

class VerifyEmailView(generic.View):
    def get(self, request, uidb64, token):
        success, _ = verify_email(uidb64, token)

        template = (
            "accounts/email_verified.html"
            if success
            else "accounts/email_verification_failed.html"
        )

        return render(request, template)
