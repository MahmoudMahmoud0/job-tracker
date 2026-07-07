from django.urls import path
from .views import (
    CompanyListView,
    CompanyCreateView,
    CompanyDeleteView,
    CompanyUpdateView,
    CompanyDetailView
)

app_name = "companies"

urlpatterns = [
    path("", CompanyListView.as_view(), name="company-list"),
    path("create/", CompanyCreateView.as_view(), name="company-create"),
    path("delete/<int:pk>/", CompanyDeleteView.as_view(), name="company-delete"),
    path("detail/<int:pk>/", CompanyDetailView.as_view(), name="company-detail"),
    path("update/<int:pk>/", CompanyUpdateView.as_view(), name="company-update"),
]