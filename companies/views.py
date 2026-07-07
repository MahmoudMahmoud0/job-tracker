from django.urls import reverse_lazy
from django.views import generic
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Company
from .forms import CompanyForm

class CompanyListView(LoginRequiredMixin, generic.ListView):
    model = Company
    context_object_name = "companies"
    template_name = "companies/company_list.html"
    paginate_by = 20

    def get_queryset(self):
        return self.request.user.companies.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = context.get("paginator")
        page_obj = context.get("page_obj")

        if paginator and page_obj:
            context["page_range"] = paginator.get_elided_page_range(page_obj.number)

        return context

class CompanyCreateView(LoginRequiredMixin, generic.CreateView):
    model = Company
    form_class = CompanyForm
    template_name = "companies/company_create.html"
    success_url = reverse_lazy("companies:company-list")

    def form_valid(self, form):
        company = form.save(commit=False)
        company.owner = self.request.user
        company.save()
        return super().form_valid(form)

class CompanyDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Company
    template_name = "companies/company_delete.html"
    success_url = reverse_lazy("companies:company-list")
    
    def get_queryset(self):
        return self.request.user.companies.all()

class CompanyDetailView(LoginRequiredMixin, generic.DetailView):
    context_object_name = "company"
    template_name = "companies/company_detail.html"

    def get_queryset(self):
        return self.request.user.companies.all()

class CompanyUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Company
    form_class = CompanyForm
    context_object_name = "company"
    template_name = "companies/company_update.html"
    
    def get_queryset(self):
        return self.request.user.companies.filter(owner=self.request.user)
    
    def get_success_url(self):
        return reverse_lazy("companies:company-detail", kwargs={"pk": self.object.pk},)
    
    # def form_valid(self, form):
    #     comapy = form.save(commit=False)
    #     comapy.updated_at = timezone.now()
    #     comapy.save()
    #     return super().form_valid(form)
