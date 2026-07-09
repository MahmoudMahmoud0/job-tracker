from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.utils.dateparse import parse_date
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import Application, SavedFilter, FollowUp
from .forms import ApplicationForm, FollowUpForm
from .mixins import ApplicationCompanyMixin, ApplicationTagBuilderMixin

class ApplicationBaseView(LoginRequiredMixin, generic.View):
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

    def get_valid_saved_filters(self, filters):
        valid_filters = {}
        company_ids = {str(pk) for pk in self.request.user.companies.values_list("pk", flat=True)}
        tag_ids = {str(pk) for pk in self.request.user.tags.values_list("pk", flat=True)}
        allowed_statuses = {value for value, _ in Application.STATUS_CHOICES}
        allowed_sources = {value for value, _ in Application.SOURCE_CHOICES}
        allowed_sorts = {value for value, _ in self.SORT_OPTIONS}

        q = filters.get("q", "").strip()
        if q:
            valid_filters["q"] = q

        company = filters.get("company", "").strip()
        if company in company_ids:
            valid_filters["company"] = company

        status = filters.get("status", "").strip()
        if status in allowed_statuses:
            valid_filters["status"] = status

        source = filters.get("source", "").strip()
        if source in allowed_sources:
            valid_filters["source"] = source

        tag = filters.get("tag", "").strip()
        if tag in tag_ids:
            valid_filters["tag"] = tag

        date_from = filters.get("date_from", "").strip()
        if date_from and parse_date(date_from):
            valid_filters["date_from"] = date_from

        date_to = filters.get("date_to", "").strip()
        if date_to and parse_date(date_to):
            valid_filters["date_to"] = date_to

        archived = filters.get("archived", "").strip()
        if archived == "true":
            valid_filters["archived"] = archived

        sort = filters.get("sort", "").strip()
        if sort and sort in allowed_sorts and sort != "newest":
            valid_filters["sort"] = sort

        return valid_filters

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
        current_filters = {
            k: v
            for k, v in self.get_current_filters().items()
            if v not in ("", "newest")
        }        
        saved_filters = []
        for saved_filter in self.request.user.saved_filters.all():
            saved_filters.append({
                "label": saved_filter.name,
                "active": saved_filter.filters == current_filters,
                "query_string": self.build_query_string(
                    **saved_filter.filters,
                    page=None,
                ),
                "is_saved": True
            })

        return saved_filters + [
            {
                "label": "Active",
                "active": self.request.GET.get("archived", "") != "true",
                "query_string": self.build_query_string(archived="", page=None),
                "is_saved": False
            },
            {
                "label": "Archived",
                "active": self.request.GET.get("archived") == "true",
                "query_string": self.build_query_string(archived="true", page=None),
                "is_saved": False
            },
            {
                "label": "Applied",
                "active": self.request.GET.get("status") == "applied",
                "query_string": self.build_query_string(status="applied", page=None),
                "is_saved": False
            },
            {
                "label": "Interviewing",
                "active": self.request.GET.get("status") == "interviewing",
                "query_string": self.build_query_string(status="interviewing", page=None),
                "is_saved": False
            },
            {
                "label": "Offers",
                "active": self.request.GET.get("status") == "offer",
                "query_string": self.build_query_string(status="offer", page=None),
                "is_saved": False
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

        allowed_sorts = {
            "newest": "-created_at",
            "oldest": "created_at",
            "applied_newest": "-applied_at",
            "applied_oldest": "applied_at",
            "title": "title",
            "company": "company__name",
            "salary_high": "-salary_max",
            "salary_low": "salary_min",
        }

        return queryset.order_by(
            allowed_sorts.get(sort, "-created_at")
        ).distinct()

    def get_view_mode(self):
        return "kanban" if self.request.GET.get("view") == "kanban" else "list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query_params = self.request.GET.copy()
        query_params.pop("page", None)
        current_filters = self.get_current_filters()
        active_filter_chips = self.get_active_filter_chips(current_filters)
        view_mode = self.get_view_mode()

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
        context["view_mode"] = view_mode
        context["is_kanban"] = view_mode == "kanban"
        context["page_kicker"] = "Application Board" if view_mode == "kanban" else "Application Workspace"
        context["page_title"] = (
            "See your pipeline by stage and move with more clarity."
            if view_mode == "kanban"
            else "Track every role with clear next-step context."
        )
        context["page_description"] = (
            "Scan every status column at once, keep filters intact, and update roles without losing the bigger picture of your search."
            if view_mode == "kanban"
            else "Keep your applications, stages, salary ranges, and notes in one place so your job search stays focused instead of fragmented."
        )
        return context

    def get_post_redirect(self):
        return redirect(self.request.get_full_path())

    def post(self, request, *args, **kwargs):
        if request.POST.get("action") == "save_filter":
            name = " ".join(request.POST.get("name", "").split())

            if name:
                max_length = SavedFilter._meta.get_field("name").max_length
                if len(name) > max_length:
                    messages.error(request, f"Filter name must be {max_length} characters or fewer.")
                    return redirect(request.get_full_path())

                filters = self.get_valid_saved_filters(self.get_current_filters())

                SavedFilter.objects.update_or_create(
                    owner=request.user,
                    name=name,
                    defaults={
                        "filters": filters,
                    },
                )
                messages.success(request, "Filter saved.")
            return self.get_post_redirect()

        if request.POST.get("action") == "delete_filter":
            filter_name = request.POST.get("filter_name", "").strip()
            deleted, _ = request.user.saved_filters.filter(name=filter_name).delete()

            if deleted:
                messages.success(request, "Filter deleted.")
            else:
                messages.error(request, "Saved filter not found.")

            return self.get_post_redirect()

        if request.POST.get("action") == "update_status":
            application_id = request.POST.get("application_id", "").strip()
            application = request.user.applications.filter(pk=application_id).first()
            if not application:
                messages.error(request, "Application not found.")
                return redirect(request.get_full_path())
            
            status = request.POST.get("status", "").strip()
            allowed_statuses = {value for value, _ in Application.STATUS_CHOICES}
            if status not in allowed_statuses:
                messages.error(request, "Invalid status.")
                return redirect(request.get_full_path())

            if application.status != status:
                application.status = status
                application.save()
                messages.success(request, "Status updated.")
            
        return self.get_post_redirect()


class ApplicationIndexView(generic.View):
    def dispatch(self, request, *args, **kwargs):
        if request.GET.get("view") == "kanban":
            return ApplicationKanbanView.as_view()(request, *args, **kwargs)

        return ApplicationListView.as_view()(request, *args, **kwargs)


class ApplicationListView(ApplicationBaseView, generic.ListView):
    model = Application
    context_object_name = "applications"
    template_name = "applications/application_list.html"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = context.get("paginator")
        page_obj = context.get("page_obj")

        if paginator and page_obj:
            context["page_range"] = paginator.get_elided_page_range(page_obj.number)

        return context
    

class ApplicationKanbanView(ApplicationBaseView, generic.ListView):
    model = Application
    context_object_name = "applications"
    template_name = "applications/application_kanban.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        applications = context["applications"]

        context["kanban_columns"] = [
            {
                "value": value,
                "label": label,
                "applications": applications.filter(status=value),
            }
            for value, label in Application.STATUS_CHOICES
        ]

        return context


class ApplicationCreateView(ApplicationCompanyMixin, ApplicationTagBuilderMixin, LoginRequiredMixin, generic.CreateView):
    model = Application
    form_class = ApplicationForm
    template_name = "applications/application_create.html"
    success_url = reverse_lazy("applications:application-view")

    def get_form(self, form_class=None):
        form_class = self.get_form_class() if form_class is None else form_class
        form = form_class(**self.get_form_kwargs(), owner=self.request.user)
        form.fields.pop("archived", None)
        if "company" in form.fields:
            form.fields["company"].queryset = self.request.user.companies.all()
        return form

    def form_valid(self, form):
        company = self.resolve_company(form)
        title = form.cleaned_data["title"]
        duplicate = Application.objects.filter(
            owner=self.request.user,
            company=company,
            title__iexact=title,
        ).exists()

        form.instance.owner = self.request.user
        form.instance.company = company

        status = form.cleaned_data.get("status")
        applied_date = form.cleaned_data.get("applied_at")

        if applied_date and status == "wishlist":
            form.instance.status = "applied"

        response = super().form_valid(form)
        self.attach_new_tags(self.object)

        if duplicate:
            messages.warning(
                self.request,
                "You already have another application for this role at this company."
            )

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
            .prefetch_related("tags", "status_history", "follow_ups")
        )
    
    def post(self, request, *args, **kwargs):
        if request.POST.get("action") == "switch_followup_status":
            application = self.get_object()
            follow_up_id = request.POST.get("follow_up_id", "").strip()
            follow_up = application.follow_ups.filter(pk=follow_up_id).first()

            if not follow_up:
                messages.error(request, "Follow-up not found.")
                return redirect("applications:application-detail", pk=application.pk)

            follow_up.completed = not follow_up.completed
            follow_up.completed_at = timezone.now() if follow_up.completed else None
            follow_up.save(update_fields=["completed", "completed_at", "updated_at"])

            if follow_up.completed:
                messages.success(request, "Follow-up marked as completed.")
            else:
                messages.success(request, "Follow-up marked as pending.")

            return redirect("applications:application-detail", pk=application.pk)

        return redirect("applications:application-detail", pk=self.get_object().pk)

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
    success_url = reverse_lazy("applications:application-view")
    
    def get_queryset(self):
        return self.request.user.applications.select_related("company").prefetch_related("tags")

class FollowUpCreateView(LoginRequiredMixin, generic.CreateView):
    model = FollowUp
    template_name = "followups/followup_create.html"
    form_class = FollowUpForm

    def get_application(self):
        return get_object_or_404(
            Application,
            pk=self.kwargs["pk"],
            owner=self.request.user,
        )

    def form_valid(self, form):
        application = self.get_application()
        form.instance.application = application
        messages.success(self.request, "Follow-up added.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.get_return_url()

    def get_return_url(self):
        next_url = self.request.GET.get("next", "").strip()
        if self.request.method == "POST":
            next_url = self.request.POST.get("next", "").strip()

        if next_url and url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        ):
            return next_url

        return reverse_lazy("applications:application-view")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["application"] = self.get_application()
        context["cancel_url"] = self.get_return_url()
        return context

class FollowUpUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = FollowUp
    form_class = FollowUpForm
    template_name = "followups/followup_update.html"

    def get_success_url(self):
        return reverse_lazy("applications:application-detail", kwargs={"pk": self.object.application.pk})
    
    def get_queryset(self):
        return FollowUp.objects.filter(application__owner=self.request.user).select_related("application", "application__company")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["application"] = self.object.application
        context["cancel_url"] = reverse_lazy("applications:application-detail", kwargs={"pk": self.object.application.pk})
        return context

class FollowUpDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = FollowUp
    context_object_name = "follow_up"
    template_name = "followups/followup_delete.html"

    def get_success_url(self):
        return reverse_lazy("applications:application-detail", kwargs={"pk": self.object.application.pk})
        
    def get_queryset(self):
        return FollowUp.objects.filter(application__owner=self.request.user).select_related("application", "application__company")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Follow-up deleted.")
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["application"] = self.object.application
        context["cancel_url"] = reverse_lazy("applications:application-detail", kwargs={"pk": self.object.application.pk})
        return context
