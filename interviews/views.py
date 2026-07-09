from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic

from .forms import InterviewForm
from .models import Interview


class InterviewNavigationMixin:
    def get_return_url(self, fallback):
        return self.request.POST.get("next") or self.request.GET.get("next") or fallback


class InterviewQuerysetMixin:
    def get_queryset(self):
        queryset = Interview.objects.filter(
            application__owner=self.request.user
        ).select_related("application", "application__company")
        return queryset


class InterviewListView(LoginRequiredMixin, InterviewQuerysetMixin, generic.ListView):
    model = Interview
    template_name = "interviews/interview_list.html"
    context_object_name = "interviews"


class InterviewCreateView(LoginRequiredMixin, InterviewNavigationMixin, generic.CreateView):
    model = Interview
    form_class = InterviewForm
    template_name = "interviews/interview_create.html"
    success_url = reverse_lazy("interviews:interview-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = self.get_return_url(reverse_lazy("interviews:interview-list"))
        return context

    def form_valid(self, form):
        application = form.cleaned_data["application"]
        if application.status != "interviewing":
            application.status = "interviewing"
            application.save()
        return super().form_valid(form)


class InterviewDetailView(LoginRequiredMixin, InterviewQuerysetMixin, generic.DetailView):
    model = Interview
    template_name = "interviews/interview_detail.html"
    context_object_name = "interview"


class InterviewUpdateView(
    LoginRequiredMixin,
    InterviewNavigationMixin,
    InterviewQuerysetMixin,
    generic.UpdateView,
):
    model = Interview
    form_class = InterviewForm
    template_name = "interviews/interview_update.html"
    context_object_name = "interview"

    def get_success_url(self):
        return reverse_lazy("interviews:interview-detail", kwargs={"pk": self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = self.get_return_url(
            reverse_lazy("interviews:interview-detail", kwargs={"pk": self.object.pk})
        )
        return context


class InterviewDeleteView(
    LoginRequiredMixin,
    InterviewNavigationMixin,
    InterviewQuerysetMixin,
    generic.DeleteView,
):
    model = Interview
    template_name = "interviews/interview_delete.html"
    context_object_name = "interview"

    def get_success_url(self):
        return reverse_lazy("interviews:interview-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = self.get_return_url(
            reverse_lazy("interviews:interview-detail", kwargs={"pk": self.object.pk})
        )
        return context
