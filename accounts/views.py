from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views import generic

from .tokens import build_verification_url
from .forms import SignupForm
from .services import verify_email
from django.urls import reverse_lazy
from .emails import send_verification_email


class SignupView(generic.CreateView):
    template_name = "accounts/signup.html"
    form_class = SignupForm
    success_url = reverse_lazy("accounts:signup")

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.is_active = False
        self.object.save()

        # send confirmation email
        verification_url = build_verification_url(self.object, self.request)
        send_verification_email(self.object, verification_url)

        return HttpResponseRedirect(self.get_success_url())

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
