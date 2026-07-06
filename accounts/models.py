from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from zoneinfo import available_timezones

TIMEZONE_CHOICES = sorted(
    (tz, tz) for tz in available_timezones()
)

class User(AbstractUser):
    username = models.CharField(max_length=150, blank=True)
    email = models.EmailField(_("email"), unique=True)
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)
    is_email_verified = models.BooleanField(default=False, verbose_name="Email Verification Status",)

    reminder_email_notifier = models.BooleanField(default=True, verbose_name="Remind by Emails Status")
    
    reminder_lead_time = models.PositiveIntegerField(default=3)

    timezone = models.CharField(
        max_length=64,
        choices=TIMEZONE_CHOICES,
        default="UTC",
    )

    # Export preferences
    export_format = models.CharField(
        max_length=10,
        choices=[
            ("csv", "CSV"),
            ("xlsx", "Excel"),
            ("json", "JSON"),
            ("pdf", "PDF"),
        ],
        default="csv",
    )

    # Data management
    auto_delete_exports = models.BooleanField(default=False)
    retain_export_days = models.PositiveIntegerField(default=30)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

