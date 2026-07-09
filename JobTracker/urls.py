from django.contrib import admin
from django.urls import path, include
from core.views import LandingPageView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LandingPageView.as_view(), name="landing"),
    path('accounts/', include("accounts.urls", namespace="accounts")),
    path('companies/', include("companies.urls", namespace="companies")),
    path('applications/', include("applications.urls", namespace="applications")),
    path('interviews/', include("interviews.urls", namespace="interviews")),
]
