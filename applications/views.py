from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.utils.dateparse import parse_date
from .models import Application
from .forms import ApplicationForm
from .mixins import ApplicationCompanyMixin, ApplicationTagBuilderMixin

class ApplicationListView(LoginRequiredMixin, generic.ListView):
    model = Application
    context_object_name = "applications"
    template_name = "applications/application_list.html"
    paginate_by = 20
    SORT_OPTIONS = [
        ("newest", "Newest created"),
        ("oldest", "Oldest created"),
        ("applied_newest", "Newest applied date"),
        ("applied_oldest", "Oldest applied date"),
        ("title", "Role title"),
        ("company", "Company"),
        ("salary_high", "Highest salary"),
        ("salary_low", "Lowest salary"),
    ]

    def get_current_filters(self):
        return {
            "q": self.request.GET.get("q", ""),
            "company": self.request.GET.get("company", ""),
            "status": self.request.GET.get("status", ""),
            "source": self.request.GET.get("source", ""),
            "tag": self.request.GET.get("tag", ""),
            "date_from": self.request.GET.get("date_from", ""),
            "date_to": self.request.GET.get("date_to", ""),
            "archived": self.request.GET.get("archived", ""),
            "sort": self.request.GET.get("sort", "newest"),
        }

    def build_query_string(self, **updates):
        query_params = self.request.GET.copy()
        query_params.pop("page", None)

        for key, value in updates.items():
            if value in (None, ""):
                query_params.pop(key, None)
            else:
                query_params[key] = value

        return query_params.urlencode()

    def get_quick_filters(self):
        return [
            {
                "label": "Active",
                "active": self.request.GET.get("archived", "") != "true",
                "query_string": self.build_query_string(archived="", page=None),
            },
            {
                "label": "Archived",
                "active": self.request.GET.get("archived") == "true",
                "query_string": self.build_query_string(archived="true", page=None),
            },
            {
                "label": "Applied",
                "active": self.request.GET.get("status") == "applied",
                "query_string": self.build_query_string(status="applied", page=None),
            },
            {
                "label": "Interviewing",
                "active": self.request.GET.get("status") == "interviewing",
                "query_string": self.build_query_string(status="interviewing", page=None),
            },
            {
                "label": "Offers",
                "active": self.request.GET.get("status") == "offer",
                "query_string": self.build_query_string(status="offer", page=None),
            },
        ]

    def get_active_filter_chips(self, current_filters):
        chips = []

        status_map = dict(Application.STATUS_CHOICES)
        source_map = dict(Application.SOURCE_CHOICES)
        sort_map = dict(self.SORT_OPTIONS)
        company_map = {str(company.pk): company.name for company in self.request.user.companies.all()}
        tag_map = {str(tag.pk): tag.name for tag in self.request.user.tags.all()}

        if current_filters["q"]:
            chips.append({
                "label": f'Search: {current_filters["q"]}',
                "remove_url": f'?{self.build_query_string(q="", page=None)}',
            })
        if current_filters["company"]:
            chips.append({
                "label": f'Company: {company_map.get(current_filters["company"], "Selected")}',
                "remove_url": f'?{self.build_query_string(company="", page=None)}',
            })
        if current_filters["status"]:
            chips.append({
                "label": f'Status: {status_map.get(current_filters["status"], current_filters["status"])}',
                "remove_url": f'?{self.build_query_string(status="", page=None)}',
            })
        if current_filters["source"]:
            chips.append({
                "label": f'Source: {source_map.get(current_filters["source"], current_filters["source"])}',
                "remove_url": f'?{self.build_query_string(source="", page=None)}',
            })
        if current_filters["tag"]:
            chips.append({
                "label": f'Tag: {tag_map.get(current_filters["tag"], "Selected")}',
                "remove_url": f'?{self.build_query_string(tag="", page=None)}',
            })
        if current_filters["date_from"]:
            chips.append({
                "label": f'Applied from: {current_filters["date_from"]}',
                "remove_url": f'?{self.build_query_string(date_from="", page=None)}',
            })
        if current_filters["date_to"]:
            chips.append({
                "label": f'Applied to: {current_filters["date_to"]}',
                "remove_url": f'?{self.build_query_string(date_to="", page=None)}',
            })
        if current_filters["archived"] == "true":
            chips.append({
                "label": "Archived only",
                "remove_url": f'?{self.build_query_string(archived="", page=None)}',
            })
        if current_filters["sort"] != "newest":
            chips.append({
                "label": f'Sort: {sort_map.get(current_filters["sort"], current_filters["sort"])}',
                "remove_url": f'?{self.build_query_string(sort="newest", page=None)}',
            })

        return chips

    def get_queryset(self):
        queryset = (
            self.request.user.applications
            .select_related("company")
            .prefetch_related("tags")
        )

        company = self.request.GET.get("company")
        status = self.request.GET.get("status")
        source = self.request.GET.get("source")
        tag = self.request.GET.get("tag")
        archived = self.request.GET.get("archived")
        search = self.request.GET.get("q")
        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")
        sort = self.request.GET.get("sort")

        if company:
            queryset = queryset.filter(company_id=company)

        if status:
            queryset = queryset.filter(status=status)

        if source:
            queryset = queryset.filter(source=source)

        if tag:
            queryset = queryset.filter(tags__id=tag)

        if archived == "true":
            queryset = queryset.filter(archived=True)
        else:
            queryset = queryset.filter(archived=False)

        if search:
            queryset = queryset.filter(
                models.Q(title__icontains=search) |
                models.Q(company__name__icontains=search) |
                models.Q(department__icontains=search)
            )

        date_from_parsed = parse_date(date_from) if date_from else None
        date_to_parsed = parse_date(date_to) if date_to else None
        if date_from_parsed:
            queryset = queryset.filter(applied_at__gte=date_from_parsed)

        if date_to_parsed:
            queryset = queryset.filter(applied_at__lte=date_to_parsed)

        allowed_sorts = dict(self.SORT_OPTIONS)

        return queryset.order_by(
            allowed_sorts.get(sort, "-created_at")
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = context.get("paginator")
        page_obj = context.get("page_obj")
        query_params = self.request.GET.copy()
        query_params.pop("page", None)
        current_filters = self.get_current_filters()
        active_filter_chips = self.get_active_filter_chips(current_filters)

        if paginator and page_obj:
            context["page_range"] = paginator.get_elided_page_range(page_obj.number)

        context["companies"] = self.request.user.companies.all()
        context["status_choices"] = Application.STATUS_CHOICES
        context["source_choices"] = Application.SOURCE_CHOICES
        context["tags"] = self.request.user.tags.all()
        context["current_filters"] = current_filters
        context["sort_options"] = self.SORT_OPTIONS
        context["current_sort_label"] = dict(self.SORT_OPTIONS).get(current_filters["sort"], "Newest created")
        context["quick_filters"] = self.get_quick_filters()
        context["active_filter_chips"] = active_filter_chips
        context["has_active_filters"] = bool(active_filter_chips)
        context["query_string"] = query_params.urlencode()
        return context

class ApplicationCreateView(ApplicationCompanyMixin, ApplicationTagBuilderMixin, LoginRequiredMixin, generic.CreateView):
    model = Application
    form_class = ApplicationForm
    template_name = "applications/application_create.html"
    success_url = reverse_lazy("applications:application-list")

    def get_form(self, form_class=None):
        form_class = self.get_form_class() if form_class is None else form_class
        form = form_class(**self.get_form_kwargs(), owner=self.request.user)
        form.fields.pop("archived", None)
        if "company" in form.fields:
            form.fields["company"].queryset = self.request.user.companies.all()
        return form

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.company = self.resolve_company(form)
        response = super().form_valid(form)
        self.attach_new_tags(self.object)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context.get("form")
        new_tag_rows = self.get_new_tag_rows()
        context["new_tag_rows"] = new_tag_rows
        context["existing_tag_picker"] = self.get_existing_tag_picker_context(form)
        context["show_quick_company"] = self.should_show_quick_company(form)
        context["show_new_tags"] = self.should_show_new_tags(new_tag_rows)
        return context
    
class ApplicationDetailView(LoginRequiredMixin, generic.DetailView):
    context_object_name = "application"
    template_name = "applications/application_detail.html"

    def get_queryset(self):
        return (
            self.request.user.applications
            .select_related("company")
            .prefetch_related("tags", "status_history")
        )

class ApplicationUpdateView(ApplicationCompanyMixin, ApplicationTagBuilderMixin, LoginRequiredMixin, generic.UpdateView):
    model = Application
    form_class = ApplicationForm
    context_object_name = "application"
    template_name = "applications/application_update.html"

    def get_success_url(self):
        return reverse_lazy("applications:application-detail", kwargs={"pk": self.object.id})

    def get_queryset(self):
        return self.request.user.applications.filter(owner=self.request.user)

    def get_form(self, form_class=None):
        form_class = self.get_form_class() if form_class is None else form_class
        form = form_class(**self.get_form_kwargs(), owner=self.request.user)
        if "company" in form.fields:
            form.fields["company"].queryset = self.request.user.companies.all()
        return form

    def form_valid(self, form):
        form.instance.company = self.resolve_company(form)
        response = super().form_valid(form)
        self.attach_new_tags(self.object)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context.get("form")
        new_tag_rows = self.get_new_tag_rows()
        context["new_tag_rows"] = new_tag_rows
        context["existing_tag_picker"] = self.get_existing_tag_picker_context(form)
        context["show_quick_company"] = self.should_show_quick_company(form)
        context["show_new_tags"] = self.should_show_new_tags(new_tag_rows)
        return context

class ApplicationDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Application
    context_object_name = "application"
    template_name = "applications/application_delete.html"
    success_url = reverse_lazy("applications:application-list")
    
    def get_queryset(self):
        return self.request.user.applications.select_related("company").prefetch_related("tags")
