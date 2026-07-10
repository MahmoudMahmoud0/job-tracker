from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from applications.models import Application, ApplicationStatusHistory, FollowUp
from interviews.models import Interview


ACTIVE_APPLICATION_STATUSES = [
    "wishlist",
    "applied",
    "interviewing",
    "offer",
]

class AnalyticsBaseView(LoginRequiredMixin):
    def get_base_applications_queryset(self):
        return self.request.user.applications.select_related("company")

    def get_active_applications_queryset(self):
        return self.get_base_applications_queryset().filter(archived=False)


class DashboardView(AnalyticsBaseView, generic.TemplateView):
    template_name = "dashboard/dashboard.html"

    def get_applications_summary(self):
        now = timezone.localtime(timezone.now())
        next_week = now + timedelta(days=7)
        active_applications = self.get_active_applications_queryset()

        total_applications = active_applications.count()
        applied_applications = active_applications.filter(status="applied").count()
        interviewing_applications = active_applications.filter(status="interviewing").count()
        offer_applications = active_applications.filter(status="offer").count()
        submitted_applications = active_applications.exclude(status="wishlist").count()
        reached_interview_stage = active_applications.filter(
            status__in=["interviewing", "offer"]
        ).count()

        upcoming_interviews_count = Interview.objects.filter(
            application__owner=self.request.user,
            application__archived=False,
            outcome="pending",
            scheduled_at__gte=now,
            scheduled_at__lte=next_week,
        ).count()
        overdue_followups_count = FollowUp.objects.filter(
            application__owner=self.request.user,
            application__archived=False,
            application__status__in=ACTIVE_APPLICATION_STATUSES,
            completed=False,
            due_at__lt=now,
        ).count()

        return {
            "total_applications": total_applications,
            "active_applications": active_applications.exclude(
                status__in=["rejected", "withdrawn"]
            ).count(),
            "upcoming_interviews_count": upcoming_interviews_count,
            "overdue_followups_count": overdue_followups_count,
            "applied_applications": applied_applications,
            "submitted_applications": submitted_applications,
            "interviewing_applications": interviewing_applications,
            "offer_applications": offer_applications,
            "interview_rate": round(
                (reached_interview_stage / submitted_applications) * 100, 1
            )
            if submitted_applications
            else 0,
            "offer_rate": round((offer_applications / submitted_applications) * 100, 1)
            if submitted_applications
            else 0,
        }

    def get_pipeline_overview(self):
        overview = self.get_active_applications_queryset().aggregate(
            wishlist=Count("id", filter=Q(status="wishlist")),
            applied=Count("id", filter=Q(status="applied")),
            interviewing=Count("id", filter=Q(status="interviewing")),
            offer=Count("id", filter=Q(status="offer")),
            rejected=Count("id", filter=Q(status="rejected")),
            withdrawn=Count("id", filter=Q(status="withdrawn")),
        )

        total = sum(overview.values()) or 1
        items = []
        for value, label in Application.STATUS_CHOICES:
            count = overview.get(value, 0)
            items.append(
                {
                    "value": value,
                    "label": label,
                    "count": count,
                    "percentage": round((count / total) * 100, 1),
                }
            )

        return items

    def get_upcoming_attention(self):
        now = timezone.localtime(timezone.now())
        next_week = now + timedelta(days=7)

        upcoming_interviews = list(
            Interview.objects.filter(
                application__owner=self.request.user,
                application__archived=False,
                outcome="pending",
                scheduled_at__gte=now,
                scheduled_at__lte=next_week,
            )
            .select_related("application", "application__company")
            .order_by("scheduled_at")[:5]
        )

        overdue_followups = list(
            FollowUp.objects.filter(
                application__owner=self.request.user,
                application__archived=False,
                application__status__in=ACTIVE_APPLICATION_STATUSES,
                completed=False,
                due_at__lt=now,
            )
            .select_related("application", "application__company")
            .order_by("due_at")[:5]
        )

        return {
            "upcoming_interviews": upcoming_interviews,
            "overdue_followups": overdue_followups,
        }

    def get_weekly_trends(self):
        today = timezone.localdate()
        current_week_start = today - timedelta(days=today.weekday())
        first_week_start = current_week_start - timedelta(weeks=7)

        applied_dates = (
            self.get_active_applications_queryset()
            .filter(applied_at__isnull=False, applied_at__gte=first_week_start)
            .values_list("applied_at", flat=True)
        )

        counts_by_week = {}
        for applied_date in applied_dates:
            week_start = applied_date - timedelta(days=applied_date.weekday())
            counts_by_week[week_start] = counts_by_week.get(week_start, 0) + 1

        trend = []
        max_count = max(counts_by_week.values(), default=0)

        for index in range(8):
            week_start = first_week_start + timedelta(weeks=index)
            count = counts_by_week.get(week_start, 0)
            trend.append(
                {
                    "week_start": week_start,
                    "label": week_start.strftime("%b %d"),
                    "count": count,
                    "bar_height": max(14, round((count / max_count) * 100))
                    if max_count
                    else 14,
                }
            )
        return trend

    def get_recent_activity(self):
        activities = []

        for application in self.get_active_applications_queryset().order_by("-created_at")[:6]:
            activities.append(
                {
                    "title": f"Added {application.title}",
                    "description": f"{application.company.name} was added to your workspace.",
                    "timestamp": application.created_at,
                    "url": reverse("applications:application-detail", args=[application.pk]),
                    "tag": "Application",
                }
            )

        for history in (
            ApplicationStatusHistory.objects.filter(application__owner=self.request.user)
            .select_related("application", "application__company")
            .order_by("-changed_at")[:6]
        ):
            activities.append(
                {
                    "title": f"Moved to {history.get_status_display()}",
                    "description": (
                        f"{history.application.title} at "
                        f"{history.application.company.name}"
                    ),
                    "timestamp": history.changed_at,
                    "url": reverse(
                        "applications:application-detail",
                        args=[history.application.pk],
                    ),
                    "tag": "Status",
                }
            )

        for interview in (
            Interview.objects.filter(
                application__owner=self.request.user,
                scheduled_at__isnull=False,
            )
            .select_related("application", "application__company")
            .order_by("-scheduled_at")[:6]
        ):
            activities.append(
                {
                    "title": "Interview scheduled",
                    "description": (
                        f"{interview.application.title} at "
                        f"{interview.application.company.name}"
                    ),
                    "timestamp": interview.scheduled_at,
                    "url": reverse("interviews:interview-detail", args=[interview.pk]),
                    "tag": "Interview",
                }
            )

        for followup in (
            FollowUp.objects.filter(application__owner=self.request.user)
            .select_related("application", "application__company")
            .order_by("-created_at")[:6]
        ):
            activities.append(
                {
                    "title": f"Follow-up added: {followup.title}",
                    "description": (
                        f"{followup.application.title} at "
                        f"{followup.application.company.name}"
                    ),
                    "timestamp": followup.created_at,
                    "url": reverse(
                        "applications:application-detail",
                        args=[followup.application.pk],
                    ),
                    "tag": "Follow-up",
                }
            )

        activities.sort(key=lambda item: item["timestamp"], reverse=True)
        return activities[:10]

    def get_opportunity_sources(self):
        source_labels = dict(Application.SOURCE_CHOICES)
        active_applications = self.get_active_applications_queryset()
        total_sources = active_applications.exclude(source="").count() or 1

        sources = (
            active_applications.exclude(source="")
            .values("source")
            .annotate(count=Count("id"))
            .order_by("-count", "source")[:5]
        )

        return [
            {
                "value": item["source"],
                "label": source_labels.get(item["source"], item["source"]),
                "count": item["count"],
                "percentage": round((item["count"] / total_sources) * 100, 1),
            }
            for item in sources
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        summary = self.get_applications_summary()
        attention = self.get_upcoming_attention()

        context.update(
            {
                "page_kicker": "Workspace Overview",
                "page_title": "See what needs attention before your next move.",
                "page_description": (
                    "Track application momentum, upcoming interviews, overdue "
                    "follow-ups, and the sources that are actually producing results."
                ),
                "summary": summary,
                "pipeline_overview": self.get_pipeline_overview(),
                "weekly_trends": self.get_weekly_trends(),
                "recent_activity": self.get_recent_activity(),
                "opportunity_sources": self.get_opportunity_sources(),
                "upcoming_interviews": attention["upcoming_interviews"],
                "overdue_followups": attention["overdue_followups"],
                "has_dashboard_data": summary["total_applications"] > 0,
            }
        )
        return context

