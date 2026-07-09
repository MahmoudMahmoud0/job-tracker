from django.urls import path
from .views import (
    InterviewListView,
    InterviewCreateView,
    InterviewDetailView,
    InterviewUpdateView,
    InterviewDeleteView
)
app_name = "interviews"

urlpatterns = [
    path("", InterviewListView.as_view(), name="interview-list"),
    path("create/", InterviewCreateView.as_view(), name="interview-create"),
    path("detail/<int:pk>/", InterviewDetailView.as_view(), name="interview-detail"),
    path("update/<int:pk>/", InterviewUpdateView.as_view(), name="interview-update"),
    path("delete/<int:pk>/", InterviewDeleteView.as_view(), name="interview-delete"),
]