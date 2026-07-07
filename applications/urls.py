from django.urls import path
from .views import (
    ApplicationListView,
    ApplicationCreateView,
    ApplicationDeleteView,
    ApplicationUpdateView,
    ApplicationDetailView
)

app_name = "applications"

urlpatterns = [
    path("", ApplicationListView.as_view(), name="application-list"),
    path("create/", ApplicationCreateView.as_view(), name="application-create"),
    path("delete/<int:pk>/", ApplicationDeleteView.as_view(), name="application-delete"),
    path("detail/<int:pk>/", ApplicationDetailView.as_view(), name="application-detail"),
    path("update/<int:pk>/", ApplicationUpdateView.as_view(), name="application-update"),
]