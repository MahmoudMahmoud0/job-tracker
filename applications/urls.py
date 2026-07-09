from django.urls import path
from .views import (
    ApplicationIndexView,
    ApplicationCreateView,
    ApplicationDeleteView,
    ApplicationUpdateView,
    ApplicationDetailView,
    FollowUpCreateView,
    FollowUpUpdateView,
    FollowUpDeleteView,
)

app_name = "applications"

urlpatterns = [
    path("", ApplicationIndexView.as_view(), name="application-view"),
    path("create/", ApplicationCreateView.as_view(), name="application-create"),
    path("delete/<int:pk>/", ApplicationDeleteView.as_view(), name="application-delete"),
    path("detail/<int:pk>/", ApplicationDetailView.as_view(), name="application-detail"),
    path("update/<int:pk>/", ApplicationUpdateView.as_view(), name="application-update"),
    path("create/<int:pk>/followups/create", FollowUpCreateView.as_view(), name="followup-create"),
    path("detail/<int:pk>/followups/update/", FollowUpUpdateView.as_view(), name="followup-update"),
    path("detail/<int:pk>/followups/delete/", FollowUpDeleteView.as_view(), name="followup-delete"),
]
